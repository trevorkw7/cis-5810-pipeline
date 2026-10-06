"""Build colab_input.zip for the splatfacto Colab notebook.

Inputs: splat/colmap/ (transforms.json, sparse_pc.ply, plus the 62 high-orbit frames copied into images/ from
the dataset repo) and splat/low_orbit_camera_path.json.
Output zip: data/images, data/images_2 (half res), data/transforms.json, data/sparse_pc.ply (axis-fixed),
low_orbit_path.json (the 108 low-orbit render cameras).
The low-orbit test frames (IMG_4984) are never read or included.

Usage (from the repo root): python3 splat/prepare_input.py [--poses splat/colmap] [--path splat/low_orbit_camera_path.json] [--out colab_input.zip]
Needs numpy and pillow.
"""
import argparse, json, os, shutil, tempfile, zipfile
import numpy as np
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument("--poses", default="splat/colmap"); p.add_argument("--path", default="splat/low_orbit_camera_path.json")
p.add_argument("--out", default="colab_input.zip")
a = p.parse_args()
SRC = a.poses
work = tempfile.mkdtemp(); d = os.path.join(work, "data")
os.makedirs(f"{d}/images"); os.makedirs(f"{d}/images_2")

# 1. frames, full and half resolution (nerfstudio 1.1.5 picks images_2 automatically for 1920 px frames)
for f in sorted(os.listdir(f"{SRC}/images")):
    shutil.copy(f"{SRC}/images/{f}", f"{d}/images/{f}")
    im = Image.open(f"{SRC}/images/{f}")
    im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(f"{d}/images_2/{f}", quality=95)

# 2. poses; drop the converter's stale applied_transform so nerfstudio's dataparser_transforms.json
#    maps directly from this file's frame
tf = json.load(open(f"{SRC}/transforms.json"))
tf.pop("applied_transform", None)
json.dump(tf, open(f"{d}/transforms.json", "w"), indent=2)

# 3. point cloud: the shared ply uses COLMAP axes (x, z, -y) while the poses use (y, x, -z);
#    map (X', Y', Z') -> (-Z', X', -Y') so the points line up with the cameras
lines = open(f"{SRC}/sparse_pc.ply").read().splitlines()
n = int([l for l in lines if l.startswith("element vertex")][0].split()[-1])
hi = lines.index("end_header"); v = np.array([l.split() for l in lines[hi + 1:hi + 1 + n]], float)
pts = np.stack([-v[:, 2], v[:, 0], -v[:, 1]], 1)
def in_frame(P):
    fs = []
    for fr in tf["frames"]:
        w2c = np.linalg.inv(np.array(fr["transform_matrix"]) @ np.diag([1, -1, -1, 1]))
        X = P @ w2c[:3, :3].T + w2c[:3, 3]; z = X[:, 2]
        u = tf["fl_x"] * X[:, 0] / z + tf["cx"]; y = tf["fl_y"] * X[:, 1] / z + tf["cy"]
        fs.append(((z > 0) & (u >= 0) & (u < tf["w"]) & (y >= 0) & (y < tf["h"])).mean())
    return float(np.mean(fs))
print("points inside training frames: raw %.2f, fixed %.2f" % (in_frame(v[:, :3]), in_frame(pts)))
with open(f"{d}/sparse_pc.ply", "w") as f:
    f.write("ply\nformat ascii 1.0\nelement vertex %d\nproperty float x\nproperty float y\nproperty float z\n"
            "property uint8 red\nproperty uint8 green\nproperty uint8 blue\nend_header\n" % n)
    for q, c in zip(pts, v[:, 3:].astype(int)):
        f.write("%f %f %f %d %d %d\n" % (*q, *c))

# 4. low-orbit camera path: the 108 fixed render cameras (transforms.json frame, OpenGL axes)
path = json.load(open(a.path))["camera_path"]
shutil.copy(a.path, f"{work}/low_orbit_path.json")

# 5. zip
with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(f"{work}/low_orbit_path.json", "low_orbit_path.json")
    for sub in ("images", "images_2"):
        for f in sorted(os.listdir(f"{d}/{sub}")): z.write(f"{d}/{sub}/{f}", f"data/{sub}/{f}")
    z.write(f"{d}/transforms.json", "data/transforms.json"); z.write(f"{d}/sparse_pc.ply", "data/sparse_pc.ply")
shutil.rmtree(work)
print("wrote", a.out, "frames", len(tf["frames"]), "views", len(path))

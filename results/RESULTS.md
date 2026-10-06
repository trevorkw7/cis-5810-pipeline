# Results

| | [Real only (v1)](https://app.roboflow.com/new-workspace-9juoy/yolo-real-vs-synthetic-real/1) | [Real + synthetic (v3)](https://app.roboflow.com/new-workspace-9juoy/yolo-real-vs-synthetic-real/3) |
|---|---|---|
| Train images | 54 real | 54 real + 108 splat renders |
| Labels | SAM 3 | SAM 3 |
| Model | YOLOv11s, COCO-pretrained | YOLOv11s, COCO-pretrained |
| Image size | 640 (stretch) | 640 (stretch) |
| Epochs | 100 | 100 |
| Augmentation | none | none |
| Valid | 8 real high-angle | 8 real high-angle |
| Test | 85 blind low-angle | 85 blind low-angle |
| mAP50 | 56.5 | **98.7** |
| mAP50:95 | 28.0 | **92.1** |
| AP50 mug | 8.6 | 96.6 |
| AP50 bottle | 75.6 | 99.8 |
| AP50 BB-8 | 85.4 | 99.7 |
| Test set | [predictions](https://app.roboflow.com/new-workspace-9juoy/yolo-real-vs-synthetic-real/1/images?split=test&predictions=true) | [predictions](https://app.roboflow.com/new-workspace-9juoy/yolo-real-vs-synthetic-real/3/images?split=test&predictions=true) |

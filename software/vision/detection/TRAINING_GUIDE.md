# YOLOv8 Chinese Chess Detection - Training & Inference Guide

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Dataset Setup](#2-dataset-setup)
3. [Training](#3-training)
4. [Monitor Training Quality](#4-monitor-training-quality)
5. [Test on Images](#5-test-on-images)
6. [Test on Video / Camera](#6-test-on-video--camera)
7. [Quality Metrics Explained](#7-quality-metrics-explained)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prerequisites

```bash
cd /home/qbot/chinese_chess_bot_307
source .venv/bin/activate

# Verify packages
python -c "import ultralytics; print(ultralytics.__version__)"
python -c "import cv2; print(cv2.__version__)"
```

---

## 2. Dataset Setup

The dataset is from Roboflow (Chinese Chess v6) with **14 classes**:

| ID | Class | Vietnamese | ID | Class | Vietnamese |
|----|-------|------------|-----|-------|------------|
| 0 | b_advisor | Sĩ đen | 7 | r_advisor | Sĩ đỏ |
| 1 | b_cannon | Pháo đen | 8 | r_cannon | Pháo đỏ |
| 2 | b_chariot | Xe đen | 9 | r_chariot | Xe đỏ |
| 3 | b_elephant | Tượng đen | 10 | r_elephant | Tượng đỏ |
| 4 | b_general | Tướng đen | 11 | r_general | Tướng đỏ |
| 5 | b_horse | Mã đen | 12 | r_horse | Mã đỏ |
| 6 | b_soldier | Tốt đen | 13 | r_soldier | Tốt đỏ |

**Dataset structure:**
```
datasets/
├── data.yaml              ← Roboflow config (DO NOT use for training)
├── chinese_chess.yaml      ← Our config (USE THIS)
├── train/
│   ├── images/ (190 images)
│   └── labels/ (190 .txt files, YOLO format)
└── valid/
    ├── images/ (8 images)
    └── labels/ (8 .txt files)
```

**YOLO label format** (each `.txt` line):
```
class_id  center_x  center_y  width  height
# All values normalized 0-1
```

---

## 3. Training

```bash
cd software/vision/detection

# Standard training (yolov8n - fast, good for Raspberry Pi)
python train.py --data chinese_chess.yaml --model yolov8n.pt --epochs 100 --batch 16 --imgsz 640

# With GPU (if available)
python train.py --data chinese_chess.yaml --model yolov8n.pt --epochs 100 --batch 16 --device 0

# Higher accuracy (larger model, needs more compute)
python train.py --data chinese_chess.yaml --model yolov8s.pt --epochs 150 --batch 8 --imgsz 640
```

**Model size guide:**

| Model | Params | Size | Speed | Use case |
|-------|--------|------|-------|----------|
| yolov8n.pt | 3M | 6MB | ~45 FPS | Raspberry Pi / real-time |
| yolov8s.pt | 11M | 22MB | ~30 FPS | Balanced |
| yolov8m.pt | 26M | 50MB | ~15 FPS | Best accuracy on PC |

**Output after training:**
```
runs/detect/train/
├── weights/
│   ├── best.pt              ← Best model (USE THIS)
│   └── last.pt              ← Last checkpoint
├── results.csv              ← Epoch-by-epoch metrics
├── results.png              ← Loss & metrics plots (auto-generated)
├── confusion_matrix.png     ← Per-class accuracy matrix
├── labels.jpg               ← Dataset label distribution
├── val_batch0_pred.jpg       ← Prediction samples
└── val_batch0_labels.jpg     ← Ground truth samples
```

---

## 4. Monitor Training Quality

### 4.1 While Training (live)

```bash
# Watch metrics update in real-time
tail -f runs/detect/train/results.csv
```

### 4.2 After Training - Dashboard

```bash
cd software/vision/detection

# Print summary to console
python check_training.py --results ../../../runs/detect/train/results.csv

# Save dashboard as PNG image
python check_training.py --results ../../../runs/detect/train/results.csv --save
```

This generates **4 diagnostic charts**:

```
┌─────────────────────────────┬─────────────────────────────┐
│     Training Loss           │     Validation Loss         │
│  (should decrease ↓)        │  (should decrease ↓)        │
│                             │                             │
│  📉 box_loss                │  📉 val_box_loss            │
│  📉 cls_loss                │  📉 val_cls_loss            │
│  📉 dfl_loss                │  📉 val_dfl_loss            │
├─────────────────────────────┼─────────────────────────────┤
│     mAP                     │     Precision & Recall      │
│  (should increase ↑)        │  (should increase ↑)        │
│                             │                             │
│  📈 mAP@50                  │  📈 Precision               │
│  📈 mAP@50-95               │  📈 Recall                  │
└─────────────────────────────┴─────────────────────────────┘
```

### 4.3 Quality Assessment Criteria

| Metric | Poor | Acceptable | Good | Excellent |
|--------|------|------------|------|-----------|
| mAP@50 | <0.50 | 0.50-0.70 | 0.70-0.90 | >0.90 |
| mAP@50-95 | <0.30 | 0.30-0.50 | 0.50-0.70 | >0.70 |
| Precision | <0.60 | 0.60-0.80 | 0.80-0.90 | >0.90 |
| Recall | <0.60 | 0.60-0.80 | 0.80-0.90 | >0.90 |

### 4.4 Signs of Problems

| Problem | Symptom | Solution |
|---------|---------|----------|
| **Overfitting** | Train loss ↓ but Val loss ↑ | Add more training data, use augmentation |
| **Underfitting** | Both losses stay high | Train longer, use larger model (s→m) |
| **Bad labels** | mAP stays near 0 | Re-check label annotations |
| **Too few data** | Metrics oscillate wildly | Collect more images (aim 500+) |

---

## 5. Test on Images

```bash
cd software/vision/detection

# Test on a single image
python detect_realtime.py --model ../../../runs/detect/train/weights/best.pt --source path/to/image.jpg

# Test on a folder of images
python detect_realtime.py --model ../../../runs/detect/train/weights/best.pt --source path/to/test_folder/

# Adjust confidence threshold (lower = more detections, higher = fewer but more certain)
python detect_realtime.py --model ../../../runs/detect/train/weights/best.pt --source image.jpg --conf 0.3
```

**Controls:**
- Press any key → next image
- Press `q` → quit

---

## 6. Test on Video / Camera

```bash
cd software/vision/detection

# Live camera (camera 0)
python detect_realtime.py --model ../../../runs/detect/train/weights/best.pt --camera 0

# Different camera
python detect_realtime.py --model ../../../runs/detect/train/weights/best.pt --camera 1

# Lower confidence for more detections
python detect_realtime.py --model ../../../runs/detect/train/weights/best.pt --camera 0 --conf 0.15
```

**Controls:**
- Press `s` → save screenshot with detections
- Press `q` → quit
- Console prints detected pieces every 30 frames

---

## 7. Quality Metrics Explained

### Loss Functions (lower = better)

```
Training Flow:
                                    ┌──────────────┐
    Image ──► YOLOv8 ──► Predictions ──► Compare with ──► Loss
                                    │  Ground Truth │
                                    └──────┬───────┘
                                           │
                              ┌────────────┼────────────┐
                              ▼            ▼            ▼
                          Box Loss    Class Loss    DFL Loss
                          (vị trí)    (phân loại)   (phân bố)
```

- **Box Loss**: Sai số vị trí bounding box (IoU). Nếu cao = box lệch vị trí.
- **Class Loss**: Sai số phân loại quân cờ. Nếu cao = nhầm quân này thành quân khác.
- **DFL Loss**: Distribution Focal Loss. Hỗ trợ box regression chính xác hơn.

### Detection Metrics (higher = better)

```
                    ┌─────────────────────┐
                    │    All Predictions   │
                    └──────────┬──────────┘
                               │
               ┌───────────────┼───────────────┐
               ▼                               ▼
        ┌─────────────┐                 ┌─────────────┐
        │  Correct ✅  │                 │  Wrong ❌    │
        │ (True Pos)  │                 │ (False Pos) │
        └──────┬──────┘                 └─────────────┘
               │
    Precision = TP / (TP + FP)     "Trong số quân detect được, bao nhiêu đúng?"
    Recall    = TP / (TP + FN)     "Trong số quân thật có, bao nhiêu detect được?"
    mAP@50    = mean AP tại IoU≥0.50    "Chất lượng tổng thể (box chồng ≥50%)"
    mAP@50-95 = mean AP tại IoU 0.50→0.95  "Chất lượng nghiêm ngặt"
```

### Confusion Matrix

Auto-generated at `runs/detect/train/confusion_matrix.png`. Đọc:
- **Đường chéo chính** (diagonal) = phân loại đúng → càng đậm càng tốt
- **Ngoài đường chéo** = nhầm lẫn giữa các class → nên gần 0

---

## 8. Troubleshooting

### Training quá chậm (CPU)
```bash
# Giảm image size
python train.py --data chinese_chess.yaml --epochs 50 --imgsz 416 --batch 8

# Hoặc dùng Google Colab với GPU miễn phí
```

### mAP thấp sau training
1. Kiểm tra confusion matrix → xem class nào bị nhầm
2. Thêm ảnh cho class yếu
3. Tăng epochs (150-200)
4. Thử model lớn hơn (yolov8s.pt)

### Validate model đã train
```bash
python train.py --data chinese_chess.yaml --validate-only ../../../runs/detect/train/weights/best.pt
```

### Resume training bị gián đoạn
```bash
# Dùng lệnh yolo CLI trực tiếp
source ../../../.venv/bin/activate
yolo detect train resume model=../../../runs/detect/train/weights/last.pt
```

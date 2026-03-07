"""
STEP 3: Huấn luyện YOLOv8 (Training)

Cách dùng:
    python train.py --data chinese_chess.yaml --epochs 100 --batch 16 --imgsz 640
    
    Hoặc dùng model lớn hơn cho độ chính xác cao hơn:
    python train.py --data chinese_chess.yaml --model yolov8m.pt --epochs 150

Kết quả sau huấn luyện:
    runs/detect/train/
    ├── weights/
    │   ├── best.pt      ← Model tốt nhất (dùng cái này)
    │   └── last.pt      ← Model cuối cùng
    ├── results.png      ← Biểu đồ loss/metrics
    ├── confusion_matrix.png
    └── val_batch*.jpg   ← Ảnh validation mẫu
"""

from ultralytics import YOLO
import argparse
import os


def train_model(data_yaml: str, model_name: str, epochs: int,
                batch_size: int, img_size: int, device: str):
    """Huấn luyện YOLOv8 trên dataset cờ tướng."""

    # Load model pretrained (transfer learning)
    print(f"[INFO] Loading pretrained model: {model_name}")
    model = YOLO(model_name)

    # Bắt đầu huấn luyện
    print(f"[INFO] Training with:")
    print(f"  Dataset: {data_yaml}")
    print(f"  Epochs:  {epochs}")
    print(f"  Batch:   {batch_size}")
    print(f"  ImgSize: {img_size}")
    print(f"  Device:  {device}")

    metrics = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=img_size,
        device=device,
        patience=20,        # Early stopping nếu 20 epoch không cải thiện
        save=True,
        save_period=10,      # Lưu checkpoint mỗi 10 epoch
        plots=True,          # Tạo biểu đồ training
        verbose=True,
    )

    # save_dir nằm trên trainer, không phải trên metrics
    save_dir = model.trainer.save_dir
    print("\n[DONE] Huấn luyện xong!")
    print(f"  Best model: {save_dir}/weights/best.pt")
    return metrics, save_dir


def validate_model(model_path: str, data_yaml: str):
    """Đánh giá model trên tập validation."""
    print(f"\n[INFO] Validating model: {model_path}")
    model = YOLO(model_path)
    metrics = model.val(data=data_yaml, verbose=True)

    print(f"\n[RESULTS]")
    print(f"  mAP50:    {metrics.box.map50:.4f}")
    print(f"  mAP50-95: {metrics.box.map:.4f}")
    print(f"  Precision: {metrics.box.mp:.4f}")
    print(f"  Recall:    {metrics.box.mr:.4f}")
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Huấn luyện YOLOv8 nhận diện cờ tướng")
    parser.add_argument("--data", type=str, default="chinese_chess.yaml",
                        help="File cấu hình dataset (.yaml)")
    parser.add_argument("--model", type=str, default="yolov8n.pt",
                        help="Pretrained model (yolov8n/s/m/l/x.pt)")
    parser.add_argument("--epochs", type=int, default=100,
                        help="Số epoch huấn luyện")
    parser.add_argument("--batch", type=int, default=16,
                        help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640,
                        help="Kích thước ảnh đầu vào")
    parser.add_argument("--device", type=str, default="",
                        help="Device: '' (auto), 'cpu', '0' (GPU 0)")
    parser.add_argument("--validate-only", type=str, default=None,
                        help="Chỉ validate model (đường dẫn tới .pt)")
    args = parser.parse_args()

    if args.validate_only:
        validate_model(args.validate_only, args.data)
    else:
        metrics, save_dir = train_model(args.data, args.model, args.epochs,
                                        args.batch, args.imgsz, args.device)
        # Tự động validate sau khi train xong
        best_model = os.path.join(str(save_dir), "weights", "best.pt")
        if os.path.exists(best_model):
            validate_model(best_model, args.data)

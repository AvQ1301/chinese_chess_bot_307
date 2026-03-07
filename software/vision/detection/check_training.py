"""
Kiểm tra chất lượng huấn luyện YOLOv8 (Training Quality Check)
Vẽ biểu đồ loss, mAP, precision, recall từ file results.csv

Cách dùng:
    python check_training.py --results ../../../runs/detect/train/results.csv
    python check_training.py --results ../../../runs/detect/train/results.csv --save
"""

import argparse
import os
import csv
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend cho headless server
import matplotlib.pyplot as plt


def load_results(csv_path: str) -> dict:
    """Đọc file results.csv từ Ultralytics training."""
    data = {
        'epoch': [],
        'train/box_loss': [],
        'train/cls_loss': [],
        'train/dfl_loss': [],
        'metrics/precision(B)': [],
        'metrics/recall(B)': [],
        'metrics/mAP50(B)': [],
        'metrics/mAP50-95(B)': [],
        'val/box_loss': [],
        'val/cls_loss': [],
        'val/dfl_loss': [],
    }

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key in data:
                raw = row.get(key, '').strip()
                if raw:
                    data[key].append(float(raw))

    return data


def plot_training_quality(data: dict, save_dir: str = None):
    """Vẽ 4 biểu đồ đánh giá chất lượng training."""
    epochs = data['epoch']

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('YOLOv8 Training Quality Dashboard - Chinese Chess', fontsize=14, fontweight='bold')

    # --- 1. Training Loss ---
    ax1 = axes[0, 0]
    ax1.plot(epochs, data['train/box_loss'], label='Box Loss', color='#e74c3c')
    ax1.plot(epochs, data['train/cls_loss'], label='Class Loss', color='#3498db')
    ax1.plot(epochs, data['train/dfl_loss'], label='DFL Loss', color='#2ecc71')
    ax1.set_title('Training Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # --- 2. Validation Loss ---
    ax2 = axes[0, 1]
    ax2.plot(epochs, data['val/box_loss'], label='Val Box Loss', color='#e74c3c', linestyle='--')
    ax2.plot(epochs, data['val/cls_loss'], label='Val Class Loss', color='#3498db', linestyle='--')
    ax2.plot(epochs, data['val/dfl_loss'], label='Val DFL Loss', color='#2ecc71', linestyle='--')
    ax2.set_title('Validation Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # --- 3. mAP ---
    ax3 = axes[1, 0]
    ax3.plot(epochs, data['metrics/mAP50(B)'], label='mAP@50', color='#e67e22', linewidth=2)
    ax3.plot(epochs, data['metrics/mAP50-95(B)'], label='mAP@50-95', color='#9b59b6', linewidth=2)
    ax3.set_title('mAP (Mean Average Precision)')
    ax3.set_xlabel('Epoch')
    ax3.set_ylabel('mAP')
    ax3.set_ylim(0, 1)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, label='Baseline 50%')

    # --- 4. Precision & Recall ---
    ax4 = axes[1, 1]
    ax4.plot(epochs, data['metrics/precision(B)'], label='Precision', color='#1abc9c', linewidth=2)
    ax4.plot(epochs, data['metrics/recall(B)'], label='Recall', color='#e74c3c', linewidth=2)
    ax4.set_title('Precision & Recall')
    ax4.set_xlabel('Epoch')
    ax4.set_ylabel('Score')
    ax4.set_ylim(0, 1)
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_dir:
        save_path = os.path.join(save_dir, 'training_quality_dashboard.png')
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"[SAVED] Dashboard: {save_path}")

    # Also print summary
    print_summary(data)

    return fig


def print_summary(data: dict):
    """In tóm tắt kết quả huấn luyện."""
    n = len(data['epoch'])
    if n == 0:
        print("[WARN] Chưa có dữ liệu training.")
        return

    last_epoch = int(data['epoch'][-1])
    best_map50_idx = max(range(n), key=lambda i: data['metrics/mAP50(B)'][i])
    best_map50 = data['metrics/mAP50(B)'][best_map50_idx]
    best_map50_epoch = int(data['epoch'][best_map50_idx])

    best_map5095_idx = max(range(n), key=lambda i: data['metrics/mAP50-95(B)'][i])
    best_map5095 = data['metrics/mAP50-95(B)'][best_map5095_idx]

    print(f"\n{'='*55}")
    print(f"  TRAINING QUALITY SUMMARY")
    print(f"{'='*55}")
    print(f"  Total Epochs:       {last_epoch}")
    print(f"  Best mAP@50:        {best_map50:.4f}  (epoch {best_map50_epoch})")
    print(f"  Best mAP@50-95:     {best_map5095:.4f}")
    print(f"  Final Precision:    {data['metrics/precision(B)'][-1]:.4f}")
    print(f"  Final Recall:       {data['metrics/recall(B)'][-1]:.4f}")
    print(f"  Final Train Loss:   box={data['train/box_loss'][-1]:.4f}  "
          f"cls={data['train/cls_loss'][-1]:.4f}  "
          f"dfl={data['train/dfl_loss'][-1]:.4f}")
    print(f"  Final Val Loss:     box={data['val/box_loss'][-1]:.4f}  "
          f"cls={data['val/cls_loss'][-1]:.4f}  "
          f"dfl={data['val/dfl_loss'][-1]:.4f}")
    print(f"{'='*55}")

    # Quality assessment
    print(f"\n  QUALITY ASSESSMENT:")
    if best_map50 >= 0.9:
        print(f"  ✅ mAP@50 >= 0.90 → Excellent! Sẵn sàng deploy.")
    elif best_map50 >= 0.7:
        print(f"  ⚠️  mAP@50 >= 0.70 → Good. Có thể cải thiện thêm.")
    elif best_map50 >= 0.5:
        print(f"  ⚠️  mAP@50 >= 0.50 → Acceptable. Cần thêm data hoặc epochs.")
    else:
        print(f"  ❌ mAP@50 < 0.50 → Kém. Kiểm tra lại dataset/labels.")

    # Overfitting check
    if n >= 10:
        train_loss_end = data['train/box_loss'][-1]
        val_loss_end = data['val/box_loss'][-1]
        if val_loss_end > train_loss_end * 2:
            print(f"  ⚠️  Val loss >> Train loss → Có dấu hiệu overfitting!")
            print(f"       Khuyến nghị: thêm data, augmentation, hoặc giảm epochs.")
        else:
            print(f"  ✅ Không có dấu hiệu overfitting rõ ràng.")

    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kiểm tra chất lượng training YOLOv8")
    parser.add_argument("--results", type=str,
                        default="../../../runs/detect/train/results.csv",
                        help="Đường dẫn tới results.csv")
    parser.add_argument("--save", action="store_true",
                        help="Lưu biểu đồ thành file PNG")
    args = parser.parse_args()

    if not os.path.exists(args.results):
        print(f"[ERROR] Không tìm thấy: {args.results}")
        print("Training đang chạy hoặc chưa bắt đầu.")
        exit(1)

    data = load_results(args.results)

    save_dir = os.path.dirname(args.results) if args.save else None
    plot_training_quality(data, save_dir=save_dir)

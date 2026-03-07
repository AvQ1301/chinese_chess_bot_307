"""
STEP 2: Chuẩn bị dataset - Chia ảnh thành train/val/test
Sau khi label xong bằng LabelImg/CVAT, chạy script này để chia dataset.

Cách dùng:
    python prepare_dataset.py --source ../../../datasets/raw_labeled --output ../../../datasets
    
Cấu trúc đầu vào (sau khi label):
    raw_labeled/
    ├── image1.jpg
    ├── image1.txt    (YOLO format label)
    ├── image2.jpg
    ├── image2.txt
    └── ...

Cấu trúc đầu ra:
    datasets/
    ├── train/
    │   ├── images/
    │   └── labels/
    ├── val/
    │   ├── images/
    │   └── labels/
    └── test/
        ├── images/
        └── labels/
"""

import os
import shutil
import random
import argparse


def split_dataset(source_dir: str, output_dir: str,
                  train_ratio: float = 0.7,
                  val_ratio: float = 0.2,
                  test_ratio: float = 0.1):
    """Chia dataset thành train/val/test theo tỉ lệ."""

    # Tìm tất cả ảnh có file label tương ứng
    image_exts = {'.jpg', '.jpeg', '.png', '.bmp'}
    all_images = []
    for f in os.listdir(source_dir):
        name, ext = os.path.splitext(f)
        if ext.lower() in image_exts:
            label_file = os.path.join(source_dir, name + '.txt')
            if os.path.exists(label_file):
                all_images.append(name)
            else:
                print(f"  [WARN] Bỏ qua {f} - không có file label")

    if not all_images:
        print("[ERROR] Không tìm thấy cặp image+label nào!")
        return

    # Xáo trộn ngẫu nhiên
    random.shuffle(all_images)

    # Chia theo tỉ lệ
    n = len(all_images)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    splits = {
        'train': all_images[:n_train],
        'val': all_images[n_train:n_train + n_val],
        'test': all_images[n_train + n_val:]
    }

    # Copy files vào thư mục tương ứng
    for split_name, file_list in splits.items():
        img_dir = os.path.join(output_dir, split_name, 'images')
        lbl_dir = os.path.join(output_dir, split_name, 'labels')
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(lbl_dir, exist_ok=True)

        for name in file_list:
            # Tìm file ảnh gốc (có thể .jpg, .png, ...)
            for ext in image_exts:
                src_img = os.path.join(source_dir, name + ext)
                if os.path.exists(src_img):
                    shutil.copy2(src_img, os.path.join(img_dir, name + ext))
                    break

            src_lbl = os.path.join(source_dir, name + '.txt')
            shutil.copy2(src_lbl, os.path.join(lbl_dir, name + '.txt'))

        print(f"  {split_name}: {len(file_list)} ảnh")

    print(f"\n[DONE] Tổng cộng {n} ảnh đã chia xong!")
    print(f"  Train: {len(splits['train'])} | Val: {len(splits['val'])} | Test: {len(splits['test'])}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chia dataset train/val/test")
    parser.add_argument("--source", type=str, required=True,
                        help="Thư mục chứa ảnh + label đã gán nhãn")
    parser.add_argument("--output", type=str,
                        default="../../../datasets",
                        help="Thư mục đầu ra (mặc định: datasets/)")
    parser.add_argument("--train", type=float, default=0.7, help="Tỉ lệ train")
    parser.add_argument("--val", type=float, default=0.2, help="Tỉ lệ validation")
    parser.add_argument("--test", type=float, default=0.1, help="Tỉ lệ test")
    args = parser.parse_args()

    split_dataset(args.source, args.output, args.train, args.val, args.test)

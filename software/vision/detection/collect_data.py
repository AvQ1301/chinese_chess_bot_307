"""
STEP 1: Thu thập dữ liệu (Data Collection)
Chụp ảnh bàn cờ từ camera để tạo dataset huấn luyện YOLOv8.

Cách dùng:
    python collect_data.py --output ../../../datasets/raw_images --camera 0
    
Hướng dẫn:
    - Nhấn 's' để lưu ảnh
    - Nhấn 'q' để thoát
    - Nên chụp ~200-500 ảnh với nhiều điều kiện khác nhau:
      + Thay đổi ánh sáng (sáng, tối, bóng)
      + Thay đổi góc camera (nếu có)
      + Thay đổi vị trí quân cờ trên bàn
      + Một số ảnh có ít quân, nhiều quân, đủ quân
"""

import cv2
import os
import argparse
from datetime import datetime


def collect_images(output_dir: str, camera_id: int):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"[ERROR] Không mở được camera {camera_id}")
        return

    # Đặt độ phân giải cao nếu camera hỗ trợ
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    count = len([f for f in os.listdir(output_dir) if f.endswith(('.jpg', '.png'))])
    print(f"[INFO] Đã có {count} ảnh trong {output_dir}")
    print("[INFO] Nhấn 's' để chụp ảnh, 'q' để thoát")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Không đọc được frame từ camera")
            break

        # Hiển thị số ảnh đã chụp
        display = frame.copy()
        cv2.putText(display, f"Saved: {count} | Press 's' to save, 'q' to quit",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Data Collection - Chinese Chess", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"chess_{timestamp}.jpg"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, frame)
            count += 1
            print(f"  [SAVED] {filename} (Total: {count})")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[DONE] Tổng cộng {count} ảnh trong {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Thu thập ảnh bàn cờ tướng")
    parser.add_argument("--output", type=str,
                        default="../../../datasets/raw_images",
                        help="Thư mục lưu ảnh")
    parser.add_argument("--camera", type=int, default=0,
                        help="Camera ID (mặc định: 0)")
    args = parser.parse_args()
    collect_images(args.output, args.camera)

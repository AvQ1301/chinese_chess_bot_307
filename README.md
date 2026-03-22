# CCR3 - Chinese Chess Robot

Dự án robot chơi cờ tướng tích hợp xử lý hình ảnh (Vision) và trí tuệ nhân tạo (Pikafish Engine).

## Cấu trúc thư mục

- `docs/`: Tài liệu hướng dẫn và kiến trúc.
- `software/`: Mã nguồn Python điều khiển robot.
  - `common/`: Cấu hình và tiện ích dùng chung.
  - `vision/`: Nhận diện bàn cờ và quân cờ (YOLO).
  - `chess_engine/`: Giao thức kết nối với công cụ tính toán nước đi.
  - `control/`: Động học và điều khiển tay máy.
  - `integration/`: Tích hợp các module và vòng lặp chính.
- `firmware/`: Mã nguồn Arduino (C++/Ino).
- `datasets/`: Dữ liệu huấn luyện mô hình.

## Hướng dẫn cài đặt

1. Cài đặt Python 3.9+
2. Cài đặt dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Nạp firmware lên Arduino trong thư mục `firmware/src/`.
4. Chạy ứng dụng chính:
   ```bash
   python software/integration/main.py
   ```

"""
STEP 4: Nhận diện real-time từ camera (Inference)
Dùng model đã huấn luyện để nhận diện quân cờ trên video trực tiếp.

Cách dùng:
    python detect_realtime.py --model runs/detect/train/weights/best.pt --camera 0
    
    Hoặc test trên ảnh tĩnh:
    python detect_realtime.py --model best.pt --source path/to/image.jpg
    
    Hoặc test trên thư mục ảnh:
    python detect_realtime.py --model best.pt --source path/to/test_images/
"""

import cv2
import argparse
import os
import numpy as np
from ultralytics import YOLO


# 14 class cờ tướng - mỗi class một màu hiển thị
CLASS_COLORS = {
    'black_advisor':  (128, 128, 128),
    'black_cannon':   (100, 100, 100),
    'black_elephant': (80, 80, 80),
    'black_king':     (50, 50, 50),
    'black_knight':   (60, 60, 60),
    'black_pawn':     (90, 90, 90),
    'black_rook':     (70, 70, 70),
    'red_advisor':    (0, 0, 255),
    'red_cannon':     (0, 50, 200),
    'red_elephant':   (0, 100, 255),
    'red_king':       (0, 0, 200),
    'red_knight':     (50, 50, 255),
    'red_pawn':       (0, 80, 220),
    'red_rook':       (30, 30, 255),
}


def draw_detections(frame, results, conf_threshold: float = 0.25):
    """Vẽ bounding box và tên quân cờ lên frame."""
    detections = []
    result = results[0]

    if result.boxes is None:
        return frame, detections

    for box in result.boxes:
        conf = float(box.conf[0])
        if conf < conf_threshold:
            continue

        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        cls_id = int(box.cls[0])
        class_name = result.names[cls_id]

        # Tâm quân cờ
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        detections.append({
            'class': class_name,
            'confidence': conf,
            'bbox': (x1, y1, x2, y2),
            'center': (cx, cy),
        })

        # Vẽ bounding box
        color = CLASS_COLORS.get(class_name, (0, 255, 0))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Vẽ tên + confidence
        label = f"{class_name} {conf:.2f}"
        (label_w, label_h), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - label_h - baseline - 4),
                      (x1 + label_w, y1), color, -1)
        cv2.putText(frame, label, (x1, y1 - baseline - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Vẽ tâm
        cv2.circle(frame, (cx, cy), 3, (0, 255, 255), -1)

    return frame, detections


def detect_from_camera(model_path: str, camera_id: int, conf: float):
    """Nhận diện real-time từ camera."""
    model = YOLO(model_path)
    print(f"[INFO] Model loaded: {model_path}")
    print(f"[INFO] Classes: {model.names}")

    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"[ERROR] Không mở được camera {camera_id}")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("[INFO] Nhấn 'q' để thoát, 's' để chụp ảnh kết quả")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Chạy YOLO inference
        results = model(frame, conf=conf, verbose=False)
        annotated, detections = draw_detections(frame, results, conf)

        # Hiển thị FPS và số quân phát hiện
        fps_text = f"Pieces: {len(detections)}"
        cv2.putText(annotated, fps_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # In thông tin ra console (mỗi 30 frame)
        frame_count += 1
        if frame_count % 30 == 0 and detections:
            print(f"\n--- Frame {frame_count} | {len(detections)} pieces ---")
            for d in detections:
                print(f"  {d['class']:20s} conf={d['confidence']:.2f}  "
                      f"center=({d['center'][0]}, {d['center'][1]})")

        cv2.imshow("Chinese Chess Detection", annotated)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            save_path = f"detection_result_{frame_count}.jpg"
            cv2.imwrite(save_path, annotated)
            print(f"  [SAVED] {save_path}")

    cap.release()
    cv2.destroyAllWindows()


def detect_from_source(model_path: str, source: str, conf: float):
    """Nhận diện trên ảnh tĩnh hoặc thư mục ảnh."""
    model = YOLO(model_path)
    print(f"[INFO] Model loaded: {model_path}")

    if os.path.isdir(source):
        # Thư mục ảnh
        image_exts = {'.jpg', '.jpeg', '.png', '.bmp'}
        image_files = sorted([
            os.path.join(source, f) for f in os.listdir(source)
            if os.path.splitext(f)[1].lower() in image_exts
        ])
        print(f"[INFO] Tìm thấy {len(image_files)} ảnh trong {source}")
    else:
        image_files = [source]

    for img_path in image_files:
        frame = cv2.imread(img_path)
        if frame is None:
            print(f"[WARN] Không đọc được: {img_path}")
            continue

        results = model(frame, conf=conf, verbose=False)
        annotated, detections = draw_detections(frame, results, conf)

        print(f"\n{'='*50}")
        print(f"File: {img_path}")
        print(f"Detected {len(detections)} pieces:")
        for d in detections:
            print(f"  {d['class']:20s} conf={d['confidence']:.2f}  "
                  f"bbox=({d['bbox'][0]},{d['bbox'][1]},{d['bbox'][2]},{d['bbox'][3]})  "
                  f"center=({d['center'][0]}, {d['center'][1]})")

        # Resize nếu ảnh quá lớn
        h, w = annotated.shape[:2]
        if w > 1280:
            scale = 1280 / w
            annotated = cv2.resize(annotated, (1280, int(h * scale)))

        cv2.imshow("Detection Result", annotated)
        print("Nhấn phím bất kỳ để tiếp, 'q' để thoát")
        key = cv2.waitKey(0) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Nhận diện quân cờ tướng real-time bằng YOLOv8")
    parser.add_argument("--model", type=str, required=True,
                        help="Đường dẫn tới model (.pt)")
    parser.add_argument("--camera", type=int, default=None,
                        help="Camera ID cho real-time")
    parser.add_argument("--source", type=str, default=None,
                        help="Đường dẫn ảnh hoặc thư mục ảnh")
    parser.add_argument("--conf", type=float, default=0.25,
                        help="Ngưỡng confidence (mặc định: 0.25)")
    args = parser.parse_args()

    if args.source:
        detect_from_source(args.model, args.source, args.conf)
    elif args.camera is not None:
        detect_from_camera(args.model, args.camera, args.conf)
    else:
        # Mặc định dùng camera 0
        detect_from_camera(args.model, 0, args.conf)

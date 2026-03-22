import cv2
import numpy as np
import os
import sys

# Thêm đường dẫn gốc vào sys.path để import các module mới
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from software.common.config import *
from software.vision.detector import ChessDetector
from software.vision.board_mapper import BoardMapper
from software.chess_engine.engine_client import EngineClient
from software.control.kinematics import Kinematics, ucci_to_grid_label

def main():
    print(" Đang khởi động hệ thống CCR3...")
    
    # 1. Khởi tạo các module
    detector = ChessDetector(MODEL_PATH, CONF_THRESHOLD)
    mapper = BoardMapper()
    engine = EngineClient(ENGINE_PATH)
    
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f" KHÔNG MỞ ĐƯỢC CAMERA SỐ {CAMERA_INDEX}!")
        return

    cv2.namedWindow("Control Panel")
    cv2.resizeWindow("Control Panel", 450, 450)
    # (Thêm các trackbar ở đây tương tự như testpikafish2.py)
    # ... lược bớt để demo ...

    print(" Hệ thống đã sẵn sàng. Nhấn SPACE để phân tích.")

    while True:
        ret, frame_raw = cap.read()
        if not ret: break

        # Xử lý frame (crop, resize...)
        # ... logic zoom/crop từ testpikafish2.py ...
        frame = frame_raw # Placeholder

        cv2.imshow("LIVE CAMERA", frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'): break
        elif key == ord(' '):
            print(" Đang phân tích...")
            
            # Step 1: Detect
            yolo_pieces, pieces_list, annotated_frame = detector.detect_pieces(frame)
            
            # Step 2: Map Grid
            # (Giả sử các giá trị trackbar được truyền vào)
            final_points = mapper.detect_grid(frame, 135, 100, 1, 28, pieces_list, 10)
            mapped_points, pA1, pA9, pJ1 = mapper.map_points_to_labels(final_points)
            
            if not mapped_points:
                print(" Lỗi: Không bắt được lưới!")
                continue
                
            # Step 3: Engine
            current_fen, grid_to_piece = mapper.generate_fen(mapped_points, yolo_pieces)
            best_move, msg = engine.get_best_move(current_fen, THINK_TIME_MS)
            
            if best_move:
                print(f" Nước đi tốt nhất: {best_move}")
                # Step 4: Kinematics & Move planning
                # ... logic điều khiển robot ...
            
    cap.release()
    cv2.destroyAllWindows()
    engine.stop_engine()

if __name__ == "__main__":
    main()

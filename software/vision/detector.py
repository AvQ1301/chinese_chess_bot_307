import cv2
import numpy as np
from ultralytics import YOLO

class ChessDetector:
    def __init__(self, model_path, conf_threshold=0.7):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

    def detect_pieces(self, frame, show_text=False):
        results = self.model.predict(source=frame, conf=self.conf_threshold, verbose=False)
        yolo_pieces = []
        pieces_list = []
        
        annotated_frame = frame.copy()
        
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)  
            r = int(min(x2 - x1, y2 - y1) / 2)  
            cls_name = self.model.names[int(box.cls[0])]
            
            yolo_pieces.append((cx, cy, r, cls_name, int(x1), int(y1), int(x2), int(y2)))
            pieces_list.append((cx, cy, r))
            
            if show_text:
                cv2.putText(annotated_frame, cls_name, (int(x1), int(y1) - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        
        return yolo_pieces, pieces_list, annotated_frame

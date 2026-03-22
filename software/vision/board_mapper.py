import cv2
import numpy as np
import math
from software.common.config import FEN_MAP, ROBOT_SIDE, ROW_LABELS

class BoardMapper:
    def __init__(self):
        pass

    def detect_grid(self, frame, thresh_val, length_val, min_thick, max_thick, pieces_list, shadow_buf):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
        scale = max(5, 120 - length_val)
        h_size, v_size = int(frame.shape[1] / scale), int(frame.shape[0] / scale)

        mask_h = cv2.morphologyEx(binary, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (h_size, 1)))
        mask_v = cv2.morphologyEx(binary, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_size)))

        for cnt in cv2.findContours(mask_h, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
            if not (min_thick <= cv2.boundingRect(cnt)[3] <= max_thick): cv2.drawContours(mask_h, [cnt], -1, 0, -1)
        for cnt in cv2.findContours(mask_v, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
            if not (min_thick <= cv2.boundingRect(cnt)[2] <= max_thick): cv2.drawContours(mask_v, [cnt], -1, 0, -1)

        mask_joints = cv2.bitwise_and(cv2.dilate(mask_h, np.ones((3, 3)), iterations=5),
                          cv2.dilate(mask_v, np.ones((3, 3)), iterations=5))

        raw_points = []
        for cnt in cv2.findContours(mask_joints, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
            if cv2.contourArea(cnt) > 0:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                    is_shadow = any(math.sqrt((cx - px)**2 + (cy - py)**2) < (pr + shadow_buf) for px, py, pr in pieces_list)
                    if not is_shadow: raw_points.append((cx, cy))

        raw_points.extend([(px, py) for px, py, _ in pieces_list])

        final_points = []
        for cx, cy in raw_points:
            if sum(1 for tx, ty in raw_points if abs(cy - ty) <= 15) >= 5 and sum(1 for tx, ty in raw_points if abs(cx - tx) <= 15) >= 4:
                final_points.append((cx, cy))
        
        return final_points

    def map_points_to_labels(self, final_points):
        mapped_points = []
        pixel_A1 = pixel_A9 = pixel_J1 = None

        if len(final_points) > 10:
            xs, ys = [p[0] for p in final_points], [p[1] for p in final_points]

            valid_xs = [x for x in xs if sum(1 for tx in xs if abs(tx - x) <= 15) >= 5]
            valid_ys = [y for y in ys if sum(1 for ty in ys if abs(ty - y) <= 15) >= 5]

            if valid_xs and valid_ys:
                min_x, max_x = min(valid_xs), max(valid_xs)
                min_y, max_y = min(valid_ys), max(valid_ys)
                width, height = max_x - min_x, max_y - min_y

                if width > 0 and height > 0:
                    step_x, step_y = width / 8.0, height / 9.0
                    river_top = min_y + 4.2 * step_y
                    river_bottom = min_y + 4.8 * step_y

                    for cx, cy in final_points:
                        if cx < min_x - 15 or cx > max_x + 15 or cy < min_y - 15 or cy > max_y + 15:
                            continue
                        if river_top < cy < river_bottom:
                            continue

                        c_idx, r_idx = max(0, min(int(round((cx - min_x)/step_x)), 8)), max(0, min(int(round((cy - min_y)/step_y)), 9))
                        label_str = f"{ROW_LABELS[r_idx]}{c_idx + 1}"

                        if not any(pt['label'] == label_str for pt in mapped_points):
                            mapped_points.append({'label': label_str, 'px': cx, 'py': cy})
                            if label_str == 'A1': pixel_A1 = (cx, cy)
                            if label_str == 'A9': pixel_A9 = (cx, cy)
                            if label_str == 'J1': pixel_J1 = (cx, cy)
        
        return mapped_points, pixel_A1, pixel_A9, pixel_J1

    def generate_fen(self, mapped_points, yolo_pieces):
        board = [["" for _ in range(9)] for _ in range(10)]
        grid_to_piece = {} 
        
        for p in yolo_pieces:
            cx, cy, cls_name = p[0], p[1], p[3]
            best_dist = float('inf')
            best_row, best_col = -1, -1
            best_label = ""
            
            for pt in mapped_points:
                dist = math.sqrt((cx - pt['px'])**2 + (cy - pt['py'])**2)
                if dist < best_dist:
                    best_dist = dist
                    best_row = ord(pt['label'][0]) - ord('A')
                    best_col = int(pt['label'][1:]) - 1
                    best_label = pt['label']

            if best_row != -1 and best_col != -1 and best_dist < 25:
                board[best_row][best_col] = FEN_MAP.get(cls_name, "")
                grid_to_piece[best_label] = cls_name

        fen_rows = []
        for row in board:
            empty_count = 0
            row_str = ""
            for cell in row:
                if cell == "":
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += cell
            if empty_count > 0:
                row_str += str(empty_count)
            fen_rows.append(row_str)
        
        fen_string = "/".join(fen_rows) + f" {ROBOT_SIDE} - - 0 1"
        return fen_string, grid_to_piece

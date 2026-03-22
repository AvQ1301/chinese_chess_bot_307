import os

# =============================================================
# 1. CẤU HÌNH HỆ THỐNG
# =============================================================
MODEL_PATH = "software/vision/models/best (2).pt"                
CONF_THRESHOLD = 0.7                      
CAMERA_INDEX = 1                          
THINK_TIME_MS = 2000                      

# Mặc định Robot cầm quân Đen (Pikafish sẽ tính nước đi cho phe Đen)
ROBOT_SIDE = 'b' # 'w' cho quân trắng, 'b' cho quân đen 

# TỪ ĐIỂN DỊCH TÊN YOLO SANG KÝ HIỆU FEN QUỐC TẾ
FEN_MAP = {
    "tuongdo": "K", "sido": "A", "tinhdo": "B", "mado": "N", "xedo": "R", "phaodo": "C", "totdo": "P",
    "tuongden": "k", "siden": "a", "tinhden": "b", "maden": "n", "xeden": "r", "phaoden": "c", "totden": "p"
}

ROW_LABELS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
REAL_WIDTH_A1_A9 = 230.0
REAL_HEIGHT_A1_J1 = 234.0
OFFSET_X = 115.0
OFFSET_Y = 300.0

# Paths
ENGINE_PATH = os.path.join("software", "chess_engine", "pikafish", "pikafish.exe")

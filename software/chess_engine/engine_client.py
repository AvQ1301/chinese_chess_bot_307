import subprocess
import os

class EngineClient:
    def __init__(self, engine_path):
        self.engine_path = engine_path
        self.engine = None
        self.start_engine()

    def start_engine(self):
        print(f" Đang khởi động não bộ Pikafish tại {self.engine_path}...")
        try:
            self.engine = subprocess.Popen(
                self.engine_path, 
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(" Đã kết nối thành công với Pikafish!\n")
        except FileNotFoundError:
            print(f" LỖI: Không tìm thấy file {self.engine_path}.")
            # Note: In a real app, don't use os._exit here
            raise

    def get_best_move(self, fen_string, think_time_ms):
        self.engine.stdin.write(f"position fen {fen_string}\n")
        self.engine.stdin.write(f"go movetime {think_time_ms}\n")
        self.engine.stdin.flush()
        
        game_over_msg = None
        
        while True:
            line = self.engine.stdout.readline().strip()
            
            # --- BỘ LỌC TÍN HIỆU THẮNG/THUA ---
            parts = line.split()
            if "score" in parts and "mate" in parts:
                mate_idx = parts.index("mate")
                if mate_idx + 1 < len(parts):
                    mate_val = parts[mate_idx + 1]
                    if mate_val == "1":
                        game_over_msg = " CHIẾU TƯỚNG HẾT CỜ! NƯỚC ĐI NÀY SẼ KẾT LIỄU BẠN (MÁY THẮNG)!"
                    elif mate_val == "-1" or mate_val == "0":
                        game_over_msg = " MÁY TÍNH ĐANG BỊ CHIẾU BÍ VÀ SẮP THUA!"

            if line.startswith("bestmove"):
                best_move = parts[1] if len(parts) > 1 else ""
                
                # Nếu máy trả về none tức là nó không còn nước đi hợp lệ nào
                if best_move == "(none)" or best_move == "0000":
                    return None, " CHÚC MỪNG! BẠN ĐÃ CHIẾU BÍ VÀ GIÀNH CHIẾN THẮNG TRƯỚC AI!"
                
                return best_move, game_over_msg

    def stop_engine(self):
        if self.engine:
            self.engine.terminate()

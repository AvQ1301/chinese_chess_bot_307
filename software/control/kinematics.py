from software.common.config import ROW_LABELS

def ucci_to_grid_label(ucci_str):
    """
    Converts UCCI move (e.g., 'a1') to grid label (e.g., 'J1')
    """
    file_char = ucci_str[0].lower() 
    rank_char = ucci_str[1]         
    col = str(ord(file_char) - ord('a') + 1)
    row = chr(ord('A') + (9 - int(rank_char)))
    return f"{row}{col}"

class Kinematics:
    def __init__(self, pixel_A1, pixel_A9, pixel_J1, real_width, real_height, offset_x, offset_y):
        self.pixel_A1 = pixel_A1
        self.pixel_A9 = pixel_A9
        self.pixel_J1 = pixel_J1
        self.real_width = real_width
        self.real_height = real_height
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        if pixel_A1 and pixel_A9 and pixel_J1:
            self.dx = abs(pixel_A9[0] - pixel_A1[0])
            self.dy = abs(pixel_J1[1] - pixel_A1[1])
        else:
            self.dx = self.dy = 0

    def get_robot_xy(self, px, py):
        if self.dx <= 0 or self.dy <= 0:
            return None, None
            
        rob_x = round(((px - self.pixel_A1[0]) * (self.real_width / self.dx)) - self.offset_x, 1)
        rob_y = round(((self.pixel_A1[1] - py) * (self.real_height / self.dy)) - self.offset_y, 1)
        return rob_x, rob_y

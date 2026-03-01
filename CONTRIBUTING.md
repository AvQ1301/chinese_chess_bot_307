# Hướng dẫn đóng góp - Contributing Guide

Cảm ơn bạn đã quan tâm đến dự án **CCR3 - Chinese Chess Robot**! 🎉

---

## ⚠️ Quy tắc chung cho TẤT CẢ thành viên

> **Bắt buộc tuân thủ** — vi phạm sẽ bị reject PR.

| # | Quy tắc | Chi tiết |
|---|---------|----------|
| 1 | **Branch riêng theo tên** | Mỗi người tạo branch: `feature/<tên>-<mô-tả>`. VD: `feature/phuong-kinematics`, `feature/hoang-vision` |
| 2 | **Comment nhất quán** | Code phải có comment bằng tiếng Việt **hoặc** tiếng Anh, nhất quán trong cùng một file |
| 3 | **Docstring bắt buộc** | Mỗi file/module phải có docstring giải thích chức năng ở đầu file |
| 4 | **KHÔNG push trực tiếp lên `main`** | Luôn tạo Pull Request (PR) để review trước khi merge |
| 5 | **KHÔNG commit file > 100MB** | Dùng [Git LFS](https://git-lfs.github.com/) cho file 3D lớn (`.SLDPRT`, `.SLDASM`, `.STEP`...) |
| 6 | **Giữ `.gitignore` sạch** | Phải loại trừ: `__pycache__/`, `*.pyc`, `.DS_Store`, `node_modules/`, `*.tmp` |
| 7 | **Ghi rõ dependencies** | Python → `requirements.txt`, Arduino → `platformio.ini` |

### Ví dụ docstring đầu file

**Python:**
```python
"""
CCR3 - Chinese Chess Robot
Module: Forward Kinematics

Tính toán động học thuận cho cánh tay SCARA 2 bậc tự do.
Input: góc khớp (q1, q2)
Output: vị trí end-effector (x, y)
"""
```

**C++ (firmware):**
```cpp
/**
 * CCR3 - Chinese Chess Robot
 * Module: Stepper Motor Control
 *
 * Điều khiển stepper motor qua driver A4988/TMC2209.
 * Nhận lệnh từ Raspberry Pi qua Serial.
 */
```

---

## Quy trình đóng góp

### 1. Clone repo
```bash
git clone https://github.com/AvQ1301/chinese_chees_bot_307.git
cd chinese_chees_bot_307
```

### 2. Tạo branch riêng (BẮT BUỘC)
```bash
# Format: feature/<tên-bạn>-<mô-tả-ngắn>
git checkout -b feature/phuong-kinematics
git checkout -b feature/hoang-yolo-detection
git checkout -b fix/quan-serial-timeout
```

### 3. Quy tắc đặt tên branch
- `feature/<tên>-<mô-tả>` – Tính năng mới
- `fix/<tên>-<mô-tả>` – Sửa lỗi
- `docs/<tên>-<mô-tả>` – Cập nhật tài liệu
- `refactor/<tên>-<mô-tả>` – Tái cấu trúc code

### 4. Commit message
Sử dụng format:
```
<type>: <mô tả ngắn>

<mô tả chi tiết (nếu cần)>
```

Ví dụ:
```
feat: thêm module nhận diện quân cờ bằng YOLOv8
fix: sửa lỗi tính toán động học ngược
docs: cập nhật sơ đồ đấu nối điện
```

### 5. Push và tạo Pull Request (KHÔNG push lên main)
```bash
git push origin feature/phuong-kinematics
```
Sau đó vào GitHub → tạo **Pull Request** → chờ review → merge.

#### Checklist trước khi tạo PR:
- [ ] Code có comment/docstring đầy đủ
- [ ] Không có file > 100MB
- [ ] Đã test cơ bản
- [ ] Dependencies đã ghi vào `requirements.txt` hoặc `platformio.ini`
- [ ] Mô tả rõ ràng thay đổi trong PR
- [ ] Đính kèm ảnh/video nếu có

## Quy tắc code

- **Python**: Tuân thủ PEP 8
- **C/C++ (firmware)**: Sử dụng camelCase cho biến, PascalCase cho class
- Comment bằng tiếng Việt hoặc tiếng Anh — **nhất quán trong cùng file**
- Viết unit test cho các module quan trọng
- Mỗi file **phải có docstring** giải thích chức năng

## Git LFS cho file lớn

Nếu cần commit file 3D (`.SLDPRT`, `.SLDASM`, `.STEP`, `.STL` lớn):
```bash
git lfs install
git lfs track "*.SLDPRT"
git lfs track "*.SLDASM"
git lfs track "*.STEP"
git add .gitattributes
git commit -m "chore: setup Git LFS for CAD files"
```

## Create issues in JIRA
https://support.atlassian.com/jira-software-cloud/docs/reference-issues-in-your-development-work/

## Cấu trúc thư mục

Vui lòng đặt file đúng thư mục theo cấu trúc đã quy định trong README.

## Liên hệ

Nếu có thắc mắc, vui lòng tạo Issue hoặc liên hệ trực tiếp qua nhóm Lab307.

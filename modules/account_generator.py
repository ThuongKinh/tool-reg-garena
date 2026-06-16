import random
import string

def generate_account_data():
    """
    Sinh cặp dữ liệu Username và Password theo Ma trận cấu trúc con người.
    Bùng nổ tổ hợp biến số để giảm tỉ lệ trùng lặp xuống < 0.01%.
    """
    # Khởi tạo gốc ngày sinh ngẫu nhiên (Ngày: 01-28, Tháng: 01-12, Năm: 1990-2007)
    day = f"{random.randint(1, 28):02d}"
    month = f"{random.randint(1, 12):02d}"
    year = f"{random.randint(1990, 2007)}"
    
    # 1. Mở rộng bể Họ và Tên phổ biến tại Việt Nam để tăng tổ hợp gốc
    ho_pool = ["nguyen", "tran", "le", "pham", "hoang", "phan", "vu", "vo", "dang", "bui", "do", "ho", "ngo", "duong", "ly"]
    ten_pool = ["tam", "hai", "linh", "anh", "dung", "phong", "quan", "minh", "vy", "lan", "huong", "tuan", "dat", "khang", "duy", "son"]
    
    # Từ khóa chèn thêm phong cách game thủ khi bị hệ thống báo trùng tên
    sub_words = ["pro", "vip", "kun", "isme", "gaming", "tv", "chibi", "dz", "01", "ff"]
    
    # 2. XOAY TUA CẤU TRÚC (Đa dạng hóa định dạng để qua mặt AI quét mẫu của Garena)
    struct_type = random.randint(1, 3)
    
    if struct_type == 1:
        # Cấu trúc 1: Họ + Tên + Từ chèn + Số ngẫu nhiên (Ví dụ: tranminhpro882)
        name_base = random.choice(ho_pool) + random.choice(ten_pool) + random.choice(sub_words)
        num_part = f"{random.randint(10, 999)}"
        username = f"{name_base}{num_part}"
        
    elif struct_type == 2:
        # Cấu trúc 2: Viết tắt Họ + Tên đầy đủ + Chuỗi ngày tháng năm sinh (Ví dụ: nminh160602)
        initial_ho = random.choice(ho_pool)[0]
        name_base = initial_ho + random.choice(ten_pool)
        username = f"{name_base}{day}{month}{year[-2:]}"
        
    else:
        # Cấu trúc 3: Họ + Tên + Băm đuôi số entropy lớn (Ví dụ: phamlinh9831)
        name_base = random.choice(ho_pool) + random.choice(ten_pool)
        num_part = f"{random.randint(100, 9999)}"
        username = f"{name_base}{num_part}"
        
    # Làm sạch chuỗi, cắt cứng đúng 15 ký tự theo quy định Garena
    username = username.lower().strip()[:15]
    
    # ──► FORMAT PASSWORD (Đồng bộ theo yêu cầu: Viết tắt + 2 số ngày sinh + Ký tự đặc biệt)
    abbreviations = ["Grn", "Garena", "Acc", "Sll", "Mmo", "Tool", "Pwt", "Vn"]
    abbr_part = random.choice(abbreviations) + ''.join(random.choice(string.ascii_lowercase) for _ in range(2))
    
    # Lấy 2 số đầu ngày sinh (Dùng luôn biến day)
    num_part_pass = day
    special_char = random.choice("!@")
    
    password = f"{abbr_part}{num_part_pass}{special_char}"
    
    # Bảo hiểm độ dài mật khẩu tối thiểu luôn >= 10 ký tự
    if len(password) < 10:
        remaining = 11 - len(password)
        password += ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(remaining))
        
    return username, password

import json
import os
from datetime import datetime

def save_account_json(username, password, email, filename="outputs/accounts.json"):
    """
    Lưu thông tin tài khoản đăng ký thành công vào file JSON bảo toàn cấu trúc.
    """
    # 1. Tự động tạo thư mục outputs nếu chưa tồn tại trên Linux Mint
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # 2. Đóng gói dữ liệu danh tính mới kèm mốc thời gian đăng ký
    new_account = {
        "username": username,
        "password": password,
        "email": email,
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    accounts_list = []
    
    # 3. Nếu file JSON đã tồn tại, đọc dữ liệu cũ ra trước để nạp thêm vào
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                accounts_list = json.load(f)
                if not isinstance(accounts_list, list):
                    accounts_list = []
        except (json.JSONDecodeError, PermissionError):
            # Phòng trường hợp file bị lỗi định dạng định dạng hoặc bị lock ngầm
            accounts_list = []
            
    # 4. Thêm tài khoản mới vào danh sách
    accounts_list.append(new_account)
    
    # 5. Ghi lại toàn bộ danh sách vào file JSON (indent=4 cho đẹp mắt, dễ nhìn)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(accounts_list, f, ensure_ascii=False, indent=4)
        
    print(f"[💾 STORAGE] Đã ghi nhận thành công acc {username} vào {filename}!")

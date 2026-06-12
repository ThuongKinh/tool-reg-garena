from modules.browser.driver_config import stealth_driver_context
import time

def test_bot_detection():
    print("[INFO] Đang khởi tạo stealth driver để test Anti-bot...")
    
    # Sử dụng context manager bạn đã viết
    with stealth_driver_context(headless=False) as driver:
        print("[INFO] Trình duyệt đã mở. Đang đi tới trang check vân tay...")
        
        # Trang này dùng để test độ ẩn danh
        driver.get("https://browserleaks.com/webgl")
        
        print("[SUCCESS] Đã vào trang test!")
        print("[INFO] Hãy nhìn vào mục 'Unmasked Vendor' và 'Unmasked Renderer'.")
        print("Nếu nó hiện 'Google Inc.' và 'ANGLE (Intel...) Whitelist' nghĩa là bạn đã FAKE THÀNH CÔNG!")
        
        # Giữ màn hình 20 giây để bạn quan sát bằng mắt trước khi tự đóng
        time.sleep(20)

if __name__ == "__main__":
    test_bot_detection()

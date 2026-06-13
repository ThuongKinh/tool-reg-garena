import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from modules.browser.driver_config import create_stealth_driver

def run_garena_test():
    print("[PREPARE] Khởi chạy luồng Test Garena sạch...")
    driver = create_stealth_driver(headless=False)
    
    try:
        print("🌐 Đang truy cập Garena Universal Form...")
        driver.get("https://sso.garena.com/universal/register?locale=vi-VN")
        
        print("\n" + "="*60)
        print("🎯 LUỒNG JAVASCRIPT ĐÃ ĐƯỢC GIẢI PHÓNG")
        print("👉 Bây giờ bạn hãy tự tay gõ thông tin và kéo thử Captcha.")
        print("="*60)
        
        # Thay thế hoàn toàn vòng lặp while True bằng lệnh tạm dừng tự nhiên
        input("\nNhấn ENTER tại đây nếu muốn đóng trình duyệt và kết thúc mẻ test...")
        
    except Exception as e:
        print("Lỗi luồng chạy:", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    run_garena_test()
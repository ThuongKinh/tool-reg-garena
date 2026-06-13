import undetected_chromedriver as uc
from contextlib import contextmanager
import platform
import subprocess
import os
import shutil
import re

def get_local_chrome_major_version():
    if platform.system() == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            version_match = re.search(r"(\d+)\.", version)
            if version_match:
                return version_match.group(1)
        except Exception:
            pass
    return "124"

def create_stealth_driver(headless: bool = False):
    options = uc.ChromeOptions()
    chrome_major = get_local_chrome_major_version()
    
    # Giữ User-Agent sạch, không chỉnh sửa sâu
    user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_major}.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")

    # Tạo thư mục profile ẩn danh sạch hoàn toàn cho mỗi lượt
    data_dir = os.path.join(os.getcwd(), "outputs", "chrome_test_profile")
    if os.path.exists(data_dir):
        try:
            shutil.rmtree(data_dir, ignore_errors=True)
        except:
            pass
    options.add_argument(f"--user-data-dir={data_dir}")
    options.add_argument("--incognito") # Ép chạy chế độ ẩn danh sạch

    if not headless:
        options.add_argument("--start-maximized")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--lang=vi-VN")
        
        # GỠ BỎ SWIFTSHADER: Cho phép Chrome dùng card đồ họa thật của máy Dell để JavaScript chạy mượt, đúng tốc độ
        options.add_argument("--disable-blink-features=AutomationControlled")

    try:
        chrome_version_int = int(chrome_major)
        driver = uc.Chrome(
            options=options, 
            use_subprocess=True,
            version_main=chrome_version_int
        )
    except Exception as e:
        print(f"[ERROR] Không thể khởi tạo driver: {e}")
        raise

    # KHÔNG TIÊM MÃ GIẢ LẬP ĐỂ TRÁNH LỖI PHÁT HIỆN CAN THIỆP JAVASCRIPT
    return driver

def quit_driver(driver):
    try:
        if driver:
            driver.quit()
    except Exception:
        pass

@contextmanager
def stealth_driver_context(headless: bool = False):
    driver = None
    try:
        driver = create_stealth_driver(headless=headless)
        yield driver
    finally:
        quit_driver(driver)
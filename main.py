import os
import sys
import time
import random
import string
import csv
import secrets
import traceback 
import numpy as np
import urllib.request  
from datetime import datetime

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from modules.browser.driver_config import stealth_driver_context
from modules.mail.mailtm_manager import MailTmManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def get_public_ip() -> str:
    """Lấy IP mạng công cộng hiện tại qua API ipify."""
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=4) as response:
            return response.read().decode('utf-8').strip()
    except Exception:
        return None

def rotate_ip_and_wait(old_ip: str):
    """Treo luồng nhắc người dùng xoay mạng bằng điện thoại iPhone."""
    print("\n" + "="*60)
    print("🔄 [NETWORK ROTATE] YÊU CẦU XOAY IP TRÊN IPHONE")
    print(f" ➔ IP cũ vừa dùng: {old_ip}")
    print(" 👉 HÀNH ĐỘNG: Hãy vuốt mở Control Center trên iPhone, BẬT rồi TẮT Chế độ máy bay.")
    print("="*60 + "\n")
    
    while True:
        time.sleep(2.5)  
        current_ip = get_public_ip()
        
        if current_ip is None:
            print("[NETWORK] Đang đợi iPhone cấp lại IP dữ liệu di động...")
            continue
            
        if current_ip != old_ip:
            print(f"✅ [NETWORK] Đã nhận diện dải IP mới hoàn toàn từ iPhone: {current_ip}")
            time.sleep(2)
            return current_ip
        else:
            print(f"[NETWORK] Vẫn phát hiện IP cũ ({current_ip}). Vui lòng gạt lại mạng trên iPhone...")

def gen_username_human(account_index=1) -> str:
    first_names = ["nguyen", "tran", "le", "pham", "hoang", "phan", "vu", "vo", "dang", "bui", "do", "ho"]
    last_names = ["tam", "hai", "linh", "anh", "dung", "phong", "quan", "minh", "vy", "lan", "huong", "tuan"]
    name_part = random.choice(first_names) + random.choice(last_names)
    
    birth_formats = [
        f"{random.randint(1,28):02d}{random.randint(1,12):02d}{random.randint(85,99)}", 
        f"{random.randint(1,28):02d}{random.randint(1,12):02d}{random.randint(0,6):02d}", 
        f"{random.randint(1990, 2006)}" 
    ]
    birth_part = random.choice(birth_formats)
    username = f"{name_part}{birth_part}{account_index}"
    return username[:15]

def gen_password_human() -> str:
    length = secrets.randbelow(5) + 10  
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "@#$!"
    
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]
    
    all_chars = lowercase + uppercase + digits + special
    password += [secrets.choice(all_chars) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)

def move_mouse_humanlike(driver, target_element):
    """Mô phỏng chuột rê mượt tránh bẫy dịch chuyển tức thời."""
    try:
        actions = ActionChains(driver)
        random_offset_x = random.randint(-100, -50)
        random_offset_y = random.randint(-30, -15)
        actions.move_to_element_with_offset(target_element, random_offset_x, random_offset_y).perform()
        time.sleep(random.uniform(0.12, 0.25))
        
        actions_final = ActionChains(driver)
        actions_final.move_to_element(target_element).perform()
        time.sleep(random.uniform(0.15, 0.3))
    except Exception as e:
        try:
            ActionChains(driver).move_to_element(target_element).perform()
        except:
            pass

def is_garena_captcha_visible(driver) -> bool:
    try:
        captcha_selectors = [
            ".geetest_popup_box", "[class*='captcha']", "[id*='captcha']",
            ".universal-captcha-container", "iframe[src*='captcha']", ".geetest_widget",
            ".geetest_panel", ".geetest_wind"
        ]
        for selector in captcha_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                if el.is_displayed() and el.size['width'] > 0:
                    return True
    except:
        pass
    return False

# ==================== TẦNG QUÉT SÂU HẠ TẦNG LOG MẠNG VÀ CONSOLE ====================
def dump_and_print_browser_logs(driver):
    """Bóc tách và in ra toàn bộ log lỗi điều hướng/bảo mật từ Console Tab của Chrome."""
    print("\n🔮 [DEEP NETWORK LOGS] --- NHẬT KÝ HỆ THỐNG TRÌNH DUYỆT TẠI THỜI ĐIỂM CHẶN ---")
    try:
        logs = driver.get_log('browser')
        if not logs:
            print(" ➔ Không ghi nhận lỗi mã nguồn Javascript hoặc lỗi 403 cục bộ.")
        for entry in logs:
            # Lọc và hiển thị trực quan mức độ lỗi
            timestamp = datetime.fromtimestamp(entry.get('timestamp', 0)/1000.0).strftime('%H:%M:%S')
            print(f" [{timestamp}][{entry['level']}] ➔ {entry['message']}")
    except Exception as e:
        print(f" Không thể truy xuất log bảo mật: {e}")
    print("="*70 + "\n")

def check_and_wait_for_captcha(driver, stage_name=""):
    """Quét nhanh sự xuất hiện của Captcha. Nếu có, bóc log console mạng rồi dừng chờ lệnh."""
    time.sleep(0.6)
    if is_garena_captcha_visible(driver):
        print("\n" + "!"*60)
        print(f"🚨 [ALERT] PHÁT HIỆN CAPTCHA XUẤT HIỆN SỚM (Giai đoạn: {stage_name})!")
        
        # Gọi tầng quét log mạng/console ngay khi bị dính chặn
        dump_and_print_browser_logs(driver)
        
        print(" 👉 TRẠNG THÁI: Tạm dừng điền form.")
        print(" 👉 HÀNH ĐỘNG: Giải tay trực tiếp trên màn hình Chrome.")
        print("!"*60 + "\n")
        input("[WAIT] Sau khi giải xong, nhấn ENTER tại đây để chạy tiếp...")
        print("[CONTINUE] Tiếp tục xử lý form...")
        time.sleep(1)
# ===================================================================================

def human_type_custom(driver, wait, element_selector, text, speed_mode="normal"):
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, element_selector)))
    move_mouse_humanlike(driver, element)
    
    ActionChains(driver).click(element).perform()
    time.sleep(random.uniform(0.25, 0.45))
    
    special_chars = "@#$!"
    for index, char in enumerate(text):
        if speed_mode == "fast":
            delay_between_keys = random.uniform(0.060, 0.110)
        elif speed_mode == "slow":
            delay_between_keys = random.uniform(0.180, 0.320)
        else:
            delay_between_keys = random.uniform(0.090, 0.180)
            
        # Giả lập khựng nhịp sinh học
        if index > 0 and index % 4 == 0:
            delay_between_keys += random.uniform(0.120, 0.250)
            
        if char in special_chars:
            element.send_keys(char)
            time.sleep(delay_between_keys)
        else:
            key_hold_time = random.uniform(0.065, 0.115) 
            try:
                ActionChains(driver).key_down(char).perform()
                time.sleep(key_hold_time) 
                ActionChains(driver).key_up(char).perform()
                time.sleep(delay_between_keys) 
            except Exception:
                element.send_keys(char)
                time.sleep(delay_between_keys)
                
    time.sleep(random.uniform(0.40, 0.70))

def save_account_to_csv(username, password, email):
    file_path = "outputs/accounts.csv"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file_exists = os.path.isfile(file_path)
    
    with open(file_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Tài khoản", "Mật khẩu", "Email", "Ngày tạo"])
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([username, password, email, current_time])
    print(f"[STORAGE] Đã lưu tài khoản thành công vào: {file_path}")

def run_single_registration(account_index: int) -> bool:
    print(f"\n[PREPARE] Khởi tạo luồng đăng ký cho tài khoản index: #{account_index}")
    
    import platform
    try:
        current_os = platform.system()
        if current_os == "Windows":
            os.system("taskkill /f /im chrome.exe >nul 2>&1")
            os.system("taskkill /f /im chromedriver.exe >nul 2>&1")
        else:
            os.system("pkill -9 -f chrome >/dev/null 2>&1")
            os.system("pkill -9 -f chromedriver >/dev/null 2>&1")
    except Exception:
        pass
        
    mail_manager = MailTmManager()
    if not mail_manager.create_account():
        print("[CRITICAL] Khởi tạo tài khoản Mail.tm thất bại.")
        return False
        
    garena_user = gen_username_human(account_index)
    garena_pass = gen_password_human()
    
    print("\n" + "="*50)
    print(f"[THÔNG TIN TÀI KHOẢN KHỞI TẠO NỀN]")
    print(f" ➔ Garena User : {garena_user}")
    print(f" ➔ Garena Pass : {garena_pass}")
    print(f" ➔ Mail.tm Box : {mail_manager.email}")
    print("="*50 + "\n")
    
    profile_folder = os.path.abspath(os.path.join("outputs", "chrome_profile_local")) 
    profile_lock = os.path.join(profile_folder, "SingletonLock")
    if os.path.lexists(profile_lock):
        try:
            if os.path.islink(profile_lock):
                os.unlink(profile_lock)
            else:
                os.remove(profile_lock)
        except Exception:
            pass

    try:
        with stealth_driver_context(profile_folder, headless=False) as driver:
            driver.set_page_load_timeout(35)
            
            print("[BROWSER] Đang tải giao diện SSO Garena...")
            try:
                driver.get("https://sso.garena.com/universal/register?locale=vi-VN")
            except Exception:
                print("[TIMEOUT] Đang F5 tải lại...")
                time.sleep(2)
                driver.refresh()
            
            wait = WebDriverWait(driver, 25)
            user_selector = "input[placeholder*='truy cập'], input[placeholder*='đăng nhập']"
            mail_selector = "input[placeholder*='Email'], input[placeholder*='email']"
            
            # Gõ sinh học chế độ normal để giữ an toàn tối đa
            print("[BROWSER] Đang điền Username...")
            human_type_custom(driver, wait, user_selector, garena_user, speed_mode="normal")
            check_and_wait_for_captcha(driver, "Sau khi nhập Username")

            print("[BROWSER] Đang điền Mật khẩu...")
            human_type_custom(driver, wait, "input[placeholder='Mật khẩu']", garena_pass, speed_mode="slow")
            check_and_wait_for_captcha(driver, "Sau khi nhập Mật khẩu")

            print("[BROWSER] Đang điền Nhập lại mật khẩu...")
            human_type_custom(driver, wait, "input[placeholder='Nhập lại mật khẩu']", garena_pass, speed_mode="slow")
            check_and_wait_for_captcha(driver, "Sau khi xác nhận Mật khẩu")

            print("[BROWSER] Đang điền Email...")
            human_type_custom(driver, wait, mail_selector, mail_manager.email, speed_mode="normal")
            check_and_wait_for_captcha(driver, "Sau khi nhập Email")
            
            time.sleep(random.uniform(0.5, 1.0))
            
            print("[BROWSER] Bấm nút 'Đăng Ký Ngay' để gọi Captcha / Gửi OTP...")
            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Đăng Ký Ngay')]")))
            move_mouse_humanlike(driver, submit_btn)
            ActionChains(driver).click(submit_btn).perform()
            
            captcha_detected = False
            for _ in range(30):
                if is_garena_captcha_visible(driver):
                    captcha_detected = True
                    break
                time.sleep(0.1)

            if captcha_detected:
                print("\n" + "!"*60)
                print("[MANUAL PAUSE] PHÁT HIỆN CAPTCHA SAU KHI SUBMIT!")
                dump_and_print_browser_logs(driver) # Bóc log mạng khi tạch ở bước submit cuối
                input("[WAIT] Giải xong nhấn ENTER tại đây để nhận OTP...")
            
            otp_code = mail_manager.fetch_otp_garena(timeout=90, delay=4)
            if not otp_code:
                print("\n[ALERT] Không tự động bắt được OTP.")
                otp_code = input(">> Điền mã OTP thủ công vào đây: ").strip()
            
            if not otp_code or len(otp_code) < 6:
                return False

            print("[BROWSER] Đang nhập mã OTP tự động...")
            otp_selector = "input[placeholder*='xác minh'], input[placeholder*='Mã'], input[placeholder*='code']"
            human_type_custom(driver, wait, otp_selector, otp_code, speed_mode="normal")
            time.sleep(random.uniform(0.5, 1.0))
            
            print("[BROWSER] Gửi lệnh chốt hạ tài khoản...")
            submit_btn_final = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Đăng Ký Ngay')]")))
            move_mouse_humanlike(driver, submit_btn_final)
            ActionChains(driver).click(submit_btn_final).perform()
            
            time.sleep(5)
            save_account_to_csv(garena_user, garena_pass, mail_manager.email)
            print(f"[SUCCESS] ĐĂNG KÝ THÀNH CÔNG TÀI KHOẢN: {garena_user}")
            return True

    except Exception as e:
        print(f"[ERROR] Phát sinh lỗi nghiêm trọng trong mẻ chạy: {e}")
        return False

def main_orchestrator(total_accounts_needed=3):
    print("================================================================")
    print(f"🚀 KHỞI CHẠY HỆ THỐNG ĐIỀU PHỐI SLL (XOAY IPHONE THỦ CÔNG)")
    print("================================================================")
    
    current_network_ip = get_public_ip()
    print(f"[INIT NETWORK] IP khởi tạo ban đầu: {current_network_ip}\n")
    
    successful_registrations = 0
    current_index = random.randint(100, 999)

    while successful_registrations < total_accounts_needed:
        print(f"\n💎 >>> ĐANG CHẠY MẺ THỨ: {successful_registrations + 1} / {total_accounts_needed} <<<")
        
        is_success = run_single_registration(account_index=current_index)
        
        if is_success:
            successful_registrations += 1
            print(f"✔️ Thành công: {successful_registrations}/{total_accounts_needed} tài khoản.")
            if successful_registrations < total_accounts_needed:
                current_network_ip = rotate_ip_and_wait(current_network_ip)
        else:
            print("❌ Mẻ đăng ký lỗi hoặc bị chặn Antibot.")
            current_network_ip = rotate_ip_and_wait(current_network_ip) # Ép xoay IP iPhone kể cả khi thất bại
            time.sleep(5)
            
        current_index += 1

if __name__ == "__main__":
    try:
        main_orchestrator(total_accounts_needed=3)
    except Exception as e:
        print("💥 LỖI CHÍ MẠNG!")
        traceback.print_exc()
        sys.exit(1)

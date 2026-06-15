import os
import sys
import time
import random
import string
import csv
import secrets
import numpy as np
import urllib.request  # Sử dụng thư viện chuẩn để check IP không lo crash
from datetime import datetime

# Ép hệ thống nhận diện đúng đường dẫn thư mục dự án
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
        # Timeout 4 giây để tránh treo luồng khi mạng đang ngắt kết nối
        with urllib.request.urlopen("https://api.ipify.org", timeout=4) as response:
            return response.read().decode('utf-8').strip()
    except Exception:
        return None

def rotate_ip_and_wait(old_ip: str):
    """Treo luồng nhắc người dùng xoay mạng 4G và tự động phát hiện IP mới."""
    print("\n" + "="*60)
    print("🔄 [NETWORK ROTATE] YÊU CẦU ĐỔI IP (4G LTE)")
    print(f" ➔ IP vừa sử dụng: {old_ip}")
    print(" 👉 HÀNH ĐỘNG: Hãy BẬT rồi TẮT Chế độ máy bay trên Điện thoại của bạn.")
    print("="*60 + "\n")
    
    while True:
        time.sleep(2.5)  # Nghỉ ngắn giữa các lần check mạng tránh spam API
        current_ip = get_public_ip()
        
        if current_ip is None:
            print("[NETWORK] Thiết bị đang ngắt kết nối hoặc đang cấp lại IP mạng di động...")
            continue
            
        if current_ip != old_ip:
            print(f"✅ [NETWORK] Đã nhận diện IP mới sạch hoàn toàn: {current_ip}")
            print("[NETWORK] Chờ 3 giây để đường truyền ổn định...")
            time.sleep(3)
            return current_ip
        else:
            print(f"[NETWORK] Vẫn phát hiện IP cũ ({current_ip}). Vui lòng gạt mạng di động...")

def gen_username_human(account_index=1) -> str:
    """Sinh Username theo format người dùng thật: Tên Việt + Ngày sinh ngẫu nhiên."""
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
    """Sinh mật khẩu độ dài biến thiên 10-14 ký tự chuẩn bảo mật."""
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

def calculate_bezier_points(start_point, end_point, num_points=30):
    x1, y1 = start_point
    x2, y2 = end_point
    
    control_offset_x = x2 * random.uniform(0.1, 0.3)
    control_offset_y = y2 * random.uniform(0.1, 0.3)
    
    cx1 = x1 + control_offset_x + random.randint(-20, 20)
    cy1 = y1 + control_offset_y + random.randint(-20, 20)
    cx2 = x2 - control_offset_x + random.randint(-20, 20)
    cy2 = y2 - control_offset_y + random.randint(-20, 20)
    
    points = []
    for t in np.linspace(0, 1, num_points):
        x = (1-t)**3 * x1 + 3*(1-t)**2 * t * cx1 + 3*(1-t) * t**2 * cx2 + t**3 * x2
        y = (1-t)**3 * y1 + 3*(1-t)**2 * t * cy1 + 3*(1-t) * t**2 * cy2 + t**3 * y2
        points.append((int(x), int(y)))
    return points

def move_mouse_humanlike(driver, target_element, num_points=None):
    try:
        actions = ActionChains(driver)
        random_offset_x = random.randint(-150, 150)
        random_offset_y = random.randint(-80, 80)
        
        actions.move_to_element_with_offset(target_element, random_offset_x, random_offset_y)
        actions.perform()
        time.sleep(random.uniform(0.1, 0.2))
        
        actions_final = ActionChains(driver)
        actions_final.move_to_element(target_element)
        actions_final.perform()
        
        time.sleep(random.uniform(0.15, 0.25))
    except Exception as e:
        print(f"[WARNING] Lỗi luồng chuột cứu hộ: {e}")
        try:
            ActionChains(driver).move_to_element(target_element).perform()
        except:
            pass

def is_garena_captcha_visible(driver) -> bool:
    try:
        captcha_selectors = [
            ".geetest_popup_box", "[class*='captcha']", "[id*='captcha']",
            ".universal-captcha-container", "iframe[src*='captcha']", ".geetest_widget"
        ]
        for selector in captcha_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                if el.is_displayed() and el.size['width'] > 0:
                    return True
    except:
        pass
    return False

def human_type_custom(driver, wait, element_selector, text, speed_mode="normal"):
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, element_selector)))
    move_mouse_humanlike(driver, element, num_points=random.randint(20, 35))
    
    ActionChains(driver).click(element).perform()
    time.sleep(random.uniform(0.18, 0.35))
    
    special_chars = "@#$!"
    for char in text:
        if speed_mode == "fast":
            delay_between_keys = random.uniform(0.020, 0.055)
        elif speed_mode == "slow":
            delay_between_keys = random.uniform(0.150, 0.280)
        else:
            delay_between_keys = random.uniform(0.070, 0.140)
            
        if char in special_chars:
            element.send_keys(char)
            time.sleep(delay_between_keys)
        else:
            key_hold_time = random.uniform(0.045, 0.090)
            try:
                ActionChains(driver).key_down(char).perform()
                time.sleep(key_hold_time)
                ActionChains(driver).key_up(char).perform()
                time.sleep(delay_between_keys)
            except Exception:
                element.send_keys(char)
                time.sleep(delay_between_keys)
                
    time.sleep(random.uniform(0.30, 0.55))

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
    """
    Hàm thực thi đăng ký một tài khoản duy nhất.
    """
    print(f"\n[PREPARE] Khởi tạo luồng đăng ký cho tài khoản index: #{account_index}")
    
    # 🌟 BƯỚC CỨU HỘ 1: Dọn dẹp ép đóng toàn bộ tiến trình rác của mẻ trước trên Linux Mint
   # 🌟 BƯỚC CỨU HỘ 1: Dọn dẹp tiến trình rác chạy thông minh trên cả Windows lẫn Linux
    import platform
    try:
        current_os = platform.system()
        if current_os == "Windows":
            os.system("taskkill /f /im chrome.exe >nul 2>&1")
            os.system("taskkill /f /im chromedriver.exe >nul 2>&1")
        else: # Linux / Mac
            os.system("pkill -9 -f chrome >/dev/null 2>&1")
            os.system("pkill -9 -f chromedriver >/dev/null 2>&1")
        print(f"[CLEANUP] Đã quét sạch tiến trình rác nền trên hệ điều hành: {current_os}")
    except Exception:
        pass
    mail_manager = MailTmManager()
    if not mail_manager.create_account():
        print("[CRITICAL] Khởi tạo tài khoản Mail.tm thất bại. Hủy mẻ chạy này!")
        return False
        
    garena_user = gen_username_human(account_index)
    garena_pass = gen_password_human()
    
    print("\n" + "="*50)
    print(f"[THÔNG TIN TÀI KHOẢN KHỞI TẠO NỀN]")
    print(f" ➔ Garena User : {garena_user}")
    print(f" ➔ Garena Pass : {garena_pass}")
    print(f" ➔ Mail.tm Box : {mail_manager.email}")
    print("="*50 + "\n")
    
    # 🌟 BƯỚC CỨU HỘ 2: Sử dụng os.path.lexists để quét và triệt tiêu Broken Symlink SingletonLock
    # 1. Lấy tên định danh từ Docker
    instance_name = os.getenv('INSTANCE_NAME', 'local_bot')
    profile_folder = os.path.abspath(os.path.join("outputs", f"chrome_profile_{instance_name}")) 
    profile_lock = os.path.join(profile_folder, "SingletonLock")
    if os.path.lexists(profile_lock):
        try:
            if os.path.islink(profile_lock):
                os.unlink(profile_lock)
            else:
                os.remove(profile_lock)
            print("[CLEANUP] Đã cưỡng chế bẻ gãy khóa ẩn SingletonLock thành công!")
        except Exception as e:
            print(f"[WARNING] Không thể dọn dẹp file Lock ẩn: {e}.")

    try:
        with stealth_driver_context(profile_folder,headless=False) as driver:
            # Phòng ngừa mạng di động chưa thông socket hoàn toàn bằng cách giới hạn timeout chờ tải
            driver.set_page_load_timeout(35)
            
            print("[BROWSER] Đang tải giao diện SSO Garena...")
            try:
                driver.get("https://sso.garena.com/universal/register?locale=vi-VN")
            except Exception:
                print("[TIMEOUT] Trang load quá lâu do kết nối 4G chưa ổn định. Đang F5 tải lại...")
                time.sleep(2)
                driver.refresh()
            
            wait = WebDriverWait(driver, 25)
            user_selector = "input[placeholder*='truy cập'], input[placeholder*='đăng nhập']"
            mail_selector = "input[placeholder*='Email'], input[placeholder*='email']"
            
            # 1. Điền Form sinh học
            human_type_custom(driver, wait, user_selector, garena_user, speed_mode="fast")
            human_type_custom(driver, wait, "input[placeholder='Mật khẩu']", garena_pass, speed_mode="slow")
            human_type_custom(driver, wait, "input[placeholder='Nhập lại mật khẩu']", garena_pass, speed_mode="slow")
            human_type_custom(driver, wait, mail_selector, mail_manager.email, speed_mode="normal")
            time.sleep(random.uniform(1.0, 1.5))
            
            # 2. Kích hoạt nút Đăng Ký Ngay phát đầu tiên
            print("[BROWSER] Bấm nút 'Đăng Ký Ngay' để gọi Captcha...")
            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Đăng Ký Ngay')]")))
            move_mouse_humanlike(driver, submit_btn, num_points=random.randint(20, 30))
            ActionChains(driver).click(submit_btn).perform()
            
            # 3. Giám sát lớp màng Captcha Geetest
            captcha_detected = False
            for _ in range(40):
                if is_garena_captcha_visible(driver):
                    print("🚨 [ALERT] PHÁT HIỆN HỘP THOẠI CAPTCHA GEETEST!")
                    captcha_detected = True
                    break
                time.sleep(0.1)

            if captcha_detected:
                print("\n" + "!"*60)
                print("[MANUAL PAUSE] VUI LÒNG DÙNG TAY GIẢI CAPTCHA TRÊN TRÌNH DUYỆT...")
                print("!"*60 + "\n")
                input("[WAIT] Sau khi giải xong và thấy thời gian gửi code đếm ngược, nhấn ENTER tại đây để chạy tiếp...")
            else:
                print("[MONITOR] Bỏ qua lớp kiểm tra Captcha (Môi trường/IP sạch).")

            # 4. Quét API hòm thư để bóc tách mã xác minh OTP
            otp_code = mail_manager.fetch_otp_garena(timeout=90, delay=4)
            if not otp_code:
                print("\n[ALERT] API Mail.tm không tự động bắt được OTP.")
                otp_code = input(">> Hãy xem thư thủ công và điền mã OTP 8 số vào đây: ").strip()
            
            if not otp_code or len(otp_code) < 6:
                print("[ERROR] Mã OTP không hợp lệ hoặc rỗng. Hủy tiến trình mẻ!")
                return False

            # 5. Tự điền OTP và chốt tài khoản
            print("[BROWSER] Đang nhập mã OTP tự động...")
            otp_selector = "input[placeholder*='xác minh'], input[placeholder*='Mã'], input[placeholder*='code']"
            human_type_custom(driver, wait, otp_selector, otp_code, speed_mode="normal")
            time.sleep(random.uniform(0.5, 1.0))
            
            print("[BROWSER] Gửi lệnh chốt hạ tài khoản lần cuối...")
            submit_btn_final = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Đăng Ký Ngay')]")))
            move_mouse_humanlike(driver, submit_btn_final, num_points=20)
            ActionChains(driver).click(submit_btn_final).perform()
            
            print("[BROWSER] Đang đợi đồng bộ dữ liệu hệ thống...")
            time.sleep(5)
            
            # Lưu log tài khoản
            save_account_to_csv(garena_user, garena_pass, mail_manager.email)
            print(f"[SUCCESS] ĐĂNG KÝ THÀNH CÔNG TÀI KHOẢN: {garena_user}")
            return True

    except Exception as e:
        print(f"[ERROR] Phát sinh lỗi nghiêm trọng trong mẻ chạy: {e}")
        return False

def main_orchestrator(total_accounts_needed=3):
    """Bộ điều phối chính kiểm soát vòng lặp SLL và dải xoay IP mạng."""
    print("================================================================")
    print(f"🚀 KHỞI CHẠY HỆ THỐNG ĐIỀU PHỐI SLL - MỤC TIÊU: {total_accounts_needed} ACCOUNTS")
    print("================================================================")
    
    current_network_ip = get_public_ip()
    print(f"[INIT NETWORK] IP khởi tạo ban đầu hệ thống ghi nhận: {current_network_ip}\n")
    
    successful_registrations = 0
    current_index = random.randint(10, 99)

    while successful_registrations < total_accounts_needed:
        print(f"\n💎 >>> ĐANG CHẠY MẺ THỨ: {successful_registrations + 1} / {total_accounts_needed} <<<")
        
        is_success = run_single_registration(account_index=current_index)
        
        if is_success:
            successful_registrations += 1
            print(f"✔️ Đã tích lũy thành công: {successful_registrations}/{total_accounts_needed} tài khoản.")
            
            if successful_registrations < total_accounts_needed:
                current_network_ip = rotate_ip_and_wait(current_network_ip)
        else:
            print("❌ Mẻ đăng ký lỗi hoặc bị ngắt quãng. Tiến hành thử lại...")
            print("[RETRY] Hệ thống tự động dọn dẹp để chuẩn bị chạy lại mẻ lỗi...")
            time.sleep(15)
            
        current_index += 1

    print("\n" + "="*60)
    print(f"🎉 [COMPLETED] HOÀN THÀNH TOÀN BỘ CHUỖI TẠO TẬP LỆNH SLL ({total_accounts_needed} ACCS)!")
    print("="*60)
#import thư viện traceback để debug 
if __name__ == "__main__":
    try:
        main_orchestrator(total_accounts_needed=3)
    except Exception as e:
        print("💥 HỆ THỐNG GẶP LỖI CHÍ MẠNG!")
        traceback.print_exc()
        import sys
        sys.exit(1)  # Ép Python phải thoát với mã lỗi 1, Docker mới chịu restart!

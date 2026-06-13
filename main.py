import os
import sys
import time
import random
import string
import csv
import secrets
import numpy as np
from datetime import datetime

# Ép hệ thống nhận diện đúng đường dẫn thư mục dự án
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from modules.browser.driver_config import stealth_driver_context
from modules.mail.mailtm_manager import MailTmManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

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
    """
    Hàm sinh mật khẩu bằng secrets chuẩn của bạn:
    Độ dài biến thiên 10-14 ký tự, có đủ Chữ hoa, Chữ thường, Số và Ký tự đặc biệt.
    """
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
    """
    Sinh đường cong Bézier bậc 3 dựa trên khoảng cách lệch (Offset) thực tế.
    Đảm bảo tổng các bước nhảy nhỏ cuối cùng khớp vừa khít với điểm đích.
    """
    # Vì di chuyển tương đối từ tâm phần tử mốc (0,0), điểm bắt đầu luôn là (0,0)
    # Điểm kết thúc (end_point) chính là khoảng cách delta_x, delta_y cần đi đến.
    x1, y1 = start_point
    x2, y2 = end_point
    
    # Tạo độ võng sinh học ngẫu nhiên
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
    """
    Fix triệt để lỗi xoay chuột đơ màn hình:
    Di chuyển chuột mượt mà qua 2 bước dứt khoát, không nhồi lệnh làm sập DevTools.
    """
    try:
        actions = ActionChains(driver)
        
        # Bước 1: Di chuyển chuột đến một vị trí ngẫu nhiên trên màn hình trước để tạo quỹ đạo (Gia tốc)
        # Giúp con trỏ chuột không bị bẫy "nhảy cóc" (Teleport) thẳng vào ô nhập liệu
        random_offset_x = random.randint(-150, 150)
        random_offset_y = random.randint(-80, 80)
        
        actions.move_to_element_with_offset(target_element, random_offset_x, random_offset_y)
        actions.perform()
        time.sleep(random.uniform(0.1, 0.2)) # Nghỉ ngắn ngẫu nhiên cho layout thở
        
        # Bước 2: Lướt mượt mà vào chính giữa tâm ô nhập liệu/nút bấm thực tế
        actions_final = ActionChains(driver)
        actions_final.move_to_element(target_element)
        actions_final.perform()
        
        time.sleep(random.uniform(0.15, 0.25))
    except Exception as e:
        print(f"[WARNING] Lỗi luồng chuột cứu hộ: {e}")
        # Nếu có biến cố, click trực tiếp bằng Selenium thông thường để thông luồng
        try:
            ActionChains(driver).move_to_element(target_element).perform()
        except:
            pass
def is_garena_captcha_visible(driver) -> bool:
    """ Quét DOM phát hiện màng bảo vệ captcha trượt ra """
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
    """ Gõ phím siêu phân rã: Tách biệt hoàn toàn KeyDown/KeyUp đè phím rải mili giây """
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, element_selector)))
    
    print(f"[MOUSE] Rê chuột Bézier đến ô nhập liệu: {element_selector}")
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

def run_demo_regger():
    print("[PREPARE] Đang khởi tạo luồng Reg Clone...")
    
    mail_manager = MailTmManager()
    if not mail_manager.create_account():
        print("[CRITICAL] Khởi tạo tài khoản Mail.tm thất bại. Dừng luồng!")
        return
        
    garena_user = gen_username_human(random.randint(1, 99))
    garena_pass = gen_password_human()
    
    print("\n" + "="*60)
    print("[THÔNG TIN KHỞI TẠO TỔNG THỂ]")
    print(f" -> Garena User: {garena_user}")
    print(f" -> Garena Pass: {garena_pass}")
    print(f" -> Email Ảo  : {mail_manager.email}")
    print(f" -> Pass Email : {mail_manager.password}")
    print("="*60 + "\n")

    with stealth_driver_context(headless=False) as driver:
        print("[BROWSER] Đang mở trang đăng ký Garena...")
        driver.get("https://sso.garena.com/universal/register?locale=vi-VN")
        
        wait = WebDriverWait(driver, 25)
        print("[BROWSER] Đang chờ Form xuất hiện...")
        
        user_selector = "input[placeholder*='truy cập'], input[placeholder*='đăng nhập']"
        mail_selector = "input[placeholder*='Email'], input[placeholder*='email']"
        
        try:
            # 1. Điền Username (Fast Mode)
            print("[BROWSER] Đang điền Username (Fast)...")
            human_type_custom(driver, wait, user_selector, garena_user, speed_mode="fast")
            
            # 2. Điền 2 ô Mật khẩu (Slow Mode)
            print("[BROWSER] Đang điền Mật khẩu...")
            human_type_custom(driver, wait, "input[placeholder='Mật khẩu']", garena_pass, speed_mode="slow")
            human_type_custom(driver, wait, "input[placeholder='Nhập lại mật khẩu']", garena_pass, speed_mode="slow")
            
            # 3. Điền Email (Normal Mode)
            print("[BROWSER] Đang điền Email (Normal)...")
            human_type_custom(driver, wait, mail_selector, mail_manager.email, speed_mode="normal")
            
            time.sleep(random.uniform(1.2, 1.8))
            
        except Exception as e:
            print("[ERROR] Lỗi điền Form ban đầu:", e)
            return
        
        # =================================================================
        # ĐẢO LUỒNG CHUẨN GARENA: BẤM "ĐĂNG KÝ NGAY" TRƯỚC ĐỂ THU HÚT CAPTCHA
        # =================================================================
        try:
            print("[BROWSER] Định vị nút 'Đăng Ký Ngay' màu đỏ...")
            # Sửa lỗi XPATH: Khóa chặt duy nhất nút Đăng Ký Ngay, loại bỏ hẳn tag NHẬN MÃ ở đây
            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Đăng Ký Ngay')]")))
            
            # ĐỒNG BỘ CHUỘT BÉZIER: Lướt chuột sinh học tới tâm nút bấm trước khi click
            print("[MOUSE] Rê chuột Bézier lướt mượt mà đến nút Đăng Ký...")
            move_mouse_humanlike(driver, submit_btn, num_points=random.randint(22, 35))
            
            # Thực hiện click vật lý giả lập tay người
            ActionChains(driver).click(submit_btn).perform()
            print("[BROWSER] Đã bấm nút 'Đăng Ký Ngay'! Chờ Captcha xuất hiện...")
        except Exception as e:
            print("[ERROR] Không kích hoạt được nút Đăng Ký Ngay:", e)
            return
        
        # =================================================================
        # HỆ THỐNG KIỂM SOÁT ĐÓNG BĂNG LUỒNG KHI PHÁT HIỆN CAPTCHA
        # =================================================================
        print("[MONITOR] Đang quét giao diện kiểm tra Captcha...")
        captcha_detected = False
        
        for _ in range(40):
            if is_garena_captcha_visible(driver):
                print("🚨 [ALERT] LAYOUT CAPTCHA ĐÃ HIỂN THỊ TRÊN MÀN HÌNH!")
                captcha_detected = True
                break
            time.sleep(0.1)

        if captcha_detected:
            print("\n" + "!"*60)
            print("[HÀNH ĐỘNG THỦ CÔNG - MANUAL PAUSE]")
            print("👉 Hãy cầm chuột giải quyết mượt mà lớp Captcha trên Chrome.")
            print("👉 Tuyệt đối không click nhảy cóc chuột vào thanh trượt.")
            print("!"*60 + "\n")
            
            input("[WAIT] Sau khi giải xong Captcha và thấy thời gian đếm ngược chạy, nhấn ENTER...")
        else:
            print("[MONITOR] Không phát hiện Captcha chặn, tiến thẳng sang bước quét OTP.")

        # 5. Cào mã OTP đổ về hộp thư Mail.tm
        otp_code = mail_manager.fetch_otp_garena(timeout=90, delay=4)
        
        if not otp_code:
            print("\n[ALERT] Hệ thống không tự bắt được mã qua API.")
            otp_code = input(">> Vui lòng xem mã trên giao diện Mail.tm rồi gõ vào đây: ").strip()
        
        if not otp_code or len(otp_code) < 6:
            print("[ERROR] Không có mã OTP hợp lệ. Hủy luồng!")
            return

        # 6. Tự động điền mã OTP vừa nhận
        print("[BROWSER] Đang tự động điền mã xác thực OTP...")
        try:
            otp_selector = "input[placeholder*='xác minh'], input[placeholder*='Mã'], input[placeholder*='code']"
            human_type_custom(driver, wait, otp_selector, otp_code, speed_mode="normal")
            time.sleep(random.uniform(0.6, 1.2))
            
            # 7. BẤM ĐĂNG KÝ LẦN CUỐI ĐỂ CHỐT TÀI KHOẢN
            print("[BROWSER] Bấm nút 'Đăng Ký Ngay' lần cuối để chốt hạ account...")
            submit_btn_final = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Đăng Ký Ngay')]")))
            
            # Rê chuột bọc lót Bézier nốt phát cuối cùng vào nút Đăng ký cho đồng bộ hành vi
            move_mouse_humanlike(driver, submit_btn_final, num_points=20)
            ActionChains(driver).click(submit_btn_final).perform()
            
            print("[BROWSER] Tạo tài khoản hoàn tất! Chờ đồng bộ...")
            time.sleep(5)
            
        except Exception as e:
            print("[ERROR] Lỗi ở bước nhập OTP hoặc click đăng ký cuối:", e)
            driver.save_screenshot("outputs/final_error.png")
        
        save_account_to_csv(garena_user, garena_pass, mail_manager.email)
        print(f"[SUCCESS] TIẾN TRÌNH HOÀN TẤT CHO TÀI KHOẢN: {garena_user}")

if __name__ == "__main__":
    run_demo_regger()
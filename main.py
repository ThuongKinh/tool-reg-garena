import os
import sys
import time
import random
import string
import csv
from datetime import datetime

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from modules.browser.driver_config import stealth_driver_context
from modules.mail.mailtm_manager import MailTmManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def generate_random_string(length=8):
    letters_and_digits = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

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
        
    garena_user = f"tgreg{generate_random_string(6)}"
    garena_pass = f"A1{generate_random_string(6)}!"
    
    print("\n" + "="*60)
    print("[THÔNG TIN KHỞI TẠO TỔNG THỂ]")
    print(f" -> Garena User: {garena_user}")
    print(f" -> Garena Pass: {garena_pass}")
    print(f" -> Email Ảo  : {mail_manager.email}")
    print(f" -> Pass Email : {mail_manager.password}")
    print("="*60 + "\n")

    with stealth_driver_context(headless=False) as driver:
        print("[BROWSER] Đang mở trang đăng ký Garena...")
        driver.get("https://sso.garena.com/ui/register?locale=vi-VN")
        
        wait = WebDriverWait(driver, 20)
        print("[BROWSER] Đang chờ Form xuất hiện...")
        
        user_selector = "input[placeholder*='truy cập'], input[placeholder*='đăng nhập']"
        mail_selector = "input[placeholder*='Email'], input[placeholder*='email']"
        
        try:
            # 1. Điền Username
            user_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, user_selector)))
            print("[BROWSER] Đã tìm thấy Form! Đang tự động điền dữ liệu...")
            user_input.send_keys(garena_user)
            
            # 2. Điền 2 ô Mật khẩu
            pass_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
            if len(pass_inputs) >= 2:
                pass_inputs[0].send_keys(garena_pass)
                pass_inputs[1].send_keys(garena_pass)
            else:
                if pass_inputs:
                    pass_inputs[0].send_keys(garena_pass)
            
            # 3. Điền Email để kích hoạt ô OTP trượt ra
            driver.find_element(By.CSS_SELECTOR, mail_selector).send_keys(mail_manager.email)
            time.sleep(1) # Chờ 1s cho animation trượt của Garena load xong
            
        except Exception as e:
            print("[ERROR] Lỗi điền Form ban đầu:", e)
            return
        
        # 4. Tìm và tự động bấm nút "NHẬN MÃ" kế bên ô OTP
        try:
            # Tìm thẻ chứa chữ NHẬN MÃ hoặc button bên cạnh ô input
            btn_selectors = [
                "//button[contains(text(), 'NHẬN MÃ')]",
                "//span[contains(text(), 'NHẬN MÃ')]",
                "//div[contains(text(), 'NHẬN MÃ')]",
                "//button[@type='button']"
            ]
            
            send_otp_btn = None
            for xpath in btn_selectors:
                try:
                    send_otp_btn = driver.find_element(By.XPATH, xpath)
                    if send_otp_btn.is_displayed():
                        break
                except:
                    continue
                    
            if send_otp_btn:
                print("[BROWSER] Đang tự động click nút 'NHẬN MÃ'...")
                send_otp_btn.click()
            else:
                print("[WARNING] Không tự click được nút 'NHẬN MÃ'. Vui lòng click tay.")
        except Exception as btn_err:
            print("[WARNING] Lỗi khi cố click nút nhận mã:", btn_err)
        
        print("\n" + "!"*60)
        print("[HÀNH ĐỘNG THỦ CÔNG - MANUAL PAUSE]")
        print("1. Hãy nhìn vào trình duyệt Chrome.")
        print("2. NẾU nút 'NHẬN MÃ' chưa được click, hãy tự bấm vào nó.")
        print("3. Giải quyết lớp Captcha hình ảnh của Garena xuất hiện ngay sau đó.")
        print("!"*60 + "\n")
        
        input("[WAIT] Sau khi giải Captcha xong và thấy thời gian đếm ngược chạy, nhấn ENTER để tool tự cào OTP...")

        # 5. Gọi hàm quét mail lấy mã 8 số
        otp_code = mail_manager.fetch_otp_garena(timeout=90, delay=4)
        
        if not otp_code:
            print("\n[ALERT] Hệ thống không tự bắt được mã qua API.")
            otp_code = input(">> Vui lòng xem mã OTP trực tiếp từ web mail.tm rồi gõ vào đây: ").strip()
        
        if not otp_code or len(otp_code) < 6:
            print("[ERROR] Không có mã OTP hợp lệ. Hủy luồng!")
            return

        # 6. Tự động điền mã OTP vào ô "Mã xác minh"
        print("[BROWSER] Đang điền mã xác thực OTP vào ô Mã xác minh...")
        try:
            # Dựa vào ảnh: ô này có placeholder là 'Mã xác minh'
            otp_selector = "input[placeholder*='xác minh'], input[placeholder*='Mã'], input[placeholder*='code']"
            otp_input = driver.find_element(By.CSS_SELECTOR, otp_selector)
            otp_input.send_keys(otp_code)
            print("[BROWSER] Đã điền xong mã xác minh!")
            time.sleep(1)
            
            # 7. Tự động bấm nút "Đăng Ký Ngay" màu đỏ dưới cùng để hoàn tất
            print("[BROWSER] Đang tự động bấm nút 'Đăng Ký Ngay' màu đỏ...")
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .btn-submit")
            # Nếu selector trên lỗi, fallback tìm theo text trên nút màu đỏ
            if not submit_btn:
                submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Đăng Ký Ngay')]")
                
            submit_btn.click()
            print("[BROWSER] Đã bấm nút đăng ký hoàn tất! Chờ 5 giây để lưu file...")
            time.sleep(5)
            
        except Exception as e:
            print("[ERROR] Lỗi ở bước điền OTP hoặc bấm Đăng ký cuối cùng:", e)
            print("[INFO] Đã chụp ảnh màn hình debug tại: outputs/final_error.png")
            driver.save_screenshot("outputs/final_error.png")
        
        save_account_to_csv(garena_user, garena_pass, mail_manager.email)
        print(f"[SUCCESS] TIẾN TRÌNH HOÀN TẤT CHO ACC: {garena_user}")

if __name__ == "__main__":
    run_demo_regger()

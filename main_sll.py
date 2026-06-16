import asyncio
import random
from playwright.async_api import async_playwright

# Nạp các module phẳng từ thư mục modules/ của cậu
from modules.browser_config import get_stealth_browser, create_clean_context
from modules.biometrics import human_type, move_mouse_humanlike
from modules.account_generator import generate_account_data
from modules.mail_manager import get_new_email, fetch_garena_otp
from modules.storage_manager import save_account_json

async def register_single_account():
    """
    Quy trình điều phối chuẩn: Điền form -> Đăng ký ngay -> Nhận mã -> Chờ giải Captcha -> Cào OTP.
    """
    # ──► BƯỚC 1: CHUẨN BỊ DATA CON NGƯỜI
    username, password = generate_account_data()
    email_address, jwt_token = await get_new_email()
    
    if not email_address or not jwt_token:
        print("[❌] Khởi tạo hòm thư tạm thời thất bại. Dừng luồng.")
        return
        
    print(f"\n========================================")
    print(f"[🚀 KHỞI CHẠY LUỒNG ĐĂNG KÝ NEW]")
    print(f"[*] USERNAME: {username}")
    print(f"[*] PASSWORD: {password}")
    print(f"[*] EMAIL   : {email_address}")
    print(f"========================================\n")

    # ──► BƯỚC 2: KHỞI TẠO HẠ TẦNG TRÌNH DUYỆT TÀNG HÌNH
    async with async_playwright() as p:
        browser = await get_stealth_browser(p, headless=False) # Hiện màn hình để cậu giải tay
        context = await create_clean_context(browser)
        page = await context.new_page()

        # Lắng nghe màng lọc mạng DataDome
        async def handle_response(response):
            if "garena.com" in response.url and response.status == 403:
                print("[⚠️ MẠNG] DataDome 403 phát hiện hệ thống bảo mật kích hoạt!")

        page.on("response", handle_response)

        # ──► BƯỚC 3: ĐIỀU HƯỚNG VÀ ĐIỀN FORM SINH HỌC
        print("[*] Đang tiến vào trang đăng ký Garena...")
        await page.goto("https://sso.garena.com/universal/register?locale=vi-VN")
        
        # 1. Điền Tên truy cập (Fuzzy Selector *= chống đổi placeholder)
        user_selector = "input[placeholder*='truy cập']"
        await page.wait_for_selector(user_selector, timeout=10000)
        await human_type(page, user_selector, username, speed_mode="normal")
        await asyncio.sleep(random.uniform(0.3, 0.6))
        
        # 2. Điền Mật khẩu (Chế độ gõ slow cẩn thận)
        pass_selector = "input[placeholder='Mật khẩu']"
        await human_type(page, pass_selector, password, speed_mode="slow")
        await asyncio.sleep(random.uniform(0.3, 0.6))
        
        # 3. Điền Nhập lại mật khẩu
        confirm_pass_selector = "input[placeholder='Nhập lại mật khẩu']"
        await human_type(page, confirm_pass_selector, password, speed_mode="slow")
        await asyncio.sleep(random.uniform(0.4, 0.8))
        
        # 4. Điền Email
        email_selector = "input[placeholder*='mail'], input[placeholder*='Mail']"
        await human_type(page, email_selector, email_address, speed_mode="normal")
        await asyncio.sleep(random.uniform(0.5, 1.0))

        # ──► BƯỚC 4:ẤN "ĐĂNG KÝ NGAY" LẦN 1 ĐỂ MỞ LAYER TIẾP THEO
        print("[*] Thao tác chuột sinh học chuẩn bị click 'Đăng Ký Ngay'...")
        submit_btn_selector = 'button:has-text("Đăng Ký Ngay")'
        await page.wait_for_selector(submit_btn_selector, timeout=5000)
        await move_mouse_humanlike(page, submit_btn_selector) # Rê chuột lệch tâm chống bot
        await page.locator(submit_btn_selector).click()
        await asyncio.sleep(random.uniform(1.0, 1.5))

        # ──► BƯỚC 5: ẤN NÚT "NHẬN MÃ" / "GỬI MÃ XÁC THỰC"
        # Thử tìm và click nút nhận mã nếu Garena yêu cầu xác thực email riêng biệt
        print("[*] Dò tìm và click kích hoạt nút gửi mã OTP...")
        get_code_selector = 'button:has-text("Mã"), button:has-text("Nhận"), button:has-text("Gửi")'
        try:
            # Chờ ngắn nếu nút xuất hiện muộn do hiệu ứng modal popup
            await page.wait_for_selector(get_code_selector, timeout=3000)
            await move_mouse_humanlike(page, get_code_selector)
            await page.locator(get_code_selector).click()
            print("[+] Đã kích hoạt lệnh 'Nhận mã' thành công.")
        except Exception:
            print("[ℹ️ Info] Không thấy nút 'Nhận mã' tách riêng, có thể Captcha đã tự nổ trực tiếp.")

        # ──► BƯỚC 6: TẠM DỪNG LUỒNG ĐỂ CẬU TỰ GIẢI CAPTCHA BẰNG TAY
        print("\n" + "!"*60)
        print("[📢 MANUAL PAUSE] PHÁT HIỆN CAPTCHA GEETEST XUẤT HIỆN!")
        print(" 👉 HÀNH ĐỘNG: Cậu tự kéo slider giải captcha trực tiếp trên màn hình Chrome.")
        print(" 👉 LƯU Ý: Sau khi giải xong, đợi hệ thống web báo gửi mã thành công...")
        print("!"*60 + "\n")
        
        # Treo luồng Python tại Terminal, đợi cậu giải xong nhấn Enter mới chạy tiếp
        input("[WAIT] Giải captcha xong xuôi thì nhấn phím ENTER tại đây để bot cào OTP...")

        # ──► BƯỚC 7: TỰ ĐỘNG CÀO OTP TỪ MODULE MAIL BẢN VÁ
        print("[*] Bắt đầu gọi module quét hòm thư ngầm...")
        otp_code = await fetch_garena_otp(email_address, jwt_token, timeout=90)
        
        if not otp_code:
            print("[❌] Thất bại: Không lấy được OTP qua API. Hủy luồng giải phóng RAM.")
            await context.close()
            await browser.close()
            return

        # ──► BƯỚC 8: NHẬP OTP TỰ ĐỘNG QUA PHÂN PHỐI GAUSSIAN
        otp_input_selector = "input[placeholder*='xác minh'], input[placeholder*='Mã'], input[placeholder*='code']"
        await page.wait_for_selector(otp_input_selector, timeout=5000)
        await human_type(page, otp_input_selector, otp_code, speed_mode="normal")
        await asyncio.sleep(random.uniform(0.6, 1.2))
        
        # ──► BƯỚC 9: ẤN ĐĂNG KÝ NGAY LẦN NỮA ĐỂ CHỐT HẠ TÀI KHOẢN
        print("[*] Đóng hòm tài khoản: Click nút 'Đăng Ký Ngay' chặng cuối...")
        await move_mouse_humanlike(page, submit_btn_selector)
        await page.locator(submit_btn_selector).click()
        
        # Đợi 5 giây để Garena xử lý lưu database tầng server
        await page.wait_for_timeout(5000)
        
        # ──► BƯỚC 10: GHI NHẬN THÀNH QUẢ SANG FILE JSON BẢO TOÀN CẤU TRÚC
        save_account_json(username, password, email_address)
        
        # Giải phóng tài nguyên hệ thống Linux
        print(f"[🎉 HOÀN THÀNH LUỒNG] Tài khoản {username} đã đăng ký và lưu trữ sạch sẽ!")
        await context.close()
        await browser.close()

async def main():
    await register_single_account()

if __name__ == "__main__":
    asyncio.run(main())

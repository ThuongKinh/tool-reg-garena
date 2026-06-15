import time
from modules.mail.mail_engine import get_garena_otp

def check_mail_module():
    # 1. Điền Token và địa chỉ Email thật mà cậu đã tạo được từ mail.tm ở đây để test
    # (Nếu chưa có luồng tự động, cậu có thể lấy token của 1 acc mail.tm bất kỳ tạo bằng tay)
    TEST_MAIL_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3ODEyNTU5MTYsInJvbGVzIjpbIlJPTEVfVVNFUiJdLCJhZGRyZXNzIjoiZ3JuX2U2ZnVrd3htQHdlYi1saWJyYXJ5Lm5ldCIsImlkIjoiNmEyYmNlZWIyZjhiNmY5YjI5MGRhMzIyIiwibWVyY3VyZSI6eyJzdWJzY3JpYmUiOlsiL2FjY291bnRzLzZhMmJjZWViMmY4YjZmOWIyOTBkYTMyMiJdfX0.CDEw-UPUs1JNfgwQd-x11DcFitY-UYI9RPPhsKtdavl8oK6EXroITX_2XeFCxKitdGSUAvPUDgh5v0OTmI5F5Q"
    TEST_MAIL_ADDRESS = "grn_e6fukwxm@web-library.net"
    
    print(f"[START] Bắt đầu test hàm cào OTP với Email: {TEST_MAIL_ADDRESS}")
    print("[HƯỚNG DẪN] Sau khi dòng chữ 'Đang chờ thư OTP...' hiện ra:")
    print("-> Cậu hãy dùng điện thoại hoặc một trình duyệt khác, gửi một email ĐẾN địa chỉ mail trên.")
    print("-> Tiêu đề (Subject) hoặc Nội dung email BẮT BUỘC phải chứa chữ: 'Garena'")
    print("-> Trong nội dung email, hãy gõ đại một mã 6 số (Ví dụ: 456123).")
    print("-" * 60)

    # 2. Gọi hàm check của cậu với thời gian chờ tối đa là 90 giây để cậu kịp gửi thư test
    otp_result = get_garena_otp(mail_token=TEST_MAIL_TOKEN, max_wait_sec=90)

    # 3. Đánh giá kết quả
    print("-" * 60)
    if otp_result:
        print(f"[SUCCESS] Test THÀNH CÔNG! Hàm của cậu đã bốc tách chính xác mã OTP: {otp_result}")
    else:
        print("[FAIL] Test THẤT BẠI. Không tìm thấy OTP hoặc quá thời gian chờ.")

if __name__ == "__main__":
    check_mail_module()

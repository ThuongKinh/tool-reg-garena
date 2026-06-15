import json
import csv
import time
import sys

print("=== SCRIPT STARTED ===")

try:
    from mailtm_manager import MailTmManager
    print(" Import module MailTmManager thành công!")
except Exception as e:
    print(f"❌ Lỗi Import: Không tìm thấy file hoặc code bên trong 'mail_tm_manager.py' lỗi. Chi tiết: {e}")
    sys.exit(1)

def test_and_export_mail_list(loops=3):
    account_list = []
    print(f"🚀 BẮT ĐẦU CHẠY THỬ NGHIỆM MODULE (Vòng lặp: {loops} lần)")
    print("="*60)

    for i in range(1, loops + 1):
        print(f"\n[Luồng #{i}] Đang khởi tạo và yêu cầu cấp mail...")
        mail_engine = MailTmManager()
        success = mail_engine.create_account()
        
        if success:
            print(f" ✅ Tạo thành công: {mail_engine.email}")
            account_data = {
                "id": i,
                "email": mail_engine.email,
                "password": mail_engine.password,
                "token": mail_engine.token,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            account_list.append(account_data)
        else:
            print(f" ❌ Thất bại ở vòng lặp thứ {i}")
            
        if i < loops:
            rest_time = 7
            print(f"⏳ Nghỉ {rest_time} giây tránh Rate Limit...")
            time.sleep(rest_time)

    print("\n" + "="*60)
    print(f"📊 Thu thập hoàn tất. Tổng số mail tạo được: {len(account_list)}/{loops}")
    
    if not account_list:
        return

    # Xuất JSON
    with open("mail_test_output.json", "w", encoding="utf-8") as json_file:
        json.dump(account_list, json_file, indent=4, ensure_ascii=False)
    print("💾 Đã xuất file JSON: mail_test_output.json")

    # Xuất CSV
    csv_headers = ["id", "email", "password", "token", "created_at"]
    with open("mail_test_output.csv", "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
        writer.writeheader()
        writer.writerows(account_list)
    print("💾 Đã xuất file CSV: mail_test_output.csv")

if __name__ == "__main__":
    test_and_export_mail_list(loops=3)

import asyncio
import httpx
import re
import random
import string

MAIL_TM_API = "https://api.mail.tm"

def _random_string(length=8):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

async def get_new_email():
    """Cấp phát email mới từ Mail.tm (Giữ nguyên)"""
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            domain_res = await client.get(f"{MAIL_TM_API}/domains")
            domain_res.raise_for_status()
            domains = domain_res.json().get("hydra:member", [])
            if not domains:
                return None, None
            target_domain = domains[0].get("domain")
            
            username = f"grn_{_random_string(6)}"
            email_address = f"{username}@{target_domain}"
            password = _random_string(10)
            
            payload = {"address": email_address, "password": password}
            create_res = await client.post(f"{MAIL_TM_API}/accounts", json=payload)
            create_res.raise_for_status()
            
            token_res = await client.post(f"{MAIL_TM_API}/token", json=payload)
            token_res.raise_for_status()
            jwt_token = token_res.json().get("token")
            
            return email_address, jwt_token
        except Exception as e:
            print(f"[❌ Mail Lỗi] {e}")
            return None, None

async def fetch_garena_otp(email_address, jwt_token, timeout=60):
    """
    HÀM CÀO OTP BẢN VÁ: Ép kiểu dữ liệu nghiêm ngặt, chống bẫy cấu trúc list từ API.
    """
    if not jwt_token:
        print("[❌ Mail] Thiếu Token xác thực.")
        return None

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    print(f"[*] Bắt đầu cào hộp thư {email_address} (Timeout: {timeout}s)...")
    start_time = asyncio.get_event_loop().time()
    
    async with httpx.AsyncClient(timeout=10) as client:
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            try:
                msg_res = await client.get(f"{MAIL_TM_API}/messages", headers=headers)
                msg_res.raise_for_status()
                messages = msg_res.json().get("hydra:member", [])
                
                for msg in messages:
                    sender = msg.get("from", {}).get("address", "").lower()
                    subject = msg.get("subject", "").lower()
                    
                    if "garena" in sender or "garena" in subject:
                        print(f"[+ Mail] Phát hiện thư Garena. Đang bóc tách tầng sâu...")
                        
                        msg_id = msg.get("id")
                        detail_res = await client.get(f"{MAIL_TM_API}/messages/{msg_id}", headers=headers)
                        detail_data = detail_res.json()
                        
                        # 🛠️ KHỬ LỖI TYPEERROR: Kiểm tra và ép toàn bộ sang dạng chuỗi phẳng
                        text_part = detail_data.get("text", "")
                        html_part = detail_data.get("html", "")
                        intro_part = msg.get("intro", "")
                        
                        text_str = " ".join(text_part) if isinstance(text_part, list) else str(text_part)
                        html_str = " ".join(html_part) if isinstance(html_part, list) else str(html_part)
                        intro_str = " ".join(intro_part) if isinstance(intro_part, list) else str(intro_part)
                        
                        # Gom sạch vào một biến chuỗi duy nhất để quét
                        raw_content = f"{text_str} {html_str} {intro_str}"
                        
                        # Tiến hành quét lấy cụm 6-8 số
                        all_numbers = re.findall(r'\d{6,8}', raw_content)
                        
                        # Loại bỏ số năm nếu trùng hợp xuất hiện trong mail
                        valid_numbers = [num for num in all_numbers if num != "2026"]
                        
                        if valid_numbers:
                            otp_code = valid_numbers[0]
                            print(f"[🎉 OTP] Đã bóc thành công mã OTP Garena: {otp_code}")
                            return otp_code
                            
                        print(f"[⚠️ Mail] Tìm thấy thư nhưng Regex tạch. Đoạn đầu thư: {raw_content[:100]}")
                        
            except Exception as e:
                print(f"[⚠️ Mail Cảnh báo] {e}")
            
            await asyncio.sleep(3)
            
        print("[❌] Hết thời gian chờ. Không bắt được OTP.")
        return None


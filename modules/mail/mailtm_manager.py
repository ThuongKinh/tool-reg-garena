import requests
import time
import random
import string
import re
from html.parser import HTMLParser

class _StripTags(HTMLParser):
    """Strip toàn bộ HTML tag, chỉ giữ text thô."""
    def __init__(self):
        super().__init__()
        self._parts = []

    def handle_data(self, data):
        self._parts.append(data)

    def get_text(self):
        return " ".join(self._parts)


class MailTmManager:
    def __init__(self):
        self.base_url = "https://api.mail.tm"
        self.domain = self._get_active_domain()
        self.email = None
        self.password = None
        self.token = None
        self.account_id = None

    def _get_active_domain(self):
        try:
            res = requests.get(f"{self.base_url}/domains", timeout=10)
            if res.status_code == 200:
                domains = res.json().get('hydra:member', [])
                if domains:
                    return domains[0]['domain']
            raise Exception("Không thể lấy danh sách domain")
        except Exception as e:
            print(f"❌ Lỗi kết nối Mail.tm: {e}")
            return None

    def _generate_random_string(self, length=10):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def create_account(self):
        if not self.domain:
            return False
        username = f"grn_{self._generate_random_string(8)}"
        self.email = f"{username}@{self.domain}"
        self.password = self._generate_random_string(12)
        
        payload = {"address": self.email, "password": self.password}
        res = requests.post(f"{self.base_url}/accounts", json=payload, timeout=10)
        if res.status_code == 201:
            self.account_id = res.json().get('id')
            return self.get_token()
        return False

    def get_token(self):
        payload = {"address": self.email, "password": self.password}
        res = requests.post(f"{self.base_url}/token", json=payload, timeout=10)
        if res.status_code == 200:
            self.token = res.json().get('token')
            return True
        return False

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def _strip_html(self, html_content) -> str:
        if isinstance(html_content, list):
            html_content = " ".join([str(x) for x in html_content])
        elif not html_content:
            html_content = ""
        parser = _StripTags()
        parser.feed(str(html_content))
        return parser.get_text()

    def fetch_otp_garena(self, timeout=90, delay=4):
        """
        Truy cập hộp thư Mail.tm, lọc thư từ Garena, bóc tách OTP 6-8 số sạch.
        """
        print(f"⏳ Đang gọi API Mail.tm để quét hộp thư của {self.email}...")
        # Bao lô từ 6 đến 8 số để húp trọn vẹn mã xác minh dạng 09768605
        OTP_PATTERN = re.compile(r'\b\d{6,8}\b')
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                res = requests.get(f"{self.base_url}/messages", headers=self.get_headers(), timeout=10)
                if res.status_code == 200:
                    messages = res.json().get('hydra:member', [])
                    
                    # reversed() để luôn đọc thư mới nhất vừa đổ về trước, loại bỏ thư rác hệ thống
                    for msg in reversed(messages):
                        sender = msg.get('from', {}).get('address', '').lower()
                        subject = msg.get('subject', '').lower()
                        
                        # Điều kiện quét: Thư phải liên quan tới Garena hoặc verification
                        if "garena" in sender or "verification" in subject or "garena" in subject or "mã" in subject:
                            msg_id = msg.get('id')
                            
                            # Tải chi tiết nội dung bức thư Garena
                            detail_res = requests.get(f"{self.base_url}/messages/{msg_id}", headers=self.get_headers(), timeout=10)
                            if detail_res.status_code == 200:
                                detail = detail_res.json()
                                
                                raw_text = str(detail.get("text") or "").strip()
                                html_text = self._strip_html(detail.get("html") or "").strip()
                                content = raw_text if raw_text else html_text
                                
                                if not content:
                                    continue
                                    
                                # Quét tìm mã OTP
                                match = OTP_PATTERN.search(content)
                                if match:
                                    otp = match.group(0)
                                    print(f"🎉 [API SUCCESS] Đã tìm thấy mã OTP Garena: {otp}")
                                    return otp
            except Exception as e:
                pass
                
            time.sleep(delay)
            
        print("❌ Quá thời gian chờ (Timeout) — Không nhận được thư OTP hợp lệ từ Garena.")
        return None

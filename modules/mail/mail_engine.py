import requests
import time
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


def _strip_html(html_content) -> str:
    """Làm sạch HTML, ép kiểu đầu vào an toàn."""
    if isinstance(html_content, list):
        html_content = " ".join([str(x) for x in html_content])
    elif not html_content:
        html_content = ""
        
    parser = _StripTags()
    parser.feed(str(html_content))
    return parser.get_text()


def get_garena_otp(mail_token: str, max_wait_sec: int = 60) -> str | None:
    """
    Poll mail.tm để lấy mã OTP 6 số từ Garena.
    Trả về OTP string nếu thành công, None nếu timeout.
    """
    headers = {
        "Authorization": f"Bearer {mail_token}",
        "Content-Type": "application/json"
    }

    OTP_PATTERN = re.compile(r'\b\d{6}\b')
    start_time = time.time()
    print("[INFO] Đang chờ thư OTP từ Garena...")

    while time.time() - start_time < max_wait_sec:
        try:
            # 1. Lấy danh sách thư
            resp = requests.get(
                "https://api.mail.tm/messages",
                headers=headers,
                timeout=10
            )

            if resp.status_code != 200:
                print(f"[WARNING] API trả về {resp.status_code}, thử lại...")
            else:
                messages = resp.json().get("hydra:member", [])

                # reversed để luôn check các thư mới nhất trước
                for msg in reversed(messages):
                    sender  = msg.get("from", {}).get("address", "").lower()
                    subject = msg.get("subject", "").lower()

                    if "garena" not in sender and "garena" not in subject:
                        continue

                    # 2. Lấy nội dung chi tiết
                    detail_resp = requests.get(
                        f"https://api.mail.tm/messages/{msg['id']}",
                        headers=headers,
                        timeout=10
                    )

                    if detail_resp.status_code != 200:
                        print(f"[WARNING] Không lấy được nội dung thư {msg['id']}")
                        continue

                    detail = detail_resp.json()

                    # 3. Ép kiểu nghiêm ngặt và xử lý khoảng trắng (Strip)
                    raw_text  = str(detail.get("text") or "").strip()
                    html_text = _strip_html(detail.get("html") or "").strip()
                    
                    # Nếu có text thô thật sự thì dùng, không thì fallback sang html đã strip
                    content = raw_text if raw_text else html_text

                    if not content:
                        continue

                    # 4. Tìm OTP bằng Regex trên chuỗi chuân hóa
                    match = OTP_PATTERN.search(content)
                    if match:
                        otp = match.group(0)
                        print(f"[SUCCESS] OTP Garena: {otp}")
                        return otp

        except requests.RequestException as e:
            print(f"[WARNING] Lỗi mạng: {e}")
        except Exception as e:
            print(f"[WARNING] Lỗi hệ thống: {e}")

        time.sleep(3)

    print("[ERROR] Timeout — không nhận được OTP.")
    return None

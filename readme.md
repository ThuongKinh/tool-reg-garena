# Garena Account Regger - Project Architecture

## I. Tổng quan
1. **Mục tiêu:** Xây dựng hệ thống tự động hóa reg acc Garena số lượng lớn (SLL).
2. **Triết lý phát triển:** Phát triển phiên bản DEMO rút gọn (dùng các tài nguyên miễn phí, có hạn, kết hợp với thủ công) để kiểm tra logic dòng chảy (flow). Sau đó nâng cấp/thay thế những modules lõi để tối ưu hóa hiệu suất và chi phí khi chạy SLL.

---

## II. Ma trận phát triển: DEMO vs PRODUCTION SLL

| Tên Module | DEMO | PRODUCTION SLL | Chi tiết |
| :--- | :--- | :--- | :--- |
| **Browser** | Selenium Stealth | Playwright Async | Selenium tốn RAM, Playwright tối ưu đa luồng ngầm |
| **Mail Engine** | API Mail 10p (Mail.tm) | Domain Catch-All + IMAP | Tránh domain ảo bị Garena đưa vào blacklist |
| **Network** | Mạng LAN / Dcom 4G | Proxy Xoay IPv4 | Tránh trùng IP dẫn đến block đăng ký |
| **Captcha** | Giải bằng tay | API 3rd (AnyCaptcha...) | Tự động hóa 100% khi chạy ngầm |  
| **Data Storage** | Ghi thẳng vào file phẳng (.txt/.csv) | Kết nối Database (SQL) | Tránh xung đột khóa (Lock) khi ghi đa luồng. Quản lý trạng thái acc tốt hơn. |


---

## III. Xây dựng Core (Demo)
1. **Mục tiêu:** Tạo được tài khoản thành công bằng tay kết hợp tool.
2. **Tiến độ chi tiết:**
   - [x] **Task 1: Module Browser** -> Dùng Selenium + `selenium-stealth` để tránh bị phát hiện, tự động trỏ tới trang đăng ký Garena.
   - [x] **Task 2: Module Mail Demo** -> Sử dụng HTTP requests gọi API `mail.tm` để lấy 1 mail ảo ngẫu nhiên, điền vào form.
   - [x] **Task 3: Cơ chế dừng (Manual Pause)** -> Code dừng lại tầm 15 - 30 giây để người dùng tự tay giải Captcha và nhấn nút nhận mã.
   - [x] **Task 4: Module Mail OTP** -> Gọi API kiểm tra hòm thư ảo, cào mã OTP 6 số và tự động điền vào Garena.
   - [x] **Task 5: Module Storage** -> Xuất thông tin tài khoản đăng ký thành công ra file cục bộ.
   - [ ] **Task 6: Network** -> Setup Network, tránh bị ban IP.

---

## IV. Nâng cấp Core (SLL)
1. **Mục tiêu:** Cắt bỏ hoàn toàn phụ thuộc bên ngoài và tự động hóa 100%.
2. **Tiến độ chi tiết:**
   - [ ] **Task 1: Thay thế Mail** -> Mua domain riêng, cấu hình Catch-all. Viết hàm Python kết nối IMAP đọc OTP từ mail tổng.
   - [ ] **Task 2: Thay thế Captcha** -> Tích hợp API giải Captcha bên thứ 3 (AnyCaptcha...), nhận tọa độ/token trả về để điền tự động.
   - [ ] **Task 3: Thay thế Network** -> Cấu hình Proxy xoay đi kèm trực tiếp với từng Browser Context.
   - [ ] **Task 4: Tối ưu hóa** -> Chuyển dịch cấu trúc sang OOP kết hợp Đa luồng (`asyncio` / `threading`).

## V. Thiết lập Domain & Kịch bản Ngâm Traffic (Production SLL)

Khi vận hành hệ thống số lượng lớn, việc sử dụng các hòm thư tạm thời (Temp Mail) sẽ bị hệ thống kiểm soát của Garena chặn đứng do kích hoạt cơ chế phát hiện bất thường (Anomaly Detection). Để giải quyết triệt để rủi ro "bay domain" và tối ưu hóa chi phí vận hành, hệ thống bắt buộc phải triển khai hạ tầng Domain riêng độc lập.

### 1. Quy trình tự động hóa thiết lập Tên miền (Domain Onboarding Lifecycle)
#[Danh sách Tên miền mới mua]
│
▼
┌────────────────────────────────────────────────────────┐
| TOOL 1: Cloudflare API Automation                      │
├────────────────────────────────────────────────────────┤
│ 1. Tự động thêm Site vào tài khoản Cloudflare          │
│ 2. Kích hoạt tính năng Email Routing (Catch-All)       │
│ 3. Auto cấu hình bản ghi DNS (MX, SPF, DKIM, DMARC)   │
└──────────────────────────┬─────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────┐
│ TOOL 2: Cloudflare Pages Deploy                        │
├────────────────────────────────────────────────────────┤
│ 1. Đẩy mã nguồn Landing Page tĩnh lên Cloudflare Pages │
│ 2. Xây dựng bộ nhận diện một website doanh nghiệp thật │
└──────────────────────────┬─────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────┐
│ TOOL 3: Playwright Traffic Generator                   │
├────────────────────────────────────────────────────────┤
│ 1. Chạy bot ngầm mô phỏng hành vi người dùng thật      │
│ 2. Duy trì lưu lượng truy cập ảo liên tục từ 3 - 5 ngày│
└──────────────────────────┬─────────────────────────────┘
│
▼
[Hệ thống Domain Sạch & Uy Tín] ──► Cung cấp đầu vào an toàn cho Tool Reg Garena

## 2. Tiêu chuẩn cấu hình xác thực Mail Server (Vượt màng lọc Garena)
Nếu domain chỉ cấu hình mỗi bản ghi MX để nhận thư mà thiếu các bản ghi chứng thực danh tính, hệ thống bảo mật của Garena sẽ phân loại đây là Mail Server lậu và từ chối gửi OTP. Các bản ghi bắt buộc phải nạp qua Cloudflare DNS bao gồm:
* **MX Records:** Trỏ về máy chủ Email Routing của Cloudflare để bắt toàn bộ các ký tự email ngẫu nhiên đứng trước (Cơ chế Catch-All, ví dụ: `grn_xxxx@yourdomain.xyz`).
* **SPF (Sender Policy Framework):** Khai báo TXT Record `v=spf1 include:_spf.mx.cloudflare.net ~all` nhằm xác thực quyền hạn phân phối thư của hệ thống.
* **DMARC (Domain-based Message Authentication):** Thêm bản ghi TXT với Host: `_dmarc` và Value: `v=DMARC1; p=none;` để thiết lập chính sách bảo mật nâng cao, gia tăng tối đa điểm uy tín (Reputation) cho domain mới tạo.

### 3. Chiến lược kiểm soát lưu lượng & Tránh Blacklist (Traffic Shaper & Rate Limiting)
Để duy trì tuổi thọ cho domain và tránh việc toàn bộ tên miền gốc bị đưa vào danh sách đen, lưu lượng nhận mail xác thực sẽ được điều phối nghiêm ngặt theo mô hình hình thang dựa trên độ tuổi tên miền (Domain Age):
* **Giai đoạn Thử nghiệm (Ngày 4 - 5):** Chỉ phân phối tối đa từ 10 - 20 tài khoản/ngày trên mỗi tên miền nhằm mục đích thăm dò màng lọc.
* **Giai đoạn Tăng trưởng (Ngày 6 trở đi):** Nâng dần hạn mức đăng ký theo thang cấp độ (50 ➡️ 100 ➡️ 500 tài khoản/ngày) dựa trên tỷ lệ nhận OTP thành công.
* **Cơ chế cô lập rủi ro bằng Subdomain:** Thiết kế module tự động chia nhỏ và phân phối tải thông qua các Subdomain con (`s1.yourdomain.xyz`, `s2.yourdomain.xyz`) trên Cloudflare. Khi có biến động block, hệ thống chỉ bị ảnh hưởng ở phân vùng phân phối đó, bảo vệ an toàn cho Apex Domain gốc không bị thâm hụt.

### 4. Tối ưu hóa kiểm tra Logic điều phối Code (Quản lý rủi ro chi phí)
Để tránh tình trạng thâm hụt ngân sách khi chạy thực tế do lỗi mạng hoặc proxy chết giữa chừng, luồng code bắt buộc phải tuân thủ nghiêm ngặt cơ chế kiểm tra chéo:
* **Hàm check trạng thái Proxy trước luồng:** Luôn gọi một request ngắn (timeout 3 - 5s) để xác thực tính ổn định của IP Proxy trước khi kích hoạt API giải Captcha bên thứ ba nhằm tối ưu chi phí, loại bỏ hoàn toàn việc mất tiền oan do proxy sập.
* **Timeout cào OTP đồng bộ:** Do cơ chế Cloudflare Email Routing mất từ 5 - 10 giây để forward thư về hòm thư tổng, vòng lặp cào mail qua kết nối IMAP phải được thiết lập thời gian chờ (Timeout) tối thiểu là 45 - 60 giây để đảm bảo không bị đóng tiến trình vội vàng, gây mất trắng chi phí giải captcha của lượt chạy đó.

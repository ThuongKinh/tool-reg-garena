# Garena Account Regger - Project Architecture

## I. Tổng quan
1. **Mục tiêu:** Xây dựng hệ thống tự động hóa reg acc Garena số lượng lớn (SLL).
2. **Triết lý phát triển:** Phát triển phiên bản DEMO rút gọn (dùng các tài nguyên miễn phí, có hạn, kết hợp với thủ công) để kiểm tra logic dòng chảy (flow). Sau đó nâng cấp/thay thế những modules lõi để tối ưu hóa hiệu suất và chi phí khi chạy SLL.

---

## II. Ma trận phát triển: DEMO vs PRODUCTION SLL

| Tên Module | DEMO | PRODUCTION SLL | Chi tiết |
| :--- | :--- | :--- | :--- |
| **Browser** | Undetected Chromedriver (UC) | Playwright Async | UC chạy luồng chính ổn định trên Linux, Playwright tối ưu đa luồng ngầm diện rộng |
| **Mail Engine** | API Mail 10p (Mail.tm) | Domain Catch-All + IMAP | Tránh domain ảo bị Garena đưa vào blacklist |
| **Network** | Mạng LAN (Bị Ban IP) | Proxy Xoay HTTP/IPv4 | Tránh trùng IP dẫn đến block đăng ký, tích hợp check live ngầm |
| **Captcha** | Giải bằng tay (Manual Pause) | API 3rd (AnyCaptcha...) | Tự động hóa 100% khi chạy ngầm |  
| **Data Storage** | Ghi thẳng vào file phẳng (.csv) | Kết nối Database (SQL) | Tránh xung đột khóa (Lock) khi ghi đa luồng. Quản lý trạng thái acc tốt hơn. |

---

## III. Xây dựng Core (Demo)
1. **Mục tiêu:** Tạo được tài khoản thành công bằng tay kết hợp tool.
2. **Tiến độ chi tiết:**
   - [x] **Task 1: Module Browser** -> Dùng `undetected_chromedriver` tối ưu cờ CLI chống crash trên Linux Mint, fake vân tay WebGL và ngôn ngữ qua CDP.
   - [x] **Task 2: Module Mail Demo** -> Dùng Class OOP `MailTmManager` gọi API `mail.tm` lấy mail ngẫu nhiên điền vào form.
   - [x] **Task 3: Cơ chế dừng (Manual Pause)** -> Sử dụng `input()` dừng luồng để người dùng tự tay giải Captcha và nhấn nút nhận mã.
   - [x] **Task 4: Module Mail OTP** -> Dùng thư viện `re` bóc tách mã OTP 8 số của Garena bằng Regex `\b\d{6,8}\b` từ hòm thư trả về.
   - [x] **Task 5: Module Storage** -> Xuất thông tin tài khoản đăng ký thành công ra file `outputs/accounts.csv`.
   - [ ] **Task 6: Network** -> Tích hợp HTTP Proxy (Xác thực Extension/IP) và hàm check live kết nối ngầm trước khi mở Browser.

---

## IV. Nâng cấp Core (SLL)
1. **Mục tiêu:** Cắt bỏ hoàn toàn phụ thuộc bên ngoài và tự động hóa 100%.
2. **Tiến độ chi tiết:**
   - [ ] **Task 1: Thay thế Mail** -> Mua domain riêng, cấu hình Catch-all. Viết hàm Python kết nối IMAP đọc OTP từ mail tổng.
   - [ ] **Task 2: Thay thế Captcha** -> Tích hợp API giải Captcha bên thứ 3 (AnyCaptcha...), nhận tọa độ/token trả về để điền tự động.
   - [ ] **Task 3: Thay thế Network** -> Cấu hình Proxy xoay đi kèm trực tiếp với từng Playwright Browser Context.
   - [ ] **Task 4: Tối ưu hóa** -> Chuyển dịch cấu trúc sang OOP kết hợp Đa luồng (`asyncio` / `threading`).

---

## V. Thiết lập Domain & Kịch bản Ngâm Traffic (Production SLL)

Khi vận hành hệ thống số lượng lớn, việc sử dụng các hòm thư tạm thời (Temp Mail) sẽ bị hệ thống kiểm soát của Garena chặn đứng do kích hoạt cơ chế phát hiện bất thường (Anomaly Detection). Để giải quyết triệt để rủi ro "bay domain" và tối ưu hóa chi phí vận hành, hệ thống bắt buộc phải triển khai hạ tầng Domain riêng độc lập.

### 1. Quy trình tự động hóa thiết lập Tên miền (Domain Onboarding Lifecycle)

Mọi tên miền mới mua phục vụ dự án phải trải qua chuỗi các bước thiết lập tự động hóa nghiêm ngặt nhằm tích lũy độ uy tín (Reputation Score) trước khi chính thức đưa vào khai thác thương mại:

```mermaid
flowchart TD
    A([📋 Danh sách Tên miền mới mua])
    A --> B

    subgraph B["🔧 TOOL 1 — Cloudflare API Automation"]
        direction TB
        B1[1. Tự động thêm Site vào tài khoản Cloudflare]
        B2[2. Kích hoạt Email Routing - Catch-All]
        B3[3. Auto cấu hình DNS: MX / SPF / DKIM / DMARC]
        B1 --> B2 --> B3
    end

    B --> C

    subgraph C["🚀 TOOL 2 — Cloudflare Pages Deploy"]
        direction TB
        C1[1. Đẩy mã nguồn Landing Page tĩnh lên Cloudflare Pages]
        C2[2. Xây dựng bộ nhận diện website doanh nghiệp thật]
        C1 --> C2
    end

    C --> D

    subgraph D["🤖 TOOL 3 — Playwright Traffic Generator"]
        direction TB
        D1[1. Chạy bot ngầm mô phỏng hành vi người dùng thật]
        D2[2. Duy trì lưu lượng truy cập ảo liên tục trong 3 - 5 ngày]
        D1 --> D2
    end

    D --> E([✅ Hệ thống Domain Sạch & Uy Tín])
    E -->|Cung cấp đầu vào an toàn| F[Tool Reg Garena SLL]
```
### 2. Tiêu chuẩn cấu hình xác thực Mail Server (Vượt màng lọc Garena)

Nếu domain chỉ cấu hình mỗi bản ghi MX để nhận thư mà thiếu các bản ghi chứng thực danh tính, hệ thống bảo mật của Garena sẽ phân loại đây là Mail Server lậu và từ chối gửi OTP. Các bản ghi bắt buộc phải nạp qua Cloudflare DNS bao gồm:

* **MX Records (Mail Exchange):** Trỏ về máy chủ Email Routing của Cloudflare để bắt toàn bộ các ký tự email ngẫu nhiên đứng trước (Cơ chế Catch-All, ví dụ: `grn_xxxx@yourdomain.xyz`).
* **SPF (Sender Policy Framework):** Khai báo TXT Record với giá trị để xác thực quyền hạn phân phối thư của hệ thống:
    ```text
    v=spf1 include:_spf.mx.cloudflare.net ~all
    ```
* **DMARC (Domain-based Message Authentication):** Thêm bản ghi TXT với Host: `_dmarc` và Value dưới đây để thiết lập chính sách bảo mật nâng cao, gia tăng tối đa điểm uy tín (Reputation Score) cho domain mới tạo:
    ```text
    v=DMARC1; p=none;
    ```

### 3. Chiến lược kiểm soát lưu lượng & Tránh Blacklist (Traffic Shaper & Rate Limiting)
Để duy trì tuổi thọ cho domain và tránh việc toàn bộ tên miền gốc bị đưa vào danh sách đen, lưu lượng nhận mail xác thực sẽ được điều phối nghiêm ngặt theo mô hình hình thang dựa trên độ tuổi tên miền (Domain Age):
* **Giai đoạn Thử nghiệm (Ngày 4 - 5):** Chỉ phân phối tối đa từ 10 - 20 tài khoản/ngày trên mỗi tên miền nhằm mục đích thăm dò màng lọc.
* **Giai đoạn Tăng trưởng (Ngày 6 trở đi):** Nâng dần hạn mức đăng ký theo thang cấp độ (50 ➡️ 100 ➡️ 500 tài khoản/ngày) dựa trên tỷ lệ nhận OTP thành công.
* **Cơ chế cô lập rủi ro bằng Subdomain:** Thiết kế module tự động chia nhỏ và phân phối tải thông qua các Subdomain con (`s1.yourdomain.xyz`, `s2.yourdomain.xyz`) trên Cloudflare. Khi có biến động block, hệ thống chỉ bị ảnh hưởng ở phân vùng phân phối đó, bảo vệ an toàn cho Apex Domain gốc không bị thâm hụt.

### 4. Tối ưu hóa kiểm tra Logic điều phối Code (Quản lý rủi ro chi phí)
Để tránh tình trạng thâm hụt ngân sách khi chạy thực tế do lỗi mạng hoặc proxy chết giữa chừng, luồng code bắt buộc phải tuân thủ nghiêm ngặt cơ chế kiểm tra chéo:
* **Hàm check trạng thái Proxy trước luồng:** Luôn gọi một request ngắn (timeout 3 - 5s) để xác thực tính ổn định của IP Proxy trước khi kích hoạt API giải Captcha bên thứ ba nhằm tối ưu chi phí, loại bỏ hoàn toàn việc mất tiền oan do proxy sập.
* **Timeout cào OTP đồng bộ:** Do cơ chế Cloudflare Email Routing mất từ 5 - 10 giây để forward thư về hòm thư tổng, vòng lặp cào mail qua kết nối IMAP phải được thiết lập thời gian chờ (Timeout) tối thiểu là 45 - 60 giây để đảm bảo không bị đóng tiến trình vội vàng, gây mất trắng chi phí giải captcha của lượt chạy đó.

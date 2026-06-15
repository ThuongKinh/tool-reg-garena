# 🚀 ToolACCGrn — Hệ Thống Tự Động Hóa Đăng Ký Tài Khoản Garena Quy Mô Lớn

## I. Tổng Quan Dự Án
1. **Mục tiêu:** Xây dựng công cụ tự động tạo tài khoản Garena hàng loạt (SLL) trên máy thật (Native Linux/Windows), tối ưu tài nguyên và không phụ thuộc vào Docker.
2. **Triết lý cốt lõi:** Phát triển từ bản **DEMO** (chạy thủ công từng bước để bắt mạch màng lọc bảo mật) tiến thẳng lên bản **PRODUCTION** (tự động hóa 100%, chạy ngầm, tiết kiệm RAM/CPU).

---

## II. Ma Trận Kiến Trúc: Bản DEMO vs Bản PRODUCTION SLL

| Thành phần | Phiên bản DEMO (Hiện tại) | Phiên bản PRODUCTION SLL (Nâng cấp) | Giải thích thuật ngữ |
| :--- | :--- | :--- | :--- |
| **Trình duyệt (Browser)** | Undetected Chromedriver (Selenium) | **Playwright Async** | *Playwright Async* giúp điều khiển trình duyệt ẩn danh bằng mã bất đồng bộ, tốc độ mở trang nhanh gấp 3 lần Selenium. |
| **Cách chạy luồng (Flow)** | Chạy 100% trên giao diện (UI-Driven) | **Kiến trúc Lai (Hybrid Architecture)** | *Hybrid:* Chỉ bật trình duyệt lên để vượt qua Captcha lấy mã xác thực (Cookie), sau đó tắt trình duyệt đi và dùng lệnh mạng (HTTP Request) để đăng ký ngầm, giúp tiết kiệm 80% RAM/CPU. |
| **Mạng (Network)** | Xoay mạng thủ công (iPhone) | **Proxy Xoay (Residential Proxy)** | *Proxy xoay:* Hệ thống tự mua và đổi IP tự động sau mỗi mẻ chạy thông qua code, không cần chạm vào điện thoại. |
| **Giải Captcha** | Giải bằng tay (Manual Pause) | **API Bên Thứ 3 (AnyCaptcha/2Captcha)** | Tự động gửi hình ảnh/tọa độ Captcha sang bên thứ 3 giải bằng AI và trả kết quả về trong 2 giây. |
| **Hòm thư (Mail Engine)** | Mail 10 phút miễn phí (Mail.tm) | **Domain Catch-All + IMAP** | *Catch-All:* Mua 1 tên miền riêng (VD: `abc.com`), Garena gửi thư vào bất kỳ tên email nào (như `reg1@abc.com`, `reg2@abc.com`) thì thư đều chạy về một hòm thư tổng để code tự đọc mã OTP qua giao thức *IMAP*. |
| **Lưu trữ (Storage)** | Ghi ra file phẳng (`accounts.csv`) | **Cơ sở dữ liệu (SQLite / PostgreSQL)** | Lưu tài khoản vào Database để tránh lỗi xung đột khi nhiều luồng cùng ghi vào một file `.csv` một lúc. |

---

## III. Nhật Ký Tiến Độ Phát Triển

### 🛠️ Giai đoạn 1: Hoàn thành lõi DEMO (100%)
- [x] **Task 1 (Browser Core):** Tích hợp driver ẩn danh chống sập, vượt qua các cờ kiểm tra robot cơ bản của Chrome.
- [x] **Task 2 (Mail API):** Viết module gọi hòm thư tạm thời tự động lấy tên email nạp vào form Garena.
- [x] **Task 3 (Manual Pause):** Viết hàm thông minh phát hiện màng che Captcha, tự dừng luồng chờ người dùng giải tay và nhấn Enter để chạy tiếp.
- [x] **Task 4 (OTP Extraction):** Dùng biểu thức chính quy (Regex) tự động bóc tách mã OTP 8 số từ nội dung email Garena gửi về.
- [x] **Task 5 (File Storage):** Lưu dữ liệu đăng ký thành công cục bộ ra file `outputs/accounts.csv`.

### 🚀 Giai đoạn 2: Nâng cấp luồng SLL chống Antibot (Đang triển khai)
- [ ] **Task 1 (Dynamic Fingerprint):** Viết hàm tự động tráo đổi thông số phần cứng (CPU, RAM, Card đồ họa) ngẫu nhiên cho mỗi mẻ chạy để phá cơ chế gom cụm thiết bị của hệ thống chống bot.
- [ ] **Task 2 (Sinh học hành vi):** Sửa lại hàm di chuyển chuột theo đường cong (Bezier) và hàm gõ bàn phím có nhịp điệu (lúc nhanh, lúc chậm, có nhịp khựng) để mô phỏng chính xác thao tác tay của con người.
- [ ] **Task 3 (Catch-All Mail Core):** Cấu hình tự động hóa DNS của tên miền riêng trên Cloudflare và viết hàm Python tự động kết nối cổng IMAP để cào OTP từ hòm thư tổng.

---

## IV. Cơ Chế Phòng Thủ Của Garena (DataDome v5.7.0) & Cách Vượt Qua

Hệ thống bảo mật của Garena sử dụng tường lửa **DataDome đời mới**. Hệ thống này thu thập hành vi và thông số máy của bạn thông qua một gói tin mã hóa tinh vi để chấm điểm rủi ro (Risk Score). ToolACCGrn vượt qua bộ lọc này bằng các giải pháp kỹ thuật sau:

1. **Vượt cơ chế quét ngầm (Web Worker Isolation):**
   - *Rào cản:* DataDome tạo ra một tiến trình ngầm (Web Worker) độc lập để ép card màn hình của bạn dựng hình ẩn nhằm đọc thông số phần cứng thật, bỏ qua các tập lệnh fake bằng Javascript thông thường.
   - *Cách xử lý:* Tool can thiệp sâu bằng các cờ CLI từ lúc khởi động nhân Chromium (`--use-gl=angle`, `--use-angle=swiftshader`) để ép toàn bộ hệ thống (kể cả tiến trình ngầm) xuất ra thông số đồng bộ với User-Agent giả lập.

2. **Phá bộ lọc nhịp điệu gõ phím (Keyboard Dynamics):**
   - *Rào cản:* Robot thường gõ các ký tự với khoảng thời gian đều tăm tắp (ví dụ: luôn nghỉ 50ms giữa các phím). DataDome sẽ đo độ lệch chuẩn này để khóa tài khoản ngay lập tức với lỗi "duyệt và nhấp chuột nhanh hơn con người".
   - *Cách xử lý:* Thay vì dùng hàm ngẫu nhiên phẳng, tool áp dụng **Phân phối chuẩn (Gaussian)**. Phím ở gần gõ nhanh (60ms), phím ở xa gõ chậm (150ms), giữ phím lún xuống phần cứng (Key Hold Time) từ 65ms-115ms, và tự động khựng lại 0.2 giây sau mỗi 4 ký tự để suy nghĩ như người thật.

3. **Tối ưu hóa Token Replay (Kiến trúc Lai):**
   - Trình duyệt Playwright chỉ đóng vai trò là "mồi nhử" ở chặng đầu để giải Captcha.
   - Ngay sau khi giải xong, mã nguồn Python sẽ chộp lấy chuỗi xác thực an toàn (Cookie `datadome`) từ mạng, đóng hoàn toàn trình duyệt để giải phóng 100% RAM/CPU, sau đó dùng lệnh mạng thuần gửi tiếp yêu cầu lấy OTP và chốt tài khoản.

---

## V. Hướng Dẫn Cấu Hình Hạ Tầng Tên Miền (Bản Production)

Để tránh hòm thư bị Garena đưa vào danh sách đen, hệ thống bắt buộc phải sử dụng tên miền riêng cấu hình qua Cloudflare DNS với các bản ghi chứng thực danh tính sau:

1. **Bản ghi MX (Mail Exchange):** Trỏ về Mail Routing của Cloudflare để kích hoạt tính năng bắt toàn bộ email ngẫu nhiên (Catch-All).
2. **Bản ghi SPF (TXT Record):** Xác thực quyền hạn gửi/nhận thư hợp pháp:
   ```text
   v=spf1 include:_spf.mx.cloudflare.net ~all

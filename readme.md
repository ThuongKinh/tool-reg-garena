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
   - [ ] **Task 2: Module Mail Demo** -> Sử dụng HTTP requests gọi API `mail.tm` để lấy 1 mail ảo ngẫu nhiên, điền vào form.
   - [ ] **Task 3: Cơ chế dừng (Manual Pause)** -> Code dừng lại tầm 15 - 30 giây để người dùng tự tay giải Captcha và nhấn nút nhận mã.
   - [ ] **Task 4: Module Mail OTP** -> Gọi API kiểm tra hòm thư ảo, cào mã OTP 6 số và tự động điền vào Garena.
   - [ ] **Task 5: Module Storage** -> Xuất thông tin tài khoản đăng ký thành công ra file cục bộ.

---

## IV. Nâng cấp Core (SLL)
1. **Mục tiêu:** Cắt bỏ hoàn toàn phụ thuộc bên ngoài và tự động hóa 100%.
2. **Tiến độ chi tiết:**
   - [ ] **Task 1: Thay thế Mail** -> Mua domain riêng, cấu hình Catch-all. Viết hàm Python kết nối IMAP đọc OTP từ mail tổng.
   - [ ] **Task 2: Thay thế Captcha** -> Tích hợp API giải Captcha bên thứ 3 (AnyCaptcha...), nhận tọa độ/token trả về để điền tự động.
   - [ ] **Task 3: Thay thế Network** -> Cấu hình Proxy xoay đi kèm trực tiếp với từng Browser Context.
   - [ ] **Task 4: Tối ưu hóa** -> Chuyển dịch cấu trúc sang OOP kết hợp Đa luồng (`asyncio` / `threading`).

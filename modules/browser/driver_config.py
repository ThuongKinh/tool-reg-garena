import undetected_chromedriver as uc
from contextlib import contextmanager


def create_stealth_driver(headless: bool = False):
    """
    Khởi tạo Chrome Driver tối ưu cho Linux Mint.
    Dùng UC + CDP injection thay vì selenium_stealth để tránh xung đột.
    """
    options = uc.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")          # Bắt buộc khi headless/root
        options.add_argument("--disable-dev-shm-usage")
    else:
        options.add_argument("--start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-popup-blocking")
        # Không cần --disable-gpu trên Linux Mint có desktop
        # Không cần --no-sandbox nếu chạy user thường

    # User-Agent nhất quán với platform Win32
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
    except Exception as e:
        print(f"[ERROR] Không thể khởi tạo driver: {e}")
        raise

    _inject_fingerprint(driver)
    return driver


def _inject_fingerprint(driver):
    """
    Inject fingerprint nhất quán với Windows qua CDP.
    Tách riêng để dễ maintain và debug.
    """
    script = """
        // Platform — khớp với user-agent Win32
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32'
        });

        // Language
        Object.defineProperty(navigator, 'language', {
            get: () => 'vi-VN'
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['vi-VN', 'vi', 'en-US', 'en']
        });

        // Thêm dòng này ngay trên đoạn ghi đè cũ
        const _getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Google Inc. (Intel)';
            if (parameter === 37446) return 'ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)';
        return _getParameter.call(this, parameter);
        };

        // ĐÈ TIẾP PROTOTYPE CỦA WEBGL2 ĐỂ ĐỒNG BỘ 100%
        if (window.WebGL2RenderingContext) {
            const _getParameter2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Google Inc. (Intel)';
            if (parameter === 37446) return 'ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)';
        return _getParameter2.call(this, parameter);
        };
}

        // Ẩn automation flags
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    """

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": script
    })


def quit_driver(driver):
    """Đóng driver an toàn, không throw exception."""
    try:
        if driver:
            driver.quit()
    except Exception:
        pass


@contextmanager
def stealth_driver_context(headless: bool = False):
    """Context manager — tự động cleanup dù có lỗi hay không."""
    driver = None
    try:
        driver = create_stealth_driver(headless=headless)
        yield driver
    finally:
        quit_driver(driver)


# ── Ví dụ sử dụng ────────────────────────────────────────────
if __name__ == "__main__":

    # Cách 1: Thủ công
    driver = create_stealth_driver()
    try:
        driver.get("https://example.com")
    finally:
        quit_driver(driver)

    # Cách 2: Context manager (khuyến nghị)
    with stealth_driver_context() as driver:
        driver.get("https://example.com")

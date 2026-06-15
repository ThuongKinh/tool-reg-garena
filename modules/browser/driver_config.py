import undetected_chromedriver as uc
from contextlib import contextmanager
import os
import shutil
import re

def get_local_chrome_major_version():
    """Tự động quét phiên bản Chrome thực tế trên máy Linux Mint để đồng bộ."""
    try:
        import subprocess
        output = subprocess.check_output(["google-chrome", "--version"]).decode("utf-8")
        version_match = re.search(r"(\d+)\.", output) # Rút gọn regex quét chuẩn xác
        if version_match:
            return version_match.group(1)
    except Exception:
        pass
    return "124"
import os
import undetected_chromedriver as uc

def create_stealth_driver(data_dir, headless: bool = False):
    options = uc.ChromeOptions()
    
    # Định nghĩa chuỗi Agent sạch, tuyệt đối không dùng f-string lỗi kí tự trên Linux
    ua_string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    
    # NẠP CHUẨN: Cú pháp bọc cứng bằng dấu cộng chuỗi, không có khoảng trắng thừa
    options.add_argument('--user-agent=' + ua_string)

    # data_dir = os.path.join(os.getcwd(), "outputs", "chrome_linux_profile")
    options.add_argument(f"--user-data-dir={data_dir}")
    

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    else:
        options.add_argument("--start-maximized")
        options.add_argument("--disable-popup-blocking")
        
        # --- BỘ CỜ KHÓA CÔ LẬP TIẾN TRÌNH - CHỐNG SẬP KHI TẢI IFRAME ---
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage") # Ép Chrome dùng ổ cứng làm bộ đệm thay vì /dev/shm
        options.add_argument("--use-gl=angle") 
        options.add_argument("--use-angle=swiftshader")  # Dùng bộ dựng hình phần mềm siêu nhẹ
        
        # CHÍ MẠNG: Khóa triệt để tính năng tách tiến trình con khi gặp Iframe/Cross-site của Chrome v149
        options.add_argument("--disable-features=IsolateOrigins,site-per-process,SitePerProcess") 
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--lang=vi-VN")

    try:
        # Lấy phiên bản major tự động
        from modules.browser.driver_config import get_local_chrome_major_version
        chrome_major = get_local_chrome_major_version()
        chrome_version_int = int(chrome_major)
        
        # Bắt buộc dùng use_subprocess=False để quản lý luồng trực tiếp không qua daemon ẩn
        driver = uc.Chrome(options=options, version_main=chrome_version_int, use_subprocess=False)
    except Exception as e:
        print(f"[ERROR] Không thể khởi tạo driver: {e}")
        raise

    # Bọc lót thêm tầng Fingerprint ngầm cho đồng nhất danh tính
    _inject_hardened_fingerprint(driver, ua_string, chrome_major)
    return driver
def _inject_hardened_fingerprint(driver, user_agent, chrome_major):
    """Ghi đè cấu hình tầng sâu CDP để đồng bộ danh tính"""
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": user_agent,
        "platform": "Win32"
    })

    script = """
        // Khử hoàn toàn biến webdriver ngầm
        const newProto = navigator.__proto__;
        delete newProto.webdriver;
        navigator.__proto__ = newProto;

        Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4 });
        Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
        Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
        Object.defineProperty(navigator, 'language', { get: () => 'vi-VN' });
        Object.defineProperty(navigator, 'languages', { get: () => ['vi-VN', 'vi', 'en-US', 'en'] });

        if (navigator.userAgentData) {
            Object.defineProperty(navigator.userAgentData, 'platform', { get: () => 'Windows' });
            Object.defineProperty(navigator.userAgentData, 'brands', {
                get: () => [
                    { brand: 'Google Chrome', version: 'CHROME_VERSION_PLACEHOLDER' },
                    { brand: 'Chromium', version: 'CHROME_VERSION_PLACEHOLDER' },
                    { brand: 'Not=A?Brand', version: '99' }
                ]
            });
        }

        // --- GHI ĐÈ WEBGL KHỚP MÔI TRƯỜNG LINUX GIẢ LẬP WINDOWS ---
        // Sử dụng thông số Card Intel tiêu chuẩn, loại bỏ chuỗi Direct3D11 để tránh bẫy logic đồ họa
        const maskWebGL = (ctx) => {
            if (!ctx) return;
            const _getParameter = ctx.prototype.getParameter;
            ctx.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Google Inc. (Intel)';
                if (parameter === 37446) return 'ANGLE (Intel, Intel(R) UHD Graphics 620)';
                return _getParameter.call(this, parameter);
            };
        };
        maskWebGL(WebGLRenderingContext);
        if (window.WebGL2RenderingContext) {
            maskWebGL(WebGL2RenderingContext);
        }
    """
    
    final_script = script.replace("CHROME_VERSION_PLACEHOLDER", str(chrome_major))
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": final_script
    })

@contextmanager
def stealth_driver_context(data_dir,headless: bool = False):
    """Context Manager quản lý đóng/mở luồng tự động sạch sẽ"""
    driver = None
    try:
        driver = create_stealth_driver(data_dir,headless=headless)
        yield driver
    finally:
        try:
            if driver:
                driver.quit()
        except:
            pass

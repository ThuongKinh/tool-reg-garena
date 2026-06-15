import os
import shutil
import re
import subprocess
import random 
from contextlib import contextmanager
import undetected_chromedriver as uc

def get_local_chrome_major_version():
    """Tự động quét phiên bản Chrome thực tế trên máy Linux để đồng bộ."""
    try:
        output = subprocess.check_output(["google-chrome", "--version"]).decode("utf-8")
        version_match = re.search(r"(\d+)\.", output)
        if version_match:
            return version_match.group(1)
    except Exception:
        pass
    return "124"

def create_stealth_driver(data_dir, headless: bool = False):
    options = uc.ChromeOptions()
    
    # 1. Đồng bộ hóa hoàn toàn phiên bản Chrome thực tế vào User-Agent
    chrome_major = get_local_chrome_major_version()
    ua_string = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_major}.0.0.0 Safari/537.36"
    
    options.add_argument('--user-agent=' + ua_string)
    options.add_argument(f"--user-data-dir={data_dir}")
    options.add_argument("--incognito") # Ép chạy chế độ ẩn danh cách ly hoàn toàn session
    
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    else:
        options.add_argument("--start-maximized")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage") 
        options.add_argument("--use-gl=angle") 
        options.add_argument("--use-angle=swiftshader")  
        options.add_argument("--disable-features=IsolateOrigins,site-per-process,SitePerProcess") 
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--lang=vi-VN")

    # 🔥 KÍCH HOẠT ĐÓN LÕNG GÓI TIN: Cho phép bóc tách cấu trúc log mạng và console nền của Chrome
    options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})

    try:
        chrome_version_int = int(chrome_major)
        driver = uc.Chrome(options=options, version_main=chrome_version_int, use_subprocess=False)
    except Exception as e:
        print(f"[ERROR] Không thể khởi tạo driver: {e}")
        raise

    # 2. Sinh thông số cấu hình máy ngẫu nhiên cho mỗi luồng (Dynamic Fingerprinting)
    random_cores = random.choice([4, 6, 8, 12])
    random_memory = random.choice([8, 16, 32])
    
    gpu_profiles = [
        {"vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620)"},
        {"vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics)"},
        {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 Direct3D11)"},
        {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11)"}
    ]
    chosen_gpu = random.choice(gpu_profiles)

    _inject_hardened_fingerprint(
        driver=driver, 
        user_agent=ua_string, 
        chrome_major=chrome_major,
        cores=random_cores,
        memory=random_memory,
        gpu_vendor=chosen_gpu["vendor"],
        gpu_renderer=chosen_gpu["renderer"]
    )
    return driver

def _inject_hardened_fingerprint(driver, user_agent, chrome_major, cores, memory, gpu_vendor, gpu_renderer):
    """Ghi đè cấu hình tầng sâu CDP biến mỗi phiên chạy thành một máy tính biệt lập"""
    try:
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {
            "userAgent": user_agent,
            "platform": "Win32"
        })
    except:
        pass

    script = f"""
        const newProto = navigator.__proto__;
        delete newProto.webdriver;
        navigator.__proto__ = newProto;

        Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {cores} }});
        Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {memory} }});
        Object.defineProperty(navigator, 'platform', {{ get: () => 'Win32' }});
        Object.defineProperty(navigator, 'language', {{ get: () => 'vi-VN' }});
        Object.defineProperty(navigator, 'languages', {{ get: () => ['vi-VN', 'vi', 'en-US', 'en'] }});

        if (navigator.userAgentData) {{
            Object.defineProperty(navigator.userAgentData, 'platform', {{ get: () => 'Windows' }});
            Object.defineProperty(navigator.userAgentData, 'brands', {{
                get: () => [
                    {{ brand: 'Google Chrome', version: '{chrome_major}' }},
                    {{ brand: 'Chromium', version: '{chrome_major}' }},
                    {{ brand: 'Not=A?Brand', version: '99' }}
                ]
            }});
        }}

        const maskWebGL = (ctx) => {{
            if (!ctx) return;
            const _getParameter = ctx.prototype.getParameter;
            ctx.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) return '{gpu_vendor}';
                if (parameter === 37446) return '{gpu_renderer}';
                return _getParameter.call(this, parameter);
            }};
        }};
        maskWebGL(WebGLRenderingContext);
        if (window.WebGL2RenderingContext) {{
            maskWebGL(WebGL2RenderingContext);
        }}
    """
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": script
        })
    except:
        pass

@contextmanager
def stealth_driver_context(data_dir, headless: bool = False):
    """Context Manager quản lý đóng/mở luồng tự động sạch sẽ"""
    driver = None
    try:
        driver = create_stealth_driver(data_dir, headless=headless)
        yield driver
    finally:
        try:
            if driver:
                driver.quit()
        except:
            pass

import random
from playwright.async_api import BrowserContext

# =====================================================================
# PHẦN 1: BỂ DỮ LIỆU VÂN TAY (FINGERPRINT POOL)
# Phải gom thành bộ để tránh tình trạng: User-Agent là máy yếu nhưng RAM/GPU lại là quái vật, 
# khiến DataDome kích hoạt cơ chế phát hiện bất thường (Anomaly Detection).
# =====================================================================
FINGERPRINT_POOL = [
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "cores": 8,
        "ram": 16,
        "gl_vendor": "Google Inc. (Intel)",
        "gl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 (0x00003E9B) Direct3D11 vs_5_0 ps_5_0)"
    },
    {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "cores": 12,
        "ram": 32,
        "gl_vendor": "Google Inc. (NVIDIA)",
        "gl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)"
    },
    {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "cores": 4,
        "ram": 8,
        "gl_vendor": "Google Inc. (Intel)",
        "gl_renderer": "ANGLE (Intel, Intel(R) HD Graphics 620 Direct3D11 vs_5_0 ps_5_0)"
    }
]

# =====================================================================
# PHẦN 2: KHỞI TẠO NHÂN TRÌNH DUYỆT (LAUNCH ENGINE)
# Can thiệp sâu từ nhân Chromium bằng các cờ lệnh hệ thống (Launch Args).
# =====================================================================
async def get_stealth_browser(p, headless=False):
    """
    Khởi chạy nhân Chromium bẻ gãy các bộ quét tự động hóa toàn cục.
    """
    browser = await p.chromium.launch(
        headless=headless,
        args=[
            # Lớp 1: Xóa bỏ hoàn toàn cờ 'navigator.webdriver = true' tai hại
            "--disable-blink-features=AutomationControlled",
            
            # Lớp 2: Bảo mật và tối ưu hiệu năng chạy ngầm trên Linux Mint
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-infobars",
            "--window-position=0,0",
            
            # Lớp 3: Chí mạng chống bộ quét Web Worker của DataDome
            # Ép trình duyệt sử dụng kiến trúc ANGLE và SwiftShader để đồng bộ hóa 
            # dữ liệu dựng hình ẩn (OffscreenCanvas) khớp 100% với cấu hình fake bên ngoài.
            "--use-gl=angle",
            "--use-angle=swiftshader"
        ]
    )
    return browser

# =====================================================================
# PHẦN 3: CẤP PHÁT DANH TÍNH ĐỘNG (DYNAMIC CONTEXT)
# Đóng vai trò cấp phát 'Hộ chiếu sạch' cho từng luồng tài khoản.
# =====================================================================
async def create_clean_context(browser) -> BrowserContext:
    """
    Sinh ngẫu nhiên cấu hình phần cứng vật lý và tiêm mã độc lập để bypass antibot.
    """
    # 1. Bốc ngẫu nhiên 1 bộ danh tính từ bể dữ liệu vật lý
    selected_fp = random.choice(FINGERPRINT_POOL)
    
    # 2. Thiết lập bộ khung môi trường chuẩn Việt Nam
    context = await browser.new_context(
        user_agent=selected_fp["user_agent"],
        locale="vi-VN",
        timezone_id="Asia/Ho_Chi_Minh", # Khớp múi giờ người dùng thật
        viewport={"width": 1280, "height": 720},
        ignore_https_errors=True
    )
    
    # 3. KỸ THUẬT TIÊM SCRIPT (Mã độc lập - JavaScript Injection)
    # Vì Playwright không cho sửa trực tiếp navigator.hardwareConcurrency qua tham số, 
    # chúng ta phải viết một đoạn script chạy NGAY LẬP TỨC trước khi trang web kịp load 
    # nhằm đóng băng (freeze) các thuộc tính hệ thống lại, không cho DataDome bóc phốt.
    init_script = f"""
    Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {selected_fp["cores"]} }});
    Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {selected_fp["ram"]} }});
    
    // Đè màng lọc WebGL của cả cửa sổ chính lẫn Web Worker ngầm
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {{
        if (parameter === 37445) return '{selected_fp["gl_vendor"]}'; // UNMASKED_VENDOR_WEBGL
        if (parameter === 37446) return '{selected_fp["gl_renderer"]}'; // UNMASKED_RENDERER_WEBGL
        return getParameter.apply(this, arguments);
    }};
    """
    
    # Ra lệnh cho Context luôn luôn thực thi đoạn script này trên mọi tab được mở ra
    await context.add_init_script(init_script)
    
    print(f"[+ Stealth] Đã bọc vân tay động: CPU {selected_fp['cores']} Cores | RAM {selected_fp['ram']}GB | GPU: {selected_fp['gl_renderer'][:40]}...")
    return context

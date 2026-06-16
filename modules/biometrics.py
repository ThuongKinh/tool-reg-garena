import asyncio
import random

async def move_mouse_humanlike(page, selector):
    """
    KẾT HỢP: Mô phỏng chuột lướt lệch tâm, sử dụng thời gian khựng Gaussian 
    để phá vỡ màng màng lọc kiểm tra vận tốc chuột tức thời.
    """
    try:
        element = page.locator(selector)
        box = await element.bounding_box()
        if not box:
            return
            
        # Tọa độ tâm mục tiêu
        target_x = box["x"] + box["width"] / 2
        target_y = box["y"] + box["height"] / 2
        
        # 1. Sinh điểm lệch ngẫu nhiên ngẫu nhiên xung quanh mục tiêu
        random_offset_x = target_x + random.randint(-80, -40)
        random_offset_y = target_y + random.randint(-25, -10)
        
        # Ép chuột lướt mượt qua 5 chặng trung gian đến điểm lệch
        await page.mouse.move(random_offset_x, random_offset_y, steps=5)
        
        # Điểm khựng Gaussian: Khoảng nghỉ siêu nhỏ trước khi điều chỉnh tâm chuột
        # Trung bình nghỉ 0.18s, độ lệch chuẩn 0.03s
        mouse_pause = random.gauss(0.18, 0.03)
        mouse_pause = max(0.12, min(mouse_pause, 0.25))
        await asyncio.sleep(mouse_pause)
        
        # 2. Lướt mượt chặng cuối vào tâm phần tử
        await page.mouse.move(target_x, target_y, steps=5)
        
    except Exception:
        try:
            await page.locator(selector).hover()
        except:
            pass

async def human_type(page, selector, text, speed_mode="normal"):
    """
    KẾT HỢP: Quản lý tốc độ theo ngữ cảnh (Demo) nhưng thời gian chờ 
    giữa từng phím bấm bấm được tính bằng Đường cong hình chuông Gaussian (SLL).
    """
    await page.wait_for_selector(selector, timeout=5000)
    await move_mouse_humanlike(page, selector)
    
    await page.locator(selector).click()
    
    # Khoảng chờ Gaussian sau khi click trước khi gõ phím phím đầu tiên
    click_delay = random.gauss(0.35, 0.05)
    await asyncio.sleep(max(0.25, min(click_delay, 0.45)))
    
    special_chars = "@#$!"
    
    for index, char in enumerate(text):
        # QUẢN LÝ TỐC ĐỘ THEO NGỮ CẢNH DÙNG HÀM GAUSS
        if speed_mode == "fast":
            # Trung bình 85ms, lệch chuẩn 10ms
            delay_between_keys = random.gauss(0.085, 0.010)
            delay_between_keys = max(0.060, min(delay_between_keys, 0.110))
        elif speed_mode == "slow":
            # Gõ Pass cẩn thận: Trung bình 250ms, lệch chuẩn 30ms
            delay_between_keys = random.gauss(0.250, 0.030)
            delay_between_keys = max(0.180, min(delay_between_keys, 0.320))
        else:
            # Chế độ bình thường: Trung bình 135ms, lệch chuẩn 20ms
            delay_between_keys = random.gauss(0.135, 0.020)
            delay_between_keys = max(0.090, min(delay_between_keys, 0.180))
            
        # KHỰNG NHỊP SINH HỌC KHI GÕ HẾT CỤM TỪ (Cứ sau 4 ký tự)
        if index > 0 and index % 4 == 0:
            cognitive_pause = random.gauss(0.185, 0.030)
            delay_between_keys += max(0.120, min(cognitive_pause, 0.250))
            
        # XỬ LÝ LÝ TỰ ĐẶC BIỆT AN TOÀN
        if char in special_chars:
            await page.keyboard.type(char)
            await asyncio.sleep(delay_between_keys)
        else:
            # Thời gian giữ phím vật lý lún xuống lún xuống (Key Hold Time) bằng Gauss
            key_hold_time = random.gauss(0.090, 0.012)
            key_hold_time = max(0.065, min(key_hold_time, 0.115))
            
            try:
                await page.keyboard.down(char)
                await asyncio.sleep(key_hold_time)
                await page.keyboard.up(char)
                await asyncio.sleep(delay_between_keys)
            except Exception:
                await page.keyboard.type(char)
                await asyncio.sleep(delay_between_keys)
                
    # Nghỉ tay một chút sau khi gõ xong toàn bộ chuỗi văn bản
    after_typing = random.gauss(0.55, 0.05)
    await asyncio.sleep(max(0.40, min(after_typing, 0.70)))

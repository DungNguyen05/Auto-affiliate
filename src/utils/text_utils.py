import re


def replace_shopee_links(content, old_links, new_links):
    """
    Thay thế link Shopee cũ bằng link affiliate mới
    Đồng thời xóa các ký tự … hoặc ... xung quanh link Shopee
    
    Args:
        content: Nội dung text gốc
        old_links: List link Shopee gốc
        new_links: List link affiliate tương ứng
    
    Returns:
        str: Nội dung đã được thay thế link và làm sạch
    """
    if not old_links or not new_links:
        return content
    
    result = content
    
    # Tạo mapping old -> new
    link_map = dict(zip(old_links, new_links))
    
    # Pattern để detect link Shopee dạng rút gọn: s.shopee.vn/xxxxx
    shopee_pattern = r's\.shopee\.vn/[A-Za-z0-9]+'
    
    # Tìm tất cả link rút gọn trong content
    short_links = re.findall(shopee_pattern, result)
    
    # Thay thế từng link
    for short_link in short_links:
        # Tìm link affiliate tương ứng
        for old_link, new_link in link_map.items():
            if short_link in old_link or short_link in result:
                # Pattern để tìm link kèm theo … hoặc ... xung quanh
                # Tìm: "s.shopee.vn/xxxxx…" hoặc "s.shopee.vn/xxxxx..."
                pattern_with_dots = rf'{re.escape(short_link)}[…\.]+'
                
                # Thay thế link kèm dấu 3 chấm bằng link mới (không có dấu 3 chấm)
                result = re.sub(pattern_with_dots, new_link, result)
                
                # Thay thế link đơn thuần (nếu không có dấu 3 chấm)
                result = result.replace(short_link, new_link)
                
                print(f"  ✅ Thay: {short_link} -> {new_link[:50]}...")
                break
    
    # Làm sạch các khoảng trắng thừa (nếu có)
    result = re.sub(r'\s+', ' ', result)
    result = result.strip()
    
    return result
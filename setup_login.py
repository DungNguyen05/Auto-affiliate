"""
Script setup ban đầu - Chạy 1 lần để đăng nhập Shopee Affiliate
Sau khi chạy xong, cookies sẽ được lưu và không cần login lại

Cách dùng:
    python setup_shopee_login.py          # Setup lần đầu
    python setup_shopee_login.py test     # Test auto-login
"""

from src.core.browser_manager import BrowserManager
from config.settings import SHOPEE_AFFILIATE_URL, LOGIN_WAIT_TIME


def setup_login():
    """Setup lần đầu - Đăng nhập và lưu cookies"""
    
    print("\n" + "="*60)
    print("🚀 SETUP SHOPEE AFFILIATE - LẦN ĐẦU TIÊN")
    print("="*60 + "\n")
    
    # Khởi tạo browser (KHÔNG headless để thấy GUI)
    browser = BrowserManager(headless=False)
    
    try:
        # 1. Khởi tạo driver
        driver = browser.init_driver()
        
        # 2. Kiểm tra profile có sẵn chưa
        if browser.is_profile_exists():
            print("\n⚠️  Profile đã tồn tại. Sẽ thử mở với profile có sẵn...")
            print("Nếu đã đăng nhập rồi thì sẽ tự động vào được!\n")
        else:
            print("\n📝 Đây là lần đầu tiên. Bạn cần đăng nhập thủ công.\n")
        
        # 3. Mở trang Shopee Affiliate
        browser.open_url(SHOPEE_AFFILIATE_URL)
        
        # 4. Đợi user đăng nhập thủ công
        browser.wait_for_manual_login(wait_time=LOGIN_WAIT_TIME)
        
        # 5. Đóng browser (cookies tự động lưu)
        browser.close()
        
        print("\n" + "="*60)
        print("✅ SETUP HOÀN TẤT!")
        print("="*60)
        print("\n📌 Cookies đã được lưu vào: data/browser_profile/")
        print("📌 Lần sau chạy script sẽ TỰ ĐỘNG đăng nhập!")
        print("\n💡 Tip: Chạy lại script này để kiểm tra auto-login\n")
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        browser.close()
        raise

if __name__ == "__main__":
    import sys
    setup_login()
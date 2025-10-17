"""
Script setup ban đầu - Chạy 1 lần để đăng nhập Shopee Affiliate và Threads
Sau khi chạy xong, cookies sẽ được lưu và không cần login lại

Cách dùng:
    python setup_login.py
"""

from src.core.browser_manager import BrowserManager
from config.settings import SHOPEE_AFFILIATE_URL


def setup_login():
    """Setup lần đầu - Đăng nhập Shopee và Threads, lưu cookies"""
    
    print("\n" + "="*60)
    print("🚀 SETUP LOGIN - SHOPEE AFFILIATE & THREADS")
    print("="*60 + "\n")
    
    # Khởi tạo browser (KHÔNG headless để thấy GUI)
    browser = BrowserManager(headless=False)
    
    try:
        # Khởi tạo driver
        driver = browser.init_driver()
        
        # Mở Shopee Affiliate
        print("📦 Đang mở Shopee Affiliate...")
        driver.execute_script(f"window.open('{SHOPEE_AFFILIATE_URL}', '_blank');")
        
        # Mở Threads
        print("🧵 Đang mở Threads...")
        driver.execute_script("window.open('https://www.threads.net/', '_blank');")
        
        print("\n" + "="*60)
        print("✅ ĐÃ MỞ 2 TAB!")
        print("="*60)
        print("\n📌 Vui lòng đăng nhập vào cả 2 trang:")
        print("   1️⃣  Shopee Affiliate")
        print("   2️⃣  Threads")
        print("\n⚠️  Sau khi đăng nhập xong, đóng browser để lưu cookies!")
        print("="*60 + "\n")
        
        # Đợi user tự đóng browser
        input("Nhấn Enter sau khi bạn đã đăng nhập xong và muốn đóng browser...")
        
        browser.close()
        
        print("\n✅ Cookies đã được lưu!")
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        browser.close()
        raise


if __name__ == "__main__":
    setup_login()
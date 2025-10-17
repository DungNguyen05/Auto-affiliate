import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import sys

# Add root directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import *


class BrowserManager:
    """Quản lý Chrome browser với user profile riêng"""
    
    def __init__(self, headless=HEADLESS_MODE):
        self.driver = None
        self.headless = headless
        self.profile_path = str(BROWSER_PROFILE_DIR)
        self.driver_path = str(CHROME_DRIVER_PATH)
    
    def init_driver(self):
        """Khởi tạo Chrome driver với user profile"""
        
        print("🔧 Đang khởi tạo Chrome driver...")
        
        # Kiểm tra ChromeDriver có tồn tại không
        if not Path(self.driver_path).exists():
            raise FileNotFoundError(
                f"❌ Không tìm thấy ChromeDriver tại: {self.driver_path}\n"
                f"Vui lòng download ChromeDriver và đặt vào folder drivers/"
            )
        
        # Chrome options
        options = Options()

        options.add_argument("--lang=en-US")
        
        # User data directory - LƯU COOKIES Ở ĐÂY
        options.add_argument(f"--user-data-dir={self.profile_path}")
        
        
        # Anti-detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance & stability
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        
        # Headless mode (nếu cần)
        if self.headless:
            options.add_argument("--headless=new")
        
        # Khởi tạo service với ChromeDriver path
        service = Service(executable_path=self.driver_path)
        
        # Khởi tạo driver
        try:
            self.driver = webdriver.Chrome(
                service=service,
                options=options
            )
            
            # Xóa thuộc tính webdriver để tránh phát hiện
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(IMPLICIT_WAIT)
            
            # Maximize window
            self.driver.maximize_window()
            
            print("✅ Chrome driver đã sẵn sàng!")
            print(f"📂 User profile: {self.profile_path}")
            return self.driver
            
        except Exception as e:
            print(f"❌ Lỗi khởi tạo driver: {e}")
            raise
    
    def is_profile_exists(self):
        """Kiểm tra user profile đã tồn tại chưa"""
        profile_dir = Path(self.profile_path)
        
        # Check xem có file Default/Cookies không
        cookies_file = profile_dir / "Default" / "Cookies"
        preferences_file = profile_dir / "Default" / "Preferences"
        
        if cookies_file.exists() or preferences_file.exists():
            print("✅ User profile đã tồn tại (có cookies/preferences)")
            return True
        else:
            print("⚠️  User profile chưa có hoặc chưa login")
            return False
    
    def open_url(self, url):
        """Mở một URL"""
        if not self.driver:
            raise Exception("Driver chưa được khởi tạo!")
        
        print(f"🌐 Đang mở: {url}")
        self.driver.get(url)
        time.sleep(3)  # Đợi page load
    
    def close(self):
        """Đóng browser"""
        if self.driver:
            print("🔒 Đang đóng browser...")
            self.driver.quit()
            print("✅ Đã đóng!")
    
    def __enter__(self):
        """Context manager support"""
        self.init_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()
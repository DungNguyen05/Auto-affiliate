from pathlib import Path

# Đường dẫn root project
BASE_DIR = Path(__file__).parent.parent

# Browser settings
BROWSER_PROFILE_DIR = BASE_DIR / "data" / "browser_profile"
CHROME_DRIVER_PATH = BASE_DIR / "drivers" / "chromedriver"  # hoặc "chromedriver.exe" trên Windows

# Tạo folder nếu chưa có
BROWSER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# Browser behavior
HEADLESS_MODE = False
PAGE_LOAD_TIMEOUT = 30
IMPLICIT_WAIT = 10

# Shopee settings
SHOPEE_AFFILIATE_URL = "https://affiliate.shopee.vn/offer/custom_link"
LOGIN_WAIT_TIME = 300  # 2 phút để đăng nhập
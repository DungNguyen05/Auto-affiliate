import time
import sys
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Add root directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.core.browser_manager import BrowserManager


class ThreadsPoster:
    """Chỉ click nút 'Post' trên Threads"""

    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.driver = browser_manager.driver

        if not self.driver:
            raise Exception("Browser chưa được khởi tạo!")

    def post_threads(self):
        """Mở Threads và click nút 'Post'"""
        print("\n" + "=" * 60)
        print("🧪 TEST CLICK POST BUTTON")
        print("=" * 60 + "\n")

        try:
            # 1. Mở trang Threads
            print("📍 Bước 1: Mở Threads...")
            self.driver.get("https://www.threads.net/")  # hoặc .com tùy quốc gia
            time.sleep(3)

            # 2. Tìm và click nút 'Post'
            print("📍 Bước 2: Tìm và click nút 'Post'...")
            post_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@role='button']//div[normalize-space(text())='Post']")
                )
            )

            post_button.click()
            print("✅ Đã click vào nút 'Post'!")

            # 3. Giữ trình duyệt mở để bạn quan sát
            print("\n⏸ Giữ trình duyệt mở, không đóng...")
            print("👉 Bạn có thể kiểm tra trạng thái tại trang Threads.")
            while True:
                time.sleep(10)  # vòng lặp giữ browser mở

        except TimeoutException:
            print("❌ Không tìm thấy nút 'Post' trong thời gian chờ.")
        except Exception as e:
            print(f"❌ Lỗi không xác định: {e}")
            import traceback
            traceback.print_exc()


def test_click_post_only():
    """Chạy thử chức năng click nút Post"""
    print("\n" + "=" * 60)
    print("🚀 RUNNING TEST: Click nút Post và dừng lại")
    print("=" * 60 + "\n")

    browser = BrowserManager(headless=False)

    try:
        browser.init_driver()
        poster = ThreadsPoster(browser)
        poster.post_threads()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_click_post_only()

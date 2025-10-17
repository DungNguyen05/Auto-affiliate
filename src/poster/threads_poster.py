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
    """Click nút 'Post' trên Threads và upload ảnh/video"""

    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.driver = browser_manager.driver

        if not self.driver:
            raise Exception("Browser chưa được khởi tạo!")

    def post_threads(self):
        """Mở Threads, click nút 'Post', nhập nội dung và upload ảnh/video"""
        print("\n" + "=" * 60)
        print("🧪 TEST CLICK POST BUTTON & UPLOAD MEDIA")
        print("=" * 60 + "\n")

        try:
            # 1. Mở trang Threads
            print("📍 Bước 1: Mở Threads...")
            self.driver.get("https://www.threads.net/")
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
            time.sleep(2)

            # 3. Tìm textbox để nhập nội dung
            print("📍 Bước 3: Tìm textbox để nhập nội dung...")
            textbox = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[role="textbox"][contenteditable="true"]')
                )
            )

            # Nhập nội dung test bằng JavaScript
            test_content = "🎉 Test post from automation! Check out this amazing product! 🛍️ #affiliate #shopee"
            print(f"📍 Bước 4: Nhập nội dung: {test_content}")
            self.driver.execute_script("""
                const box = arguments[0];
                const text = arguments[1];
                box.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, text);
                box.dispatchEvent(new Event('input', { bubbles: true }));
            """, textbox, test_content)
            print("✅ Đã nhập nội dung!")
            time.sleep(2)

            # 4. Tìm input file để upload
            print("📍 Bước 5: Tìm input file để upload...")
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@type='file' and contains(@accept, 'image')]")
                )
            )

            # 5. Chuẩn bị đường dẫn file
            base_dir = Path(__file__).parent.parent.parent
            image_path = base_dir / "post_content" / "instagram_image.jpg"
            video_path = base_dir / "post_content" / "video_instagram.mp4"

            # 6. Upload ảnh (nếu tồn tại)
            if image_path.exists():
                print(f"📍 Bước 6: Upload ảnh từ {image_path}...")
                file_input.send_keys(str(image_path.absolute()))
                print("✅ Đã upload ảnh!")
                time.sleep(2)
            else:
                print(f"⚠️  Không tìm thấy ảnh tại: {image_path}")

            # 7. Upload video (nếu tồn tại)
            if video_path.exists():
                print(f"📍 Bước 7: Upload video từ {video_path}...")
                file_input.send_keys(str(video_path.absolute()))
                print("✅ Đã upload video!")
                time.sleep(2)
            else:
                print(f"⚠️  Không tìm thấy video tại: {video_path}")
                
            print("📍 Bước 8: Click nút 'Add to thread'...")
            add_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[normalize-space(text())='Add to thread']")
                )
            )
            add_button.click()
            print("✅ Đã click 'Add to thread'!")
            time.sleep(2)
            
            print("📍 Bước 9: Nhập nội dung vào thread mới...")
            second_content = "💫 More details here! Limited time offer 🔥\n👉 Link: https://shope.ee/example"
            self.driver.execute_script("""
                const text = arguments[0];
                document.execCommand('insertText', false, text);
                document.activeElement.dispatchEvent(new Event('input', { bubbles: true }));
            """, second_content)
            print("✅ Đã nhập nội dung thread thứ 2!")
            time.sleep(2)
            
            # 10. Click nút "Post" để đăng bài
            print("📍 Bước 10: Click nút 'Post' để đăng bài...")
            post_in_popup = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//h1[.//span[normalize-space()='New thread']]/ancestor::div[@role='dialog']//div[@role='button']//div[normalize-space()='Post']"
                ))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", post_in_popup)
            self.driver.execute_script("arguments[0].click();", post_in_popup)
            print("✅ Click nút Post TRONG popup thành công!")
            time.sleep(3)
            
            # 11. Đợi thông báo "Posted" hoặc lỗi
            print("📍 Bước 11: Đợi thông báo kết quả (timeout 120s)...")
            try:
                # Đợi 1 trong 2: thông báo thành công hoặc thất bại
                WebDriverWait(self.driver, 120).until(
                    lambda d: d.find_elements(By.XPATH, "//div[normalize-space(text())='Posted']") or
                            d.find_elements(By.XPATH, "//div[normalize-space(text())='Post failed to upload']")
                )
                
                # Kiểm tra loại thông báo
                if self.driver.find_elements(By.XPATH, "//div[normalize-space(text())='Posted']"):
                    print("✅ Bài đã đăng thành công!")
                elif self.driver.find_elements(By.XPATH, "//div[normalize-space(text())='Post failed to upload']"):
                    print("❌ Đăng bài thất bại: Post failed to upload")
                
                time.sleep(2)
                
            except TimeoutException:
                print("❌ Timeout 120s: Không nhận được thông báo thành công hoặc lỗi!")

            # 8. Giữ trình duyệt mở để quan sát
            print("\n⏸ Giữ trình duyệt mở, không đóng...")
            print("👉 Bạn có thể kiểm tra nội dung và media đã upload trên Threads.")
            while True:
                time.sleep(10)

        except TimeoutException:
            print("❌ Không tìm thấy element trong thời gian chờ.")
        except Exception as e:
            print(f"❌ Lỗi không xác định: {e}")
            import traceback
            traceback.print_exc()


def test_click_post_and_upload():
    """Chạy thử chức năng click Post và upload media"""
    print("\n" + "=" * 60)
    print("🚀 RUNNING TEST: Click Post và Upload Media")
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
    test_click_post_and_upload()
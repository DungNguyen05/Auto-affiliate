import time
import sys
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.core.browser_manager import BrowserManager


class ThreadsPoster:
    """Post bài viết lên Threads với nội dung và media"""

    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.driver = browser_manager.driver

        if not self.driver:
            raise Exception("Browser chưa được khởi tạo!")

    def create_post(self, content_1, content_2=None, media_paths=None):
        """
        Tạo bài post trên Threads
        
        Args:
            content_1: Nội dung thread đầu tiên
            content_2: Nội dung thread thứ 2 (optional)
            media_paths: List đường dẫn file ảnh/video cần upload
        
        Returns:
            bool: True nếu thành công
        """
        print("\n" + "=" * 60)
        print("📝 BẮT ĐẦU TẠO POST TRÊN THREADS")
        print("=" * 60 + "\n")

        try:
            # 1. Mở trang Threads
            print("📍 Bước 1: Mở Threads...")
            self.driver.get("https://www.threads.net/")
            time.sleep(3)

            # 2. Click nút 'Post'
            print("📍 Bước 2: Click nút 'Post'...")
            post_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@role='button']//div[normalize-space(text())='Post']")
                )
            )
            post_button.click()
            print("✅ Đã click nút 'Post'!")
            time.sleep(2)

            # 3. Nhập nội dung thread 1
            print("📍 Bước 3: Nhập nội dung thread 1...")
            textbox = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[role="textbox"][contenteditable="true"]')
                )
            )
            
            self.driver.execute_script("""
                const box = arguments[0];
                const text = arguments[1];
                box.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, text);
                box.dispatchEvent(new Event('input', { bubbles: true }));
            """, textbox, content_1)
            print(f"✅ Đã nhập: {content_1[:80]}...")
            time.sleep(1)

            # 4. Upload media nếu có
            if media_paths and len(media_paths) > 0:
                print(f"\n📍 Bước 4: Upload {len(media_paths)} file media...")
                
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//input[@type='file']")
                    )
                )
                
                for i, media_path in enumerate(media_paths, 1):
                    if not Path(media_path).exists():
                        print(f"  ⚠️  File không tồn tại: {media_path}")
                        continue
                    
                    print(f"  📤 [{i}/{len(media_paths)}] Upload: {Path(media_path).name}")
                    file_input.send_keys(str(Path(media_path).absolute()))
                    time.sleep(2)
                
                print("✅ Đã upload tất cả media!")
                time.sleep(2)

            # 5. Thêm thread thứ 2 nếu có
            if content_2:
                print("\n📍 Bước 5: Thêm thread thứ 2...")
                
                add_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//span[normalize-space(text())='Add to thread']")
                    )
                )
                add_button.click()
                print("✅ Đã click 'Add to thread'!")
                time.sleep(2)
                
                print("📍 Bước 6: Nhập nội dung thread 2...")
                self.driver.execute_script("""
                    const text = arguments[0];
                    document.execCommand('insertText', false, text);
                    document.activeElement.dispatchEvent(new Event('input', { bubbles: true }));
                """, content_2)
                print(f"✅ Đã nhập: {content_2[:80]}...")
                time.sleep(2)

            # 6. Click nút "Post" để đăng bài
            print("\n📍 Bước cuối: Click nút 'Post' để đăng bài...")
            time.sleep(10)
            post_final_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//h1[.//span[normalize-space()='New thread']]/ancestor::div[@role='dialog']//div[@role='button']//div[normalize-space()='Post']"
                ))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", post_final_button)
            self.driver.execute_script("arguments[0].click();", post_final_button)
            print("✅ Đã click nút Post!")
            time.sleep(3)
            
            # 7. Đợi kết quả
            print("📍 Đợi kết quả đăng bài (timeout 120s)...")
            try:
                WebDriverWait(self.driver, 120).until(
                    lambda d: d.find_elements(By.XPATH, "//div[normalize-space(text())='Posted']") or
                            d.find_elements(By.XPATH, "//div[normalize-space(text())='Post failed to upload']")
                )
                
                # Kiểm tra kết quả
                if self.driver.find_elements(By.XPATH, "//div[normalize-space(text())='Post failed to upload']"):
                    print("\n" + "=" * 60)
                    print("❌ ĐĂNG BÀI THẤT BẠI!")
                    print("=" * 60 + "\n")
                    return False
                else:
                    print("\n" + "=" * 60)
                    print("✅ ĐĂNG BÀI THÀNH CÔNG (hoặc không có thông báo)!")
                    print("=" * 60 + "\n")
                    return True

                
            except TimeoutException:
                print("❌ Timeout: Không nhận được thông báo!")
                return False

        except TimeoutException as e:
            print(f"❌ Timeout: {e}")
            return False
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_poster():
    """Test đăng bài cơ bản"""
    print("\n" + "=" * 60)
    print("🧪 TEST THREADS POSTER")
    print("=" * 60 + "\n")

    browser = BrowserManager(headless=False)

    try:
        browser.init_driver()
        poster = ThreadsPoster(browser)
        
        # Test content
        content_1 = "🎉 Test post tự động!\nĐây là nội dung thread 1"
        content_2 = "💫 Thread 2 với link: https://example.com"
        
        # Test với media (nếu có)
        base_dir = Path(__file__).parent.parent.parent
        test_image = base_dir / "post_content" / "instagram_image.jpg"
        
        media_paths = []
        if test_image.exists():
            media_paths.append(test_image)
        
        success = poster.create_post(
            content_1=content_1,
            content_2=content_2,
            media_paths=media_paths
        )
        
        if success:
            print("✅ Test thành công!")
        else:
            print("❌ Test thất bại!")
        
        input("\nNhấn Enter để đóng...")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()


if __name__ == "__main__":
    test_poster()
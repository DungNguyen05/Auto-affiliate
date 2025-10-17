import time
import sys
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.core.browser_manager import BrowserManager


class ThreadsCrawler:
    """Crawl bài viết từ trang cá nhân Threads"""
    
    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.driver = browser_manager.driver
        
        if not self.driver:
            raise Exception("Browser chưa được khởi tạo!")
    
    def crawl_profile(self, profile_url):
        """
        Crawl bài viết đầu tiên từ trang cá nhân
        
        Args:
            profile_url: URL trang cá nhân threads (vd: https://www.threads.net/@cam_review08)
        
        Returns:
            dict: Bài viết đầu tiên {content, images, videos}
        """
        print(f"\n{'='*60}")
        print(f"🔍 Đang crawl: {profile_url}")
        print(f"{'='*60}\n")
        
        # Mở trang profile
        self.driver.get(profile_url)
        time.sleep(5)
        
        # Scroll để load bài
        print("📜 Đang scroll...")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Tìm tất cả container và lấy cái thứ 2
        print("📍 Tìm container thứ 2...")
        containers = self.driver.find_elements(
            By.CSS_SELECTOR, 
            'div.x78zum5.xdt5ytf.x1iyjqo2.x1n2onr6'
        )
        
        if len(containers) < 2:
            raise Exception(f"❌ Chỉ tìm thấy {len(containers)} container, cần ít nhất 2!")
        
        main_container = containers[1]  # Lấy container thứ 2 (index 1)
        
        # Lấy mục con đầu tiên (bài viết đầu tiên)
        first_post = main_container.find_element(By.CSS_SELECTOR, 'div.x78zum5.xdt5ytf')
        
        print(f"✅ Tìm thấy bài viết đầu tiên\n")
        
        # Extract content (lấy 2 elements đầu tiên, bỏ div cuối)
        content_1 = ""
        content_2 = ""
        try:
            text_spans = first_post.find_elements(
                By.CSS_SELECTOR, 
                'span.x1lliihq.x1plvlek.xryxfnj.x1n2onr6.xyejjpt.x15dsfln.xi7mnp6.x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x1i0vuye.xjohtrz.xo1l8bm.xp07o12.x1yc453h.xat24cr.xdj266r'
            )
            
            # Lấy content 1 (element đầu tiên)
            if len(text_spans) >= 1:
                parts = []
                for child in text_spans[0].find_elements(By.XPATH, './span | ./a'):
                    text = child.text.strip()
                    if text:
                        parts.append(text)
                    # Nếu là link, lấy thêm href
                    if child.tag_name == 'a':
                        href = child.get_attribute('href')
                        if href:
                            parts.append(f"({href})")
                content_1 = " ".join(parts)
            
            # Lấy content 2 (element thứ 2)
            if len(text_spans) >= 2:
                parts = []
                for child in text_spans[1].find_elements(By.XPATH, './span | ./a'):
                    text = child.text.strip()
                    if text:
                        parts.append(text)
                    # Nếu là link, lấy thêm href
                    if child.tag_name == 'a':
                        href = child.get_attribute('href')
                        if href:
                            parts.append(f"({href})")
                content_2 = " ".join(parts)
        except:
            pass
        
        # Extract images
        images = []
        try:
            img_elements = first_post.find_elements(By.TAG_NAME, 'img')
            images = [img.get_attribute('src') for img in img_elements if img.get_attribute('src')]
        except:
            pass
        
        # Extract videos
        videos = []
        try:
            video_elements = first_post.find_elements(By.TAG_NAME, 'video')
            videos = [vid.get_attribute('src') for vid in video_elements if vid.get_attribute('src')]
        except:
            pass
        
        post_data = {
            'content_1': content_1,
            'content_2': content_2,
            'images': images,
            'videos': videos
        }
        
        print(f"Content 1: {content_1[:50]}..." if len(content_1) > 50 else f"Content 1: {content_1}")
        print(f"Content 2: {content_2[:50]}..." if len(content_2) > 50 else f"Content 2: {content_2}")
        print(f"Images: {len(images)}")
        print(f"Videos: {len(videos)}\n")
        
        print(f"{'='*60}")
        print(f"✅ Crawl xong bài viết đầu tiên!")
        print(f"{'='*60}\n")
        
        return post_data


def test_crawler():
    """Test crawler"""
    
    target_url = "https://www.threads.net/@cam_review08"
    
    print("\n" + "="*60)
    print("🧪 TEST THREADS CRAWLER")
    print("="*60 + "\n")
    
    browser = BrowserManager(headless=False)
    
    try:
        browser.init_driver()
        crawler = ThreadsCrawler(browser)
        
        post = crawler.crawl_profile(target_url)
        
        # In kết quả
        print("\n📊 KẾT QUẢ CRAWL:\n")
        print(f"Content 1: {post['content_1']}")
        print(f"Content 2: {post['content_2']}")
        print(f"Images: {len(post['images'])}")
        print(f"Videos: {len(post['videos'])}")
        print()
        
        input("\nNhấn Enter để đóng browser...")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()


if __name__ == "__main__":
    test_crawler()
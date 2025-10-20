import time
import sys
import random
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import requests

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.core.browser_manager import BrowserManager


class ThreadsCrawler:
    """Crawl bài viết từ trang cá nhân Threads"""
    
    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.driver = browser_manager.driver
        
        if not self.driver:
            raise Exception("Browser chưa được khởi tạo!")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        
        # Khởi tạo ActionChains để mô phỏng chuột
        self.actions = ActionChains(self.driver)
    
    def human_like_mouse_move(self, element=None):
        """
        Mô phỏng di chuột tự nhiên như người dùng
        
        Args:
            element: Element để di chuột đến (optional)
        """
        try:
            if element:
                # Di chuột đến element với tốc độ tự nhiên
                self.actions.move_to_element(element).perform()
            else:
                # Di chuột random trong viewport
                viewport_width = self.driver.execute_script("return window.innerWidth")
                viewport_height = self.driver.execute_script("return window.innerHeight")
                
                # Tạo tọa độ random
                x = random.randint(100, viewport_width - 100)
                y = random.randint(100, viewport_height - 100)
                
                # Di chuột đến tọa độ random
                body = self.driver.find_element(By.TAG_NAME, 'body')
                self.actions.move_to_element_with_offset(body, x, y).perform()
            
            # Đợi random giống người thật
            time.sleep(random.uniform(0.3, 0.8))
            
        except Exception as e:
            pass  # Không cần báo lỗi, chỉ là mô phỏng
    
    def human_like_scroll(self, scroll_amount=None):
        """
        Mô phỏng scroll tự nhiên như người dùng
        
        Args:
            scroll_amount: Số pixel cần scroll (None = random)
        """
        if scroll_amount is None:
            scroll_amount = random.randint(300, 700)
        
        # Scroll từ từ, không scroll một lúc
        steps = random.randint(3, 6)
        scroll_per_step = scroll_amount // steps
        
        for _ in range(steps):
            self.driver.execute_script(f"window.scrollBy(0, {scroll_per_step});")
            time.sleep(random.uniform(0.1, 0.3))
        
        # Đợi thêm chút như người thật
        time.sleep(random.uniform(0.5, 1.2))
    
    def random_pause(self, min_sec=0.5, max_sec=2.0):
        """Dừng random để giống người thật"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def simulate_reading(self, element):
        """
        Mô phỏng đọc nội dung - di chuột qua element và dừng lại
        
        Args:
            element: Element cần "đọc"
        """
        try:
            # Di chuột đến element
            self.human_like_mouse_move(element)
            
            # Dừng lại như đang đọc (2-5 giây)
            time.sleep(random.uniform(2.0, 5.0))
            
            # Di chuột random nhẹ trong element
            for _ in range(random.randint(1, 3)):
                offset_x = random.randint(-50, 50)
                offset_y = random.randint(-20, 20)
                try:
                    self.actions.move_to_element_with_offset(element, offset_x, offset_y).perform()
                    time.sleep(random.uniform(0.3, 0.8))
                except:
                    pass
        except:
            pass
    
    def extract_shopee_link(self, redirect_url):
        """Extract link Shopee từ redirect URL"""
        print(f"\n  🔗 Xử lý link: {redirect_url[:80]}...")
        
        try:
            parsed = urlparse(redirect_url)
            params = parse_qs(parsed.query)
            
            if 'u' in params:
                real_url = unquote(params['u'][0])
            else:
                real_url = redirect_url
            
            time.sleep(random.uniform(0.8, 1.5))  # Random delay
            response = self.session.get(real_url, allow_redirects=True, timeout=10)
            final_url = response.url
            
            if 'shopee.vn' in final_url and 'captcha' not in final_url:
                print(f"  ✅ Lấy được: {final_url[:80]}...")
                return final_url
            
            return None
            
        except Exception as e:
            print(f"  ❌ Lỗi: {e}")
            return None
    
    def extract_media(self, post_element):
        """Extract video và image từ bài viết"""
        videos = []
        images = []
        
        try:
            media_elements = post_element.find_elements(
                By.CSS_SELECTOR,
                '.x1lliihq.x5yr21d.xh8yej3'
            )
            
            print(f"\n  🎬 Tìm thấy {len(media_elements)} media elements")
            
            for i, element in enumerate(media_elements, 1):
                tag_name = element.tag_name
                
                if tag_name == 'video':
                    video_src = element.get_attribute('src')
                    if video_src:
                        videos.append(video_src)
                        print(f"  ✅ Video {i}: {video_src}")
                
                elif tag_name == 'img':
                    img_src = element.get_attribute('src')
                    if img_src:
                        images.append(img_src)
                        print(f"  ✅ Image {i}: {img_src}")
        
        except Exception as e:
            print(f"  ❌ Lỗi extract media: {e}")
        
        return videos, images
    
    def scroll_until_post_loaded(self, post_index):
        """Scroll từ từ cho đến khi post tại index xuất hiện và không còn hidden"""
        print(f"\n  ⏬ Đang scroll để load bài viết {post_index + 1}...")
        
        max_attempts = 50
        for attempt in range(max_attempts):
            containers = self.driver.find_elements(
                By.CSS_SELECTOR, 
                'div.x78zum5.xdt5ytf.x1iyjqo2.x1n2onr6'
            )
            
            if len(containers) < 3:
                self.random_pause(0.8, 1.5)
                continue
            
            posts = containers[2].find_elements(By.CSS_SELECTOR, 'div.x78zum5.xdt5ytf')
            
            if len(posts) > post_index:
                post = posts[post_index]
                hidden_div = post.find_elements(By.CSS_SELECTOR, 'div[hidden]')
                
                if not hidden_div:
                    print(f"  ✅ Bài viết {post_index + 1} đã load xong!")
                    return True
            
            # Scroll tự nhiên thay vì dùng Keys.PAGE_DOWN
            self.human_like_scroll()
            
            # Random pause giữa các lần scroll
            self.random_pause(0.3, 0.8)
        
        print(f"  ⚠️ Timeout: Không load được bài {post_index + 1}")
        return False
    
    def crawl_profile(self, profile_url, limit):
        """
        Crawl nhiều bài viết từ trang cá nhân
        
        Args:
            profile_url: URL trang cá nhân
            limit: Số bài viết cần crawl
        
        Returns:
            list: Danh sách dict chứa thông tin bài viết
        """
        print(f"\n{'='*60}")
        print(f"🔍 Crawl: {profile_url}")
        print(f"🎯 Số bài cần crawl: {limit}")
        print(f"{'='*60}\n")
        
        self.driver.get(profile_url)
        
        # Đợi trang load và mô phỏng hành vi người dùng
        print("⏳ Đang load trang...")
        time.sleep(random.uniform(3, 5))
        
        # Di chuột random để giống người thật
        print("🖱️  Mô phỏng hành vi người dùng...")
        for _ in range(random.randint(2, 4)):
            self.human_like_mouse_move()
        
        # Scroll nhẹ lên xuống như người thật
        self.human_like_scroll(random.randint(100, 300))
        time.sleep(random.uniform(0.5, 1.0))
        self.driver.execute_script("window.scrollTo(0, 0);")  # Scroll về đầu
        time.sleep(random.uniform(1, 2))
        
        results = []
        
        for i in range(limit):
            post_index = i
            display_number = i + 1
            
            print(f"\n{'='*60}")
            print(f"📝 Crawl bài viết {display_number}/{limit}")
            print(f"{'='*60}")
            
            if not self.scroll_until_post_loaded(post_index):
                print(f"⚠️ Dừng lại ở bài {display_number - 1}")
                break
            
            containers = self.driver.find_elements(
                By.CSS_SELECTOR, 
                'div.x78zum5.xdt5ytf.x1iyjqo2.x1n2onr6'
            )
            
            if len(containers) < 3:
                print("❌ Không tìm thấy container!")
                break
            
            posts = containers[2].find_elements(By.CSS_SELECTOR, 'div.x78zum5.xdt5ytf')
            
            if len(posts) <= post_index:
                print("❌ Không còn bài viết!")
                break
            
            current_post = posts[post_index]
            
            # Mô phỏng đọc bài viết
            print("👀 Mô phỏng đọc bài viết...")
            self.simulate_reading(current_post)
            
            content_1 = ""
            content_2 = ""
            redirect_links = []
            
            try:
                text_spans = current_post.find_elements(
                    By.CSS_SELECTOR, 
                    'span.x1lliihq.x1plvlek.xryxfnj.x1n2onr6.xyejjpt.x15dsfln.xi7mnp6.x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x1i0vuye.xjohtrz.xo1l8bm.xp07o12.x1yc453h.xat24cr.xdj266r'
                )
                
                if len(text_spans) >= 1:
                    parts = []
                    for child in text_spans[0].find_elements(By.XPATH, './span | ./a'):
                        text = child.text.strip()
                        if text:
                            parts.append(text)
                        
                        if child.tag_name == 'a':
                            href = child.get_attribute('href')
                            if href and ('l.threads.com' in href or 'shopee.vn' in href):
                                redirect_links.append(href)
                    
                    content_1 = " ".join(parts)
                
                if len(text_spans) >= 2:
                    parts = []
                    for child in text_spans[1].find_elements(By.XPATH, './span | ./a'):
                        text = child.text.strip()
                        if text:
                            parts.append(text)
                        
                        if child.tag_name == 'a':
                            href = child.get_attribute('href')
                            if href and ('l.threads.com' in href or 'shopee.vn' in href):
                                redirect_links.append(href)
                    
                    content_2 = " ".join(parts)
            except:
                pass
            
            print(f"\n{'='*60}")
            print(f"🎬 Đang extract video/image...")
            print(f"{'='*60}")
            videos, images = self.extract_media(current_post)
            
            print(f"\n{'='*60}")
            print(f"🔗 Tìm thấy {len(redirect_links)} links")
            print(f"{'='*60}")
            
            shopee_links = []
            for link in redirect_links:
                shopee_link = self.extract_shopee_link(link)
                if shopee_link:
                    shopee_links.append(shopee_link)
            
            result = {
                'content_1': content_1,
                'content_2': content_2,
                'shopee_links': shopee_links,
                'videos': videos,
                'images': images
            }
            
            results.append(result)
            
            print(f"\n{'='*60}")
            print(f"📊 KẾT QUẢ BÀI {display_number}")
            print(f"{'='*60}")
            print(f"Content 1: {content_1[:100]}...")
            print(f"Content 2: {content_2[:100] if content_2 else 'None'}...")
            print(f"Shopee Links: {len(shopee_links)}")
            print(f"Videos: {len(videos)}")
            print(f"Images: {len(images)}")
            print(f"{'='*60}\n")
            
            # Pause random giữa các bài để tránh spam
            if i < limit - 1:
                pause_time = random.uniform(2, 5)
                print(f"⏸️  Nghỉ {pause_time:.1f}s trước khi crawl bài tiếp...")
                time.sleep(pause_time)
                
                # Di chuột random
                self.human_like_mouse_move()
        
        print(f"\n{'='*60}")
        print(f"✅ HOÀN THÀNH: Crawl được {len(results)} bài viết")
        print(f"{'='*60}\n")
        
        return results


def test_crawler():
    """Test crawler"""
    
    target_url = "https://www.threads.com/@cam_review08"
    
    print("\n" + "="*60)
    print("🧪 TEST THREADS CRAWLER")
    print("="*60 + "\n")
    
    browser = BrowserManager(headless=False)
    
    try:
        browser.init_driver()
        crawler = ThreadsCrawler(browser)
        posts = crawler.crawl_profile(target_url, limit=30)
        
        input("\nNhấn Enter để đóng...")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()


if __name__ == "__main__":
    test_crawler()
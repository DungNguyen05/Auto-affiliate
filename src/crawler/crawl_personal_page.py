import time
import sys
import random
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path
from selenium.webdriver.common.by import By
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
        
        # Session để follow redirect
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def extract_shopee_link(self, redirect_url):
        """Extract link Shopee từ redirect URL"""
        print(f"\n  🔗 Xử lý link: {redirect_url[:80]}...")
        
        try:
            # Parse URL để lấy link thật
            parsed = urlparse(redirect_url)
            params = parse_qs(parsed.query)
            
            if 'u' in params:
                real_url = unquote(params['u'][0])
            else:
                real_url = redirect_url
            
            # Follow redirect bằng requests
            time.sleep(random.uniform(0.5, 1.5))
            response = self.session.get(real_url, allow_redirects=True, timeout=10)
            final_url = response.url
            
            if 'shopee.vn' in final_url and 'captcha' not in final_url:
                print(f"  ✅ Lấy được: {final_url[:80]}...")
                return final_url
            
            return None
            
        except Exception as e:
            print(f"  ❌ Lỗi: {e}")
            return None
    
    def crawl_profile(self, profile_url):
        """
        Crawl bài viết đầu tiên từ trang cá nhân
        
        Returns:
            dict: {content_1, content_2, shopee_links}
        """
        print(f"\n{'='*60}")
        print(f"🔍 Crawl: {profile_url}")
        print(f"{'='*60}\n")
        
        # Mở trang
        self.driver.get(profile_url)
        time.sleep(5)
        
        # Scroll
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Tìm container thứ 2
        containers = self.driver.find_elements(
            By.CSS_SELECTOR, 
            'div.x78zum5.xdt5ytf.x1iyjqo2.x1n2onr6'
        )
        
        if len(containers) < 2:
            raise Exception(f"❌ Chỉ tìm thấy {len(containers)} container!")
        
        # Lấy bài viết đầu tiên
        first_post = containers[1].find_element(By.CSS_SELECTOR, 'div.x78zum5.xdt5ytf')
        
        # Extract content
        content_1 = ""
        content_2 = ""
        redirect_links = []
        
        try:
            text_spans = first_post.find_elements(
                By.CSS_SELECTOR, 
                'span.x1lliihq.x1plvlek.xryxfnj.x1n2onr6.xyejjpt.x15dsfln.xi7mnp6.x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x1i0vuye.xjohtrz.xo1l8bm.xp07o12.x1yc453h.xat24cr.xdj266r'
            )
            
            # Content 1
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
            
            # Content 2
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
        
        # Extract Shopee links
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
            'shopee_links': shopee_links
        }
        
        print(f"\n{'='*60}")
        print(f"📊 KẾT QUẢ")
        print(f"{'='*60}")
        print(f"Content 1: {content_1}")
        print(f"Content 2: {content_2}")
        print(f"Shopee Links: {len(shopee_links)}")
        for i, link in enumerate(shopee_links, 1):
            print(f"  {i}. {link}")
        print(f"{'='*60}\n")
        
        return result


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
        
        input("\nNhấn Enter để đóng...")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()


if __name__ == "__main__":
    test_crawler()
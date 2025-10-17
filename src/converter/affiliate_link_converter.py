import time
import sys
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add root directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import SHOPEE_AFFILIATE_URL
from src.core.browser_manager import BrowserManager


class ShopeeConverter:
    """Convert link Shopee thường thành link affiliate"""
    
    def __init__(self, browser_manager):
        """
        Args:
            browser_manager: Instance của BrowserManager đã init driver
        """
        self.browser = browser_manager
        self.driver = browser_manager.driver
        
        if not self.driver:
            raise Exception("Browser chưa được khởi tạo!")
    
    def convert_to_affiliate(self, shopee_url):
        """
        Convert link Shopee thường thành link affiliate
        
        Args:
            shopee_url (str): Link Shopee gốc
            
        Returns:
            str: Link affiliate hoặc None nếu thất bại
        """
        
        print(f"\n{'='*60}")
        print(f"🔄 Đang convert link: {shopee_url}")
        print(f"{'='*60}\n")
        
        try:
            # 1. Vào trang custom link
            print("📍 Bước 1: Mở trang affiliate...")
            self.driver.get(SHOPEE_AFFILIATE_URL)
            time.sleep(3)
            
            # 2. Tìm textarea và paste link
            print("📍 Bước 2: Tìm ô nhập link...")
            textarea = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@id='customLink_original_url']//textarea")
                )
            )
            
            # Clear và nhập link
            print("📍 Bước 3: Nhập link vào ô...")
            textarea.clear()
            time.sleep(0.5)
            textarea.send_keys(shopee_url)
            time.sleep(1)
            
            # 3. Click button "Lấy link"
            print("📍 Bước 4: Click nút 'Lấy link'...")
            get_link_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[span[text()='Lấy link']]")
                )
            )
            get_link_button.click()
            print("✅ Đã click!")
            
            # 4. Đợi modal hiện lên và lấy link affiliate
            print("📍 Bước 5: Đợi modal kết quả hiện lên...")
            
            try:
                # Đợi modal success hiện lên
                affiliate_textarea = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[contains(@class, 'ant-modal-content')]//div[@class='success-modal-content']//textarea")
                    )
                )
                
                # Lấy link từ textarea
                affiliate_link = affiliate_textarea.get_attribute('value')
                
                if affiliate_link and len(affiliate_link) > 0:
                    print(f"\n{'='*60}")
                    print(f"✅ THÀNH CÔNG!")
                    print(f"{'='*60}")
                    print(f"📥 Link gốc: {shopee_url}")
                    print(f"📤 Link affiliate: {affiliate_link}")
                    print(f"{'='*60}\n")
                    
                    # Đóng modal (optional - tìm nút close nếu cần)
                    try:
                        close_button = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-modal-content')]//button[contains(@class, 'ant-modal-close')]")
                        close_button.click()
                        time.sleep(0.5)
                    except:
                        pass  # Không sao nếu không tìm thấy nút close
                    
                    return affiliate_link
                else:
                    print("⚠️  Link affiliate trống!")
                    return None
                    
            except TimeoutException:
                print("❌ Timeout: Không thấy modal kết quả hiện lên!")
                print("💡 Có thể link không hợp lệ hoặc cần đợi lâu hơn")
                return None
        
        except TimeoutException as e:
            print(f"❌ Timeout: Không tìm thấy element - {e}")
            return None
            
        except NoSuchElementException as e:
            print(f"❌ Không tìm thấy element - {e}")
            return None
            
        except Exception as e:
            print(f"❌ Lỗi không xác định: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def convert_multiple(self, shopee_urls):
        """
        Convert nhiều link cùng lúc
        
        Args:
            shopee_urls (list): List các link Shopee
            
        Returns:
            dict: {original_url: affiliate_url}
        """
        results = {}
        
        print(f"\n🔄 Bắt đầu convert {len(shopee_urls)} links...\n")
        
        for i, url in enumerate(shopee_urls, 1):
            print(f"\n--- Link {i}/{len(shopee_urls)} ---")
            affiliate_link = self.convert_to_affiliate(url)
            results[url] = affiliate_link
            
            # Đợi giữa các lần convert để tránh spam
            if i < len(shopee_urls):
                time.sleep(2)
        
        return results


def test_converter():
    """Test function - Chạy thử converter"""
    
    # Link test (thay bằng link thật của bạn)
    test_url = "https://shopee.vn/%C3%81o-polo-nam-d%E1%BB%87t-kim-%C4%90%E1%BB%99c-menswear-v%E1%BA%A3i-m%E1%BB%81m-m%E1%BA%A1i-%C3%B4m-body-t%C3%B4n-d%C3%A1ng-phong-c%C3%A1ch-h%C3%A0n-qu%E1%BB%91c-PL288-i.74515356.42750833522?sp_atk=7c41f233-e80c-46ed-b7e1-2ca83e29931f&xptdk=7c41f233-e80c-46ed-b7e1-2ca83e29931f"
    
    print("\n" + "="*60)
    print("🧪 TEST SHOPEE CONVERTER")
    print("="*60 + "\n")
    
    # Khởi tạo browser
    browser = BrowserManager(headless=False)
    
    try:
        # Init driver
        browser.init_driver()
        
        # Khởi tạo converter
        converter = ShopeeConverter(browser)
        
        # Convert
        affiliate_link = converter.convert_to_affiliate(test_url)
        
        if affiliate_link:
            print("\n✅ Test thành công!")
        else:
            print("\n❌ Test thất bại!")
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        browser.close()


if __name__ == "__main__":
    test_converter()
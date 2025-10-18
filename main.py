import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.core.browser_manager import BrowserManager
from src.crawler.crawl_personal_page import ThreadsCrawler
from src.database.database import Database
from src.downloader.media_downloader import MediaDownloader
from src.poster.threads_poster import ThreadsPoster
from src.converter.affiliate_link_converter import ShopeeConverter
from src.utils.text_utils import replace_shopee_links


def main():
    """
    Luồng chính:
    1. Crawl bài viết từ trang cá nhân
    2. Lưu vào database
    3. Convert link Shopee thành affiliate
    4. Thay thế link trong content
    5. Tải media về local
    6. Upload lại lên Threads
    7. Xóa media tạm
    """
    
    print("\n" + "="*80)
    print("🚀 AUTO AFFILIATE THREADS - WORKFLOW CHÍNH")
    print("="*80 + "\n")
    
    # ====== CONFIG ======
    TARGET_PROFILE = "https://www.threads.com/@cam_review08"
    
    # ====== KHỞI TẠO ======
    browser = None
    db = Database()
    downloader = MediaDownloader()
    
    try:
        # 1. CRAWL BÀI VIẾT
        print("=" * 80)
        print("BƯỚC 1: CRAWL BÀI VIẾT TỪ TRANG CÁ NHÂN")
        print("=" * 80 + "\n")
        
        browser = BrowserManager(headless=False)
        browser.init_driver()
        
        crawler = ThreadsCrawler(browser)
        post_data = crawler.crawl_profile(TARGET_PROFILE)
        
        if not post_data:
            print("❌ Không crawl được bài viết!")
            return
        
        # 2. LƯU VÀO DATABASE
        print("\n" + "=" * 80)
        print("BƯỚC 2: LƯU BÀI VIẾT VÀO DATABASE")
        print("=" * 80 + "\n")
        
        # Kết hợp content_1 và content_2
        full_content = post_data['content_1']
        if post_data['content_2']:
            full_content += "\n\n" + post_data['content_2']
        
        post_id = db.save_post(
            content=full_content,
            images=post_data['images'],
            videos=post_data['videos'],
            shopee_links=post_data['shopee_links'],
            original_url=TARGET_PROFILE
        )
        
        if not post_id:
            print("⚠️  Bài viết đã tồn tại trong database, bỏ qua...")
            return
        
        print(f"✅ Đã lưu vào database với post_id={post_id}")
        
        # 2.5. CONVERT SHOPEE LINKS
        if post_data['shopee_links']:
            print("\n" + "=" * 80)
            print("BƯỚC 2.5: CONVERT SHOPEE LINKS THÀNH AFFILIATE")
            print("=" * 80 + "\n")
            
            converter = ShopeeConverter(browser)
            affiliate_links = []
            
            for shop_link in post_data['shopee_links']:
                aff_link = converter.convert_to_affiliate(shop_link)
                if aff_link:
                    affiliate_links.append(aff_link)
                    # Cập nhật vào database
                    db.update_affiliate_link(post_id, shop_link, aff_link)
                time.sleep(2)  # Đợi giữa các lần convert
            
            # Thay thế link trong content
            if affiliate_links:
                print("\n🔄 Thay thế link trong content...")
                post_data['content_1'] = replace_shopee_links(
                    post_data['content_1'], 
                    post_data['shopee_links'], 
                    affiliate_links
                )
                
                if post_data['content_2']:
                    post_data['content_2'] = replace_shopee_links(
                        post_data['content_2'], 
                        post_data['shopee_links'], 
                        affiliate_links
                    )
                
                print("✅ Đã thay thế link trong content!")
        
        # 3. TẢI MEDIA VỀ LOCAL
        print("\n" + "=" * 80)
        print("BƯỚC 3: TẢI MEDIA VỀ LOCAL")
        print("=" * 80 + "\n")
        
        downloaded_files = []
        
        # Tải videos trước (thường quan trọng hơn)
        if post_data['videos']:
            video_paths = downloader.download_videos(post_data['videos'])
            downloaded_files.extend(video_paths)
        
        # Tải images
        if post_data['images']:
            image_paths = downloader.download_images(post_data['images'])
            downloaded_files.extend(image_paths)
        
        if not downloaded_files:
            print("⚠️  Không có media để upload!")
        
        print(f"\n✅ Tổng cộng đã tải: {len(downloaded_files)} file")
        
        # 4. UPLOAD LÊN THREADS
        print("\n" + "=" * 80)
        print("BƯỚC 4: UPLOAD LẠI LÊN THREADS")
        print("=" * 80 + "\n")
        
        poster = ThreadsPoster(browser)
        
        success = poster.create_post(
            content_1=post_data['content_1'],
            content_2=post_data['content_2'] if post_data['content_2'] else None,
            media_paths=downloaded_files
        )
        
        if success:
            # Đánh dấu đã đăng trong DB
            db.mark_as_posted(post_id)
            print("✅ Đã đánh dấu bài viết là đã đăng!")
        else:
            print("⚠️  Upload thất bại, không đánh dấu đã đăng!")
        
        # 5. XÓA MEDIA TẠM
        print("\n" + "=" * 80)
        print("BƯỚC 5: XÓA MEDIA TẠM")
        print("=" * 80 + "\n")
        
        downloader.cleanup(downloaded_files)
        
        # THỐNG KÊ
        print("\n" + "=" * 80)
        print("📊 THỐNG KÊ DATABASE")
        print("=" * 80 + "\n")
        
        stats = db.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n" + "=" * 80)
        print("✅ HOÀN THÀNH WORKFLOW!")
        print("=" * 80 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Người dùng dừng chương trình!")
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # CLEANUP
        if browser:
            input("\nNhấn Enter để đóng browser...")
            browser.close()
        
        db.close()
        print("\n✅ Đã dọn dẹp tài nguyên!")


if __name__ == "__main__":
    main()
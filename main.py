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
    1. Crawl nhiều bài viết và lưu vào database
    2. Lấy bài chưa đăng từ database
    3. Convert link Shopee thành affiliate
    4. Tải media và đăng lên Threads
    """
    
    print("\n" + "="*80)
    print("🚀 AUTO AFFILIATE THREADS - WORKFLOW CHÍNH")
    print("="*80 + "\n")
    
    # ====== CONFIG ======
    TARGET_PROFILE = "https://www.threads.com/@cam_review08"
    CRAWL_LIMIT = 20  # Số bài viết cần crawl
    POST_LIMIT = 20   # Số bài viết cần đăng
    
    # ====== KHỞI TẠO ======
    browser = None
    db = Database()
    downloader = MediaDownloader()
    
    try:
        browser = BrowserManager(headless=False)
        browser.init_driver()
        
        # ===== GIAI ĐOẠN 1: CRAWL VÀ LƯU DATABASE =====
        print("=" * 80)
        print("GIAI ĐOẠN 1: CRAWL VÀ LƯU VÀO DATABASE")
        print("=" * 80 + "\n")
        
        crawler = ThreadsCrawler(browser)
        posts_data = crawler.crawl_profile(TARGET_PROFILE, limit=CRAWL_LIMIT)
        
        if not posts_data:
            print("❌ Không crawl được bài viết!")
            return
        
        # Lưu vào database
        print(f"\n💾 Đang lưu {len(posts_data)} bài viết vào database...")
        saved_count = 0
        
        for i, post_data in enumerate(posts_data, 1):
            print(f"\n--- Bài {i}/{len(posts_data)} ---")
            
            # Kết hợp content
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
            
            if post_id:
                saved_count += 1
                print(f"✅ Đã lưu post_id={post_id}")
            else:
                print("⚠️  Bài viết đã tồn tại, bỏ qua")
        
        print(f"\n✅ Đã lưu {saved_count}/{len(posts_data)} bài viết mới")
        
        # ===== GIAI ĐOẠN 2: LẤY BÀI CHƯA ĐĂNG VÀ UPLOAD =====
        print("\n" + "=" * 80)
        print("GIAI ĐOẠN 2: LẤY BÀI CHƯA ĐĂNG VÀ UPLOAD")
        print("=" * 80 + "\n")
        
        unposted = db.get_unposted_posts(limit=POST_LIMIT)
        
        if not unposted:
            print("⚠️  Không có bài viết nào chưa đăng!")
            return
        
        print(f"📋 Có {len(unposted)} bài viết chưa đăng")
        
        converter = ShopeeConverter(browser)
        poster = ThreadsPoster(browser)
        posted_count = 0
        
        for i, post in enumerate(unposted, 1):
            if posted_count >= POST_LIMIT:
                print(f"\n✅ Đã đăng đủ {POST_LIMIT} bài, dừng lại!")
                break
            
            print("\n" + "=" * 80)
            print(f"ĐĂNG BÀI {i}/{len(unposted)}")
            print("=" * 80 + "\n")
            
            post_id = post['id']
            content_parts = post['content'].split('\n\n', 1)
            content_1 = content_parts[0] if len(content_parts) > 0 else ""
            content_2 = content_parts[1] if len(content_parts) > 1 else None
            
            # Convert Shopee links
            affiliate_links = []
            if post['shopee_links']:
                print("🔄 Đang convert Shopee links...")
                for shop_link in post['shopee_links']:
                    aff_link = converter.convert_to_affiliate(shop_link)
                    if aff_link:
                        affiliate_links.append(aff_link)
                        db.update_affiliate_link(post_id, shop_link, aff_link)
                    time.sleep(2)
                
                # Thay thế link trong content
                if affiliate_links:
                    print("🔄 Thay thế link trong content...")
                    content_1 = replace_shopee_links(content_1, post['shopee_links'], affiliate_links)
                    if content_2:
                        content_2 = replace_shopee_links(content_2, post['shopee_links'], affiliate_links)
            
            # Tải media
            print("\n📥 Đang tải media...")
            downloaded_files = []
            
            if post['videos']:
                video_paths = downloader.download_videos(post['videos'])
                downloaded_files.extend(video_paths)
            
            if post['images']:
                image_paths = downloader.download_images(post['images'])
                downloaded_files.extend(image_paths)
            
            print(f"✅ Đã tải {len(downloaded_files)} file")
            
            # Đăng bài (luôn xem như thành công)
            print("\n📤 Đang đăng bài...")
            poster.create_post(
                content_1=content_1,
                content_2=content_2,
                media_paths=downloaded_files
            )
            
            # Tự động đánh dấu đã đăng
            db.mark_as_posted(post_id)
            posted_count += 1
            print(f"✅ Đã đánh dấu là đã đăng! ({posted_count}/{POST_LIMIT})")
            
            # Xóa media tạm
            downloader.cleanup(downloaded_files)
            
            # Đợi giữa các bài đăng
            if i < len(unposted):
                print("\n⏳ Đợi 10 giây trước khi đăng bài tiếp...")
                time.sleep(10)
        
        # THỐNG KÊ
        print("\n" + "=" * 80)
        print("📊 THỐNG KÊ")
        print("=" * 80 + "\n")
        
        stats = db.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print(f"\n✅ Đã đăng: {posted_count}/{POST_LIMIT} bài")
        
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
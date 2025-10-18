import time
import requests
from pathlib import Path


class MediaDownloader:
    """Tải video và ảnh từ URL về local"""
    
    def __init__(self, download_dir="data/temp_media"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def download_file(self, url):
        """
        Tải 1 file từ URL
        
        Args:
            url: URL của file
        
        Returns:
            Path của file đã tải hoặc None nếu thất bại
        """
        try:
            print(f"  📥 Đang tải: {url[:80]}...")
            
            # Tải file trước để lấy Content-Type
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Xác định extension từ Content-Type
            content_type = response.headers.get('Content-Type', '').lower()
            if 'video' in content_type or 'mp4' in content_type:
                ext = '.mp4'
            elif 'image/jpeg' in content_type or 'image/jpg' in content_type:
                ext = '.jpg'
            elif 'image/png' in content_type:
                ext = '.png'
            elif 'image/gif' in content_type:
                ext = '.gif'
            elif 'image/webp' in content_type:
                ext = '.webp'
            else:
                # Fallback: check URL
                if '.mp4' in url.lower() or '/video' in url.lower():
                    ext = '.mp4'
                elif '.jpg' in url.lower() or '.jpeg' in url.lower():
                    ext = '.jpg'
                elif '.png' in url.lower():
                    ext = '.png'
                else:
                    ext = '.jpg'  # default
            
            # Tạo tên file
            filename = f"{int(time.time())}_{hash(url) % 100000}{ext}"
            file_path = self.download_dir / filename
            
            # Lưu file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = file_path.stat().st_size / (1024 * 1024)
            print(f"  ✅ Đã tải: {file_path.name} ({file_size:.2f} MB)")
            
            return file_path
            
        except Exception as e:
            print(f"  ❌ Lỗi tải file: {e}")
            return None
    
    def download_images(self, image_urls):
        """
        Tải nhiều ảnh
        
        Returns:
            List[Path]: Danh sách đường dẫn file đã tải
        """
        downloaded = []
        
        print(f"\n📷 Đang tải {len(image_urls)} ảnh...")
        
        for i, url in enumerate(image_urls, 1):
            print(f"\n  [{i}/{len(image_urls)}]")
            file_path = self.download_file(url)
            if file_path:
                downloaded.append(file_path)
            time.sleep(0.5)
        
        print(f"\n✅ Đã tải {len(downloaded)}/{len(image_urls)} ảnh")
        return downloaded
    
    def download_videos(self, video_urls):
        """
        Tải nhiều video
        
        Returns:
            List[Path]: Danh sách đường dẫn file đã tải
        """
        downloaded = []
        
        print(f"\n🎬 Đang tải {len(video_urls)} video...")
        
        for i, url in enumerate(video_urls, 1):
            print(f"\n  [{i}/{len(video_urls)}]")
            file_path = self.download_file(url)
            if file_path:
                downloaded.append(file_path)
            time.sleep(1)
        
        print(f"\n✅ Đã tải {len(downloaded)}/{len(video_urls)} video")
        return downloaded
    
    def cleanup(self, file_paths):
        """
        Xóa các file đã tải
        
        Args:
            file_paths: List các Path cần xóa
        """
        print(f"\n🗑️  Đang xóa {len(file_paths)} file...")
        
        deleted = 0
        for file_path in file_paths:
            try:
                if file_path.exists():
                    file_path.unlink()
                    deleted += 1
                    print(f"  ✅ Đã xóa: {file_path.name}")
            except Exception as e:
                print(f"  ❌ Lỗi xóa {file_path.name}: {e}")
        
        print(f"\n✅ Đã xóa {deleted}/{len(file_paths)} file")
    
    def cleanup_all(self):
        """Xóa toàn bộ thư mục temp"""
        try:
            import shutil
            if self.download_dir.exists():
                shutil.rmtree(self.download_dir)
                self.download_dir.mkdir(parents=True, exist_ok=True)
                print("✅ Đã xóa toàn bộ temp media")
        except Exception as e:
            print(f"❌ Lỗi xóa thư mục: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TEST MEDIA DOWNLOADER")
    print("="*60 + "\n")
    
    downloader = MediaDownloader()
    
    # Test tải video từ Threads
    test_videos = [
        "https://instagram.fhan3-2.fna.fbcdn.net/o1/v/t16/f2/m84/AQPed2pXTJn4VKguqR03O9PDm_EpOBMSr6t0exEryfi4MMqgvSNLqYodlSCIv1ZozjIT9cUkJ-hr9hShUQI9aJ6087sVM3iHLuFkOEE.mp4?_nc_cat=107&_nc_oc=AdnWgC1dTOsBGNvN2P-RFFLHblgCY7HHRT-FVJoLcxQ7DyoDY5Brv2e1xhsUWwU0elJMQXk6vw8zYH-ya5WtZ7uW&_nc_sid=5e9851&_nc_ht=instagram.fhan3-2.fna.fbcdn.net&_nc_ohc=YsnwA87XF9QQ7kNvwFNhTnF&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0FST1VTRUxfSVRFTS5DMy43MjAuZGFzaF9iYXNlbGluZV8xX3YxIiwieHB2X2Fzc2V0X2lkIjo4MzgzNzQ1MTIyMDE5NjgsInZpX3VzZWNhc2VfaWQiOjEwMTY0LCJkdXJhdGlvbl9zIjo4LCJ1cmxnZW5fc291cmNlIjoid3d3In0%3D&ccb=17-1&vs=2e822a9fc38bbb3c&_nc_vs=HBksFQIYTGlnX2JhY2tmaWxsX3RpbWVsaW5lX3ZvZC9FQzRFMUI0MUExNDlBQURCRUQzM0FEMjhGQTgxREZCMl92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYOnBhc3N0aHJvdWdoX2V2ZXJzdG9yZS9HSWYyM2lHVTlpSmtXRU1GQU5NTXl2ZjdhTVlYYnNwVEFRQUYVAgLIARIAKAAYABsCiAd1c2Vfb2lsATEScHJvZ3Jlc3NpdmVfcmVjaXBlATEVAAAm4MPo7-if_QIVAigCQzMsF0AgZmZmZmZmGBJkYXNoX2Jhc2VsaW5lXzFfdjERAHXuB2XongEA&_nc_gid=vr3W1PzTWLoZCbWpr0fPvQ&_nc_zt=28&oh=00_AfdOQwzaZEJ7nSJlJeSHYIoyGDBRtM_lN6e2K8yIXxocAg&oe=68F52635"
    ]
    
    video_paths = downloader.download_videos(test_videos)
    
    # Test tải ảnh từ Threads
    test_images = [
        "https://instagram.fhan3-1.fna.fbcdn.net/v/t51.2885-15/565348651_17920335237174114_1574908666670039334_n.jpg?stp=dst-jpegr_e35_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InRocmVhZHMuQ0FST1VTRUxfSVRFTS5pbWFnZV91cmxnZW4uMTQ0MHgxOTIwLmhkci5mODI3ODcuZGVmYXVsdF9pbWFnZS5jMiJ9&_nc_ht=instagram.fhan3-1.fna.fbcdn.net&_nc_cat=106&_nc_oc=Q6cZ2QEcKy1kyUVdVEJZnD0GertFoPzOxk8xrDrHVyS6kdTc0w7fmRK54o7zH1oisAFhwJFjVFWKGH-3XaasKItRhwdO&_nc_ohc=xJopqSYG5AgQ7kNvwFOVITW&_nc_gid=vr3W1PzTWLoZCbWpr0fPvQ&edm=APs17CUBAAAA&ccb=7-5&ig_cache_key=Mzc0NTk4Mzk0NDU0NzI4OTYwMQ%3D%3D.3-ccb7-5&oh=00_AffWBtgkwtE4-w2BU9uRRPO3rh-EZ3yQ-pe2_Gr-Blvndg&oe=68F91A06&_nc_sid=10d13b&se=-1"
    ]
    
    image_paths = downloader.download_images(test_images)
    
    # Tổng hợp tất cả file đã tải
    all_files = video_paths + image_paths
    
    print(f"\n{'='*60}")
    print(f"✅ Đã tải tổng cộng: {len(all_files)} file")
    print(f"{'='*60}\n")
    
    # Test xóa
    input("\nNhấn Enter để xóa các file đã tải...")
    downloader.cleanup(all_files)
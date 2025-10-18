import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
import sys

# Add root directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class Database:
    """Quản lý database SQLite để lưu posts từ Threads"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # Tự động xác định đường dẫn từ root project
            root_dir = Path(__file__).parent.parent.parent
            db_path = root_dir / "data" / "threads_posts.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.connect()
        self.init_database()
    
    def connect(self):
        """Kết nối database, tạo file nếu chưa có"""
        self.conn = sqlite3.connect(self.db_path)
        print(f"✅ Đã kết nối database: {self.db_path}")
    
    def init_database(self):
        """Tạo các bảng nếu chưa tồn tại"""
        cursor = self.conn.cursor()
        
        # Bảng chính: lưu thông tin bài viết
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                original_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_posted INTEGER DEFAULT 0,
                posted_at TIMESTAMP
            )
        ''')
        
        # Bảng lưu ảnh
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                image_url TEXT NOT NULL,
                local_path TEXT,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
            )
        ''')
        
        # Bảng lưu video
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                video_url TEXT NOT NULL,
                local_path TEXT,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
            )
        ''')
        
        # Bảng lưu link Shopee
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shopee_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                original_link TEXT NOT NULL,
                affiliate_link TEXT,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
            )
        ''')
        
        # Tạo index để tăng tốc độ truy vấn
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON posts(content_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_posted ON posts(is_posted)')
        
        self.conn.commit()
        print(f"✅ Database schema đã sẵn sàng")
    
    def generate_content_hash(self, content):
        """Tạo hash từ content để phát hiện trùng lặp"""
        normalized = ' '.join(content.lower().strip().split())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def is_duplicate(self, content):
        """Kiểm tra bài viết đã tồn tại chưa (dựa vào content)"""
        content_hash = self.generate_content_hash(content)
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM posts WHERE content_hash = ?', (content_hash,))
        return cursor.fetchone() is not None
    
    def save_post(self, content, images=None, videos=None, shopee_links=None, 
                  original_url=None):
        """
        Lưu bài viết mới vào database
        
        Args:
            content: Nội dung bài viết
            images: List URL ảnh ['url1', 'url2', ...]
            videos: List URL video ['url1', 'url2', ...]
            shopee_links: List link Shopee ['link1', 'link2', ...]
            original_url: URL gốc của bài viết
        
        Returns:
            post_id nếu thành công, None nếu trùng lặp
        """
        if self.is_duplicate(content):
            print(f"⚠️  Bài viết đã tồn tại (duplicate content)")
            return None
        
        cursor = self.conn.cursor()
        content_hash = self.generate_content_hash(content)
        
        try:
            # 1. Insert post chính
            cursor.execute('''
                INSERT INTO posts (content_hash, content, original_url)
                VALUES (?, ?, ?)
            ''', (content_hash, content, original_url))
            
            post_id = cursor.lastrowid
            
            # 2. Insert images
            if images:
                for img_url in images:
                    cursor.execute('''
                        INSERT INTO post_images (post_id, image_url)
                        VALUES (?, ?)
                    ''', (post_id, img_url))
            
            # 3. Insert videos
            if videos:
                for vid_url in videos:
                    cursor.execute('''
                        INSERT INTO post_videos (post_id, video_url)
                        VALUES (?, ?)
                    ''', (post_id, vid_url))
            
            # 4. Insert Shopee links
            if shopee_links:
                for link in shopee_links:
                    cursor.execute('''
                        INSERT INTO shopee_links (post_id, original_link)
                        VALUES (?, ?)
                    ''', (post_id, link))
            
            self.conn.commit()
            print(f"✅ Đã lưu post_id={post_id}")
            return post_id
            
        except sqlite3.IntegrityError as e:
            print(f"❌ Lỗi trùng lặp: {e}")
            self.conn.rollback()
            return None
        except Exception as e:
            print(f"❌ Lỗi lưu database: {e}")
            self.conn.rollback()
            raise
    
    def get_post(self, post_id):
        """Lấy thông tin đầy đủ của 1 post"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        post = cursor.fetchone()
        
        if not post:
            return None
        
        cursor.execute('SELECT image_url, local_path FROM post_images WHERE post_id = ?', (post_id,))
        images = cursor.fetchall()
        
        cursor.execute('SELECT video_url, local_path FROM post_videos WHERE post_id = ?', (post_id,))
        videos = cursor.fetchall()
        
        cursor.execute('SELECT original_link, affiliate_link FROM shopee_links WHERE post_id = ?', (post_id,))
        shopee_links = cursor.fetchall()
        
        return {
            'id': post[0],
            'content': post[2],
            'original_url': post[3],
            'images': [img[0] for img in images],
            'videos': [vid[0] for vid in videos],
            'shopee_links': [link[0] for link in shopee_links],
            'affiliate_links': [link[1] for link in shopee_links if link[1]],
            'is_posted': post[5]
        }
    
    def get_unposted_posts(self, limit=10):
        """Lấy các bài chưa đăng"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id FROM posts 
            WHERE is_posted = 0 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        post_ids = [row[0] for row in cursor.fetchall()]
        return [self.get_post(pid) for pid in post_ids]
    
    def mark_as_posted(self, post_id):
        """Đánh dấu bài đã đăng"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE posts 
            SET is_posted = 1, posted_at = ?
            WHERE id = ?
        ''', (datetime.now(), post_id))
        self.conn.commit()
        print(f"✅ Đã đánh dấu post_id={post_id} là đã đăng")
    
    def update_affiliate_link(self, post_id, original_link, affiliate_link):
        """Cập nhật affiliate link sau khi convert"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE shopee_links 
            SET affiliate_link = ?
            WHERE post_id = ? AND original_link = ?
        ''', (affiliate_link, post_id, original_link))
        self.conn.commit()
        print(f"✅ Đã cập nhật affiliate link cho post_id={post_id}")
    
    def get_stats(self):
        """Thống kê database"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM posts')
        total_posts = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM posts WHERE is_posted = 1')
        posted = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM shopee_links')
        total_links = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM shopee_links WHERE affiliate_link IS NOT NULL')
        converted_links = cursor.fetchone()[0]
        
        return {
            'total_posts': total_posts,
            'posted': posted,
            'unposted': total_posts - posted,
            'total_shopee_links': total_links,
            'converted_links': converted_links
        }
    
    def close(self):
        """Đóng kết nối database"""
        if self.conn:
            self.conn.close()
            print("✅ Đã đóng database")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TEST DATABASE")
    print("="*60 + "\n")
    
    db = Database()
    
    # Test 1: Thêm post
    print("--- Test 1: Thêm post mới ---")
    post_id = db.save_post(
        content="Áo polo nam đẹp giá rẻ 🔥 Chất vải mềm mại, thoáng mát",
        images=["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
        videos=["https://example.com/video1.mp4"],
        shopee_links=[
            "https://shopee.vn/product1",
            "https://shopee.vn/product2"
        ],
        original_url="https://threads.net/@user/post/123"
    )
    
    # Test 2: Thêm post trùng lặp
    print("\n--- Test 2: Thêm post trùng lặp ---")
    duplicate_id = db.save_post(
        content="Áo polo nam đẹp giá rẻ 🔥 Chất vải mềm mại, thoáng mát",
        images=["https://different.com/img.jpg"]
    )
    
    # Test 3: Lấy thông tin post
    if post_id:
        print("\n--- Test 3: Lấy thông tin post ---")
        post_data = db.get_post(post_id)
        print(f"Content: {post_data['content']}")
        print(f"Images: {post_data['images']}")
        print(f"Videos: {post_data['videos']}")
        print(f"Shopee links: {post_data['shopee_links']}")
        
        # Test 4: Cập nhật affiliate link
        print("\n--- Test 4: Cập nhật affiliate link ---")
        db.update_affiliate_link(
            post_id,
            "https://shopee.vn/product1",
            "https://shope.ee/affiliate123"
        )
        
        # Test 5: Lấy post chưa đăng
        print("\n--- Test 5: Lấy posts chưa đăng ---")
        unposted = db.get_unposted_posts(limit=5)
        print(f"Số post chưa đăng: {len(unposted)}")
        
        # Test 6: Đánh dấu đã đăng
        print("\n--- Test 6: Đánh dấu đã đăng ---")
        db.mark_as_posted(post_id)
    
    # Test 7: Thống kê
    print("\n--- Test 7: Thống kê database ---")
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    db.close()
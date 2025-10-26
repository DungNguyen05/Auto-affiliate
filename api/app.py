import sys
from pathlib import Path
from flask import Flask
from flask_cors import CORS
import atexit

sys.path.append(str(Path(__file__).parent.parent))
from src.core.browser_manager import BrowserManager
from api.converter_service import ConverterService
from api.routes import api_bp, set_converter_service


# Khởi tạo Flask app
app = Flask(__name__)
CORS(app)  # Cho phép CORS

# Biến global
browser_manager = None
converter_service = None


def init_browser():
    """Khởi tạo browser và converter service"""
    global browser_manager, converter_service
    
    print("\n" + "="*60)
    print("🚀 KHỞI TẠO BROWSER CHO API SERVICE")
    print("="*60 + "\n")
    
    try:
        # Init browser (headless=False để debug, có thể đổi thành True)
        browser_manager = BrowserManager(headless=True)
        browser_manager.init_driver()
        
        # Init converter service
        converter_service = ConverterService(browser_manager)
        
        # Set service cho routes
        set_converter_service(converter_service)
        
        print("✅ Browser và Service đã sẵn sàng!\n")
        
    except Exception as e:
        print(f"❌ Lỗi khởi tạo browser: {e}")
        raise


def shutdown_browser():
    """Đóng browser khi shutdown server"""
    global browser_manager
    
    print("\n" + "="*60)
    print("🔒 ĐANG ĐÓNG BROWSER...")
    print("="*60 + "\n")
    
    if browser_manager:
        browser_manager.close()
        print("✅ Browser đã đóng!")


# Register blueprint
app.register_blueprint(api_bp)

# Register shutdown handler
atexit.register(shutdown_browser)


if __name__ == '__main__':
    # Khởi tạo browser trước khi start server
    init_browser()
    
    print("\n" + "="*60)
    print("🌐 FLASK SERVER ĐANG CHẠY")
    print("="*60)
    print("\n📍 Dashboard: http://localhost:5000")
    print("📍 API Health: http://localhost:5000/api/health")
    print("📍 API Convert: POST http://localhost:5000/api/convert")
    print("\n⚠️  Nhấn Ctrl+C để dừng server\n")
    
    # Chạy Flask server
    app.run(
        host='0.0.0.0',  # Cho phép access từ mạng LAN
        port=8000,
        debug=False  # Tắt debug để tránh reload làm mất browser session
    )
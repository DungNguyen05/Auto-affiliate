from flask import Blueprint, render_template, request, jsonify
import threading

# Tạo Blueprint
api_bp = Blueprint('api', __name__)

# Lock để tránh conflict khi nhiều request cùng lúc
conversion_lock = threading.Lock()

# Biến global để lưu converter_service (sẽ được set từ app.py)
converter_service = None


def set_converter_service(service):
    """Set converter service từ app.py"""
    global converter_service
    converter_service = service


@api_bp.route('/')
def index():
    """Trang chính - Dashboard"""
    return render_template('dashboard.html')


@api_bp.route('/api/convert', methods=['POST'])
def convert():
    """API convert link Shopee"""
    
    if not converter_service:
        return jsonify({
            'success': False,
            'error': 'Service chưa sẵn sàng'
        }), 500
    
    # Lấy data từ request
    data = request.get_json()
    
    if not data or 'shopee_url' not in data:
        return jsonify({
            'success': False,
            'error': 'Thiếu shopee_url trong request'
        }), 400
    
    shopee_url = data['shopee_url'].strip()
    
    if not shopee_url:
        return jsonify({
            'success': False,
            'error': 'Link không được để trống'
        }), 400
    
    # Convert với lock để tránh conflict
    with conversion_lock:
        result = converter_service.convert_link(shopee_url)
    
    # Trả về kết quả
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@api_bp.route('/api/health', methods=['GET'])
def health():
    """Kiểm tra trạng thái service"""
    return jsonify({
        'status': 'ok',
        'service_ready': converter_service is not None
    }), 200
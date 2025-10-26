import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from src.converter.affiliate_link_converter import ShopeeConverter


class ConverterService:
    """Service wrapper cho ShopeeConverter"""
    
    def __init__(self, browser_manager):
        self.converter = ShopeeConverter(browser_manager)
    
    def convert_link(self, shopee_url):
        """
        Convert link Shopee thành affiliate
        
        Returns:
            dict: {
                'success': bool,
                'affiliate_link': str (nếu thành công),
                'original_link': str,
                'error': str (nếu thất bại)
            }
        """
        try:
            # Gọi converter
            affiliate_link = self.converter.convert_to_affiliate(shopee_url)
            
            if affiliate_link:
                return {
                    'success': True,
                    'affiliate_link': affiliate_link,
                    'original_link': shopee_url
                }
            else:
                return {
                    'success': False,
                    'error': 'Không thể convert link. Vui lòng thử lại.',
                    'original_link': shopee_url
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Lỗi: {str(e)}',
                'original_link': shopee_url
            }
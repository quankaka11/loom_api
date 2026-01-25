"""
Flask API để crawl Loom transcripts bằng Selenium
"""

from flask import Flask, request, jsonify
from selenium_loom import SeleniumLoomCrawler
import traceback

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "Loom Transcript API"})

@app.route('/crawl', methods=['POST'])
def crawl_loom():
    """
    Crawl Loom video transcript
    
    Body JSON:
    {
        "url": "https://www.loom.com/share/..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'url' in request body"
            }), 400
        
        loom_url = data['url']
        
        print(f"📹 Crawling Loom video: {loom_url}")
        
        # Khởi tạo crawler
        crawler = SeleniumLoomCrawler(headless=True)
        
        try:
            # Crawl video
            result = crawler.crawl_loom_video(loom_url)
            
            return jsonify({
                "success": True,
                "transcript": result['transcript'],
                "metadata": result['metadata'],
                "crawled_at": result['crawled_at']
            })
            
        finally:
            # Đảm bảo đóng browser
            crawler.close_driver()
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    # Chạy API trên port 5000
    app.run(host='0.0.0.0', port=5000, debug=False)
"""
Firecrawl Loom Video Crawler
Crawl transcripts và thông tin từ Loom videos sử dụng Firecrawl API
"""

import os
import json
from datetime import datetime
from firecrawl import FirecrawlApp
from typing import Dict, Any, Optional


class LoomCrawler:
    """Class để crawl thông tin từ Loom videos"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Khởi tạo LoomCrawler
        
        Args:
            api_key: Firecrawl API key. Nếu không cung cấp, sẽ lấy từ biến môi trường FIRECRAWL_API_KEY
        """
        self.api_key = api_key or os.getenv('FIRECRAWL_API_KEY')
        if not self.api_key:
            raise ValueError("Firecrawl API key is required. Set FIRECRAWL_API_KEY environment variable or pass it to constructor.")
        
        self.app = FirecrawlApp(api_key=self.api_key)
        
    def crawl_loom_video(self, url: str, formats: list = None) -> Dict[str, Any]:
        """
        Crawl thông tin từ Loom video
        
        Args:
            url: URL của Loom video
            formats: Danh sách các format muốn lấy (markdown, html, rawHtml, links, screenshot)
                    Mặc định: ['markdown', 'html']
        
        Returns:
            Dictionary chứa toàn bộ thông tin đã crawl
        """
        if formats is None:
            formats = ['markdown', 'html']
        
        print(f"🔍 Đang crawl Loom video: {url}")
        print(f"📋 Formats: {', '.join(formats)}")
        
        try:
            # Scrape URL với các options
            result = self.app.scrape(
                url,
                formats=formats,
                only_main_content=True,  # Chỉ lấy nội dung chính
                wait_for=5000,  # Đợi 5 giây để trang load
            )
            
            print("✅ Crawl thành công!")
            return result
            
        except Exception as e:
            print(f"❌ Lỗi khi crawl: {str(e)}")
            raise
    
    def extract_vtt_url(self, html_content: str) -> Optional[str]:
        """
        Trích xuất URL của file VTT (captions) từ HTML
        
        Args:
            html_content: Nội dung HTML của trang
        
        Returns:
            URL của file VTT hoặc None nếu không tìm thấy
        """
        import re
        import html
        
        # Tìm URL VTT trong HTML (thường trong thẻ <track>)
        # Pattern: src="https://cdn.loom.com/mediametadata/captions/...vtt..."
        vtt_pattern = r'https://cdn\.loom\.com/mediametadata/captions/[^"]+\.vtt[^"]*'
        match = re.search(vtt_pattern, html_content)
        
        if match:
            url = match.group(0)
            # Decode HTML entities (&amp; -> &)
            url = html.unescape(url)
            return url
        
        return None
    
    def parse_vtt_content(self, vtt_content: str) -> str:
        """
        Parse nội dung file VTT để lấy transcript
        
        Args:
            vtt_content: Nội dung file VTT
        
        Returns:
            Transcript text đã được format
        """
        lines = vtt_content.split('\n')
        transcript_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Bỏ qua header WEBVTT
            if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
                continue
            
            # Bỏ qua timestamp lines (format: 00:00:00.000 --> 00:00:05.000)
            if '-->' in line:
                continue
            
            # Bỏ qua số thứ tự cue
            if line.isdigit():
                continue
            
            # Bỏ qua dòng trống
            if not line:
                continue
            
            # Thêm dòng text vào transcript
            transcript_lines.append(line)
        
        return ' '.join(transcript_lines)
    
    def download_vtt_transcript(self, vtt_url: str) -> str:
        """
        Download và parse file VTT transcript
        
        Args:
            vtt_url: URL của file VTT
        
        Returns:
            Transcript text
        """
        import requests
        
        try:
            print(f"📥 Đang tải transcript từ VTT: {vtt_url[:80]}...")
            
            # Thêm headers để giả lập browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.loom.com/',
                'Origin': 'https://www.loom.com'
            }
            
            response = requests.get(vtt_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            vtt_content = response.text
            transcript = self.parse_vtt_content(vtt_content)
            
            print(f"✅ Đã tải transcript thành công ({len(transcript)} ký tự)")
            return transcript
            
        except Exception as e:
            print(f"⚠️  Không thể tải VTT: {str(e)}")
            return ""
    
    def extract_transcript(self, crawl_result) -> str:
        """
        Trích xuất transcript từ kết quả crawl
        Ưu tiên lấy từ file VTT (captions) nếu có
        
        Args:
            crawl_result: Kết quả từ crawl_loom_video()
        
        Returns:
            Transcript text
        """
        # Thử lấy transcript từ file VTT trước
        html_content = getattr(crawl_result, 'html', '')
        
        if html_content:
            vtt_url = self.extract_vtt_url(html_content)
            if vtt_url:
                transcript = self.download_vtt_transcript(vtt_url)
                if transcript:
                    return transcript
        
        # Fallback: Lấy từ markdown nếu không có VTT
        print("⚠️  Không tìm thấy VTT, sử dụng markdown fallback")
        markdown = getattr(crawl_result, 'markdown', '')
        
        # Tìm phần transcript trong markdown
        if 'transcript' in markdown.lower():
            lines = markdown.split('\n')
            transcript_lines = []
            in_transcript = False
            
            for line in lines:
                if 'transcript' in line.lower():
                    in_transcript = True
                    continue
                if in_transcript:
                    transcript_lines.append(line)
            
            return '\n'.join(transcript_lines).strip()
        
        return markdown
    
    def extract_metadata(self, crawl_result) -> Dict[str, Any]:
        """
        Trích xuất metadata từ kết quả crawl
        
        Args:
            crawl_result: Kết quả từ crawl_loom_video()
        
        Returns:
            Dictionary chứa metadata
        """
        meta = getattr(crawl_result, 'metadata', {})
        
        metadata = {
            'title': getattr(meta, 'title', '') if meta else '',
            'description': getattr(meta, 'description', '') if meta else '',
            'url': getattr(meta, 'source_url', getattr(meta, 'sourceURL', '')) if meta else '',
            'language': getattr(meta, 'language', '') if meta else '',
            'keywords': getattr(meta, 'keywords', '') if meta else '',
            'author': getattr(meta, 'author', '') if meta else '',
            'og_title': getattr(meta, 'og_title', getattr(meta, 'ogTitle', '')) if meta else '',
            'og_description': getattr(meta, 'og_description', getattr(meta, 'ogDescription', '')) if meta else '',
            'og_image': getattr(meta, 'og_image', getattr(meta, 'ogImage', '')) if meta else '',
            'crawled_at': datetime.now().isoformat(),
        }
        
        return metadata
    
    def save_to_json(self, data: Dict[str, Any], output_file: str):
        """
        Lưu dữ liệu vào file JSON
        
        Args:
            data: Dữ liệu cần lưu
            output_file: Đường dẫn file output
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Đã lưu vào: {output_file}")
    
    def save_transcript_to_txt(self, transcript: str, output_file: str):
        """
        Lưu transcript vào file text
        
        Args:
            transcript: Nội dung transcript
            output_file: Đường dẫn file output
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(transcript)
        print(f"📝 Đã lưu transcript vào: {output_file}")
    
    def save_vtt_file(self, vtt_content: str, output_file: str):
        """
        Lưu file VTT gốc (có timestamp)
        
        Args:
            vtt_content: Nội dung VTT
            output_file: Đường dẫn file output
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(vtt_content)
        print(f"🎬 Đã lưu VTT file vào: {output_file}")
    
    def crawl_and_save(self, url: str, output_dir: str = './output'):
        """
        Crawl Loom video và lưu tất cả thông tin
        
        Args:
            url: URL của Loom video
            output_dir: Thư mục để lưu kết quả
        """
        # Tạo thư mục output nếu chưa có
        os.makedirs(output_dir, exist_ok=True)
        
        # Crawl video
        result = self.crawl_loom_video(url, formats=['markdown', 'html', 'rawHtml', 'links'])
        
        # Trích xuất thông tin
        transcript = self.extract_transcript(result)
        metadata = self.extract_metadata(result)
        
        # Tạo tên file từ timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Lưu file VTT gốc nếu có
        html_content = getattr(result, 'html', '')
        if html_content:
            vtt_url = self.extract_vtt_url(html_content)
            if vtt_url:
                try:
                    import requests
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': 'https://www.loom.com/'
                    }
                    vtt_response = requests.get(vtt_url, headers=headers, timeout=10)
                    vtt_response.raise_for_status()
                    self.save_vtt_file(vtt_response.text, os.path.join(output_dir, f'captions_{timestamp}.vtt'))
                except Exception as e:
                    print(f"⚠️  Không thể lưu VTT file: {str(e)}")
        
        # Lưu toàn bộ kết quả crawl
        full_result = {
            'metadata': metadata,
            'transcript': transcript,
            'markdown': getattr(result, 'markdown', ''),
            'html': getattr(result, 'html', ''),
            'links': getattr(result, 'links', []),
        }
        
        self.save_to_json(full_result, os.path.join(output_dir, f'loom_full_{timestamp}.json'))
        
        # Lưu riêng transcript
        self.save_transcript_to_txt(transcript, os.path.join(output_dir, f'transcript_{timestamp}.txt'))
        
        # Lưu riêng metadata
        self.save_to_json(metadata, os.path.join(output_dir, f'metadata_{timestamp}.json'))
        
        print("\n📊 Tóm tắt:")
        print(f"  - Title: {metadata['title']}")
        print(f"  - URL: {metadata['url']}")
        print(f"  - Transcript length: {len(transcript)} characters")
        print(f"  - Links found: {len(getattr(result, 'links', []))}")
        
        return full_result


def main():
    """Hàm chính để chạy crawler"""
    
    # URL của Loom video cần crawl
    LOOM_URL = "https://www.loom.com/share/52de32bd994e4c53a4ee5419ef33ddb6?sid=19145805-a451-474d-9209-8459616ee07d"
    
    # Khởi tạo crawler
    # Lưu ý: Bạn cần set biến môi trường FIRECRAWL_API_KEY
    # hoặc truyền trực tiếp: crawler = LoomCrawler(api_key="your-api-key")
    try:
        crawler = LoomCrawler(api_key="fc-4367c23f699e468594a8e1aec99f5f68")
        
        # Crawl và lưu thông tin
        result = crawler.crawl_and_save(LOOM_URL, output_dir='./loom_output')
        
        print("\n✨ Hoàn thành!")
        
    except ValueError as e:
        print(f"\n⚠️  {str(e)}")
        print("\n📝 Hướng dẫn:")
        print("   1. Đăng ký tài khoản tại: https://www.firecrawl.dev/")
        print("   2. Lấy API key từ dashboard")
        print("   3. Set biến môi trường:")
        print("      - Windows: set FIRECRAWL_API_KEY=your-api-key")
        print("      - Linux/Mac: export FIRECRAWL_API_KEY=your-api-key")
        print("   Hoặc truyền trực tiếp vào code:")
        print("      crawler = LoomCrawler(api_key='your-api-key')")
    
    except Exception as e:
        print(f"\n❌ Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

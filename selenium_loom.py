"""
Selenium Loom Video Crawler
Crawl transcripts và thông tin từ Loom videos sử dụng Selenium
"""

import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import Dict, Any


class SeleniumLoomCrawler:
    """Class để crawl thông tin từ Loom videos bằng Selenium"""
    
    def __init__(self, headless: bool = True):
        """
        Khởi tạo SeleniumLoomCrawler
        
        Args:
            headless: Chạy browser ẩn (True) hoặc hiển thị (False)
        """
        self.headless = headless
        self.driver = None
        
    def init_driver(self):
        """Khởi tạo Selenium WebDriver"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        # Essential options for running Chrome in server environment
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--remote-debugging-port=9222')
        
        # Try to find Chrome binary on the system
        chrome_binary_paths = [
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/snap/bin/chromium',
        ]
        
        for binary_path in chrome_binary_paths:
            if os.path.exists(binary_path):
                chrome_options.binary_location = binary_path
                print(f"✅ Found Chrome at: {binary_path}")
                break
        
        # Additional stability options
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Try to use system chromedriver first, then ChromeDriverManager as fallback
        try:
            # First, try system chromedriver (from apt.txt)
            if os.path.exists('/usr/bin/chromedriver'):
                service = Service('/usr/bin/chromedriver')
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ Using system chromedriver")
            else:
                # Fallback to ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ Using ChromeDriverManager")
        except Exception as e:
            print(f"⚠️  Error initializing driver: {str(e)}")
            # Last resort: try without explicit service
            self.driver = webdriver.Chrome(options=chrome_options)
        
        print("✅ Đã khởi tạo Chrome WebDriver")
    
    def close_driver(self):
        """Đóng WebDriver"""
        if self.driver:
            self.driver.quit()
            print("🔒 Đã đóng WebDriver")
    
    def crawl_loom_video(self, url: str) -> Dict[str, Any]:
        """
        Crawl thông tin từ Loom video
        
        Args:
            url: URL của Loom video
        
        Returns:
            Dictionary chứa toàn bộ thông tin đã crawl
        """
        if not self.driver:
            self.init_driver()
        
        print(f"🔍 Đang crawl Loom video: {url}")
        
        try:
            # Truy cập trang
            self.driver.get(url)
            
            # Đợi trang load
            wait = WebDriverWait(self.driver, 15)
            
            # Đợi video player xuất hiện
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "video")))
            print("✅ Trang đã load xong")
            
            # Lấy metadata
            metadata = self.extract_metadata()
            
            # Lấy transcript
            transcript = self.extract_transcript()
            
            result = {
                'metadata': metadata,
                'transcript': transcript,
                'url': url,
                'crawled_at': datetime.now().isoformat()
            }
            
            print("✅ Crawl thành công!")
            return result
            
        except Exception as e:
            print(f"❌ Lỗi khi crawl: {str(e)}")
            raise
    
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Trích xuất metadata từ trang
        
        Returns:
            Dictionary chứa metadata
        """
        metadata = {}
        
        try:
            # Lấy title
            title_element = self.driver.find_element(By.CSS_SELECTOR, "h1, [class*='title'], [class*='Title']")
            metadata['title'] = title_element.text.strip()
        except:
            metadata['title'] = ''
        
        try:
            # Lấy description từ meta tag
            desc_element = self.driver.find_element(By.CSS_SELECTOR, "meta[property='og:description']")
            metadata['description'] = desc_element.get_attribute('content')
        except:
            metadata['description'] = ''
        
        metadata['url'] = self.driver.current_url
        metadata['crawled_at'] = datetime.now().isoformat()
        
        return metadata
    
    def extract_transcript(self) -> str:
        """
        Trích xuất transcript từ trang Loom
        
        Returns:
            Transcript text
        """
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Tìm và click vào tab Transcript
            print("🔍 Đang tìm tab Transcript...")
            
            # Thử nhiều selector khác nhau
            transcript_selectors = [
                "//button[contains(text(), 'Transcript')]",
                "//div[contains(text(), 'Transcript')]",
                "//*[contains(@aria-label, 'Transcript')]",
                "//*[@data-testid='sidebar-tab-Transcript']",
            ]
            
            transcript_button = None
            for selector in transcript_selectors:
                try:
                    transcript_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if not transcript_button:
                print("⚠️  Không tìm thấy tab Transcript")
                return ""
            
            # Click vào tab Transcript
            print("👆 Click vào tab Transcript...")
            transcript_button.click()
            time.sleep(2)  # Đợi transcript load
            
            # Lấy nội dung transcript
            print("📝 Đang lấy nội dung transcript...")
            
            # Thử lấy từ các container có thể chứa transcript
            transcript_text = ""
            
            # Cách 1: Tìm các timestamp và text
            try:
                transcript_items = self.driver.find_elements(By.CSS_SELECTOR, "[class*='transcript'], [class*='caption']")
                if transcript_items:
                    texts = []
                    for item in transcript_items:
                        text = item.text.strip()
                        if text and len(text) > 5:  # Bỏ qua text quá ngắn
                            texts.append(text)
                    transcript_text = ' '.join(texts)
            except:
                pass
            
            # Cách 2: Lấy toàn bộ text từ sidebar
            if not transcript_text:
                try:
                    sidebar = self.driver.find_element(By.ID, "tab-content")
                    transcript_text = sidebar.text.strip()
                except:
                    pass
            
            # Cách 3: Lấy từ right panel
            if not transcript_text:
                try:
                    right_panel = self.driver.find_element(By.CSS_SELECTOR, "[class*='rightPanel'], [class*='sidebar']")
                    transcript_text = right_panel.text.strip()
                except:
                    pass
            
            if transcript_text:
                print(f"✅ Đã lấy transcript ({len(transcript_text)} ký tự)")
                return transcript_text
            else:
                print("⚠️  Không lấy được nội dung transcript")
                return ""
                
        except Exception as e:
            print(f"⚠️  Lỗi khi lấy transcript: {str(e)}")
            return ""
    
    def save_to_json(self, data: Dict[str, Any], output_file: str):
        """Lưu dữ liệu vào file JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Đã lưu vào: {output_file}")
    
    def save_transcript_to_txt(self, transcript: str, output_file: str):
        """Lưu transcript vào file text"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(transcript)
        print(f"📝 Đã lưu transcript vào: {output_file}")
    
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
        result = self.crawl_loom_video(url)
        
        # Tạo tên file từ timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Lưu toàn bộ kết quả
        self.save_to_json(result, os.path.join(output_dir, f'loom_selenium_{timestamp}.json'))
        
        # Lưu riêng transcript
        if result['transcript']:
            self.save_transcript_to_txt(result['transcript'], os.path.join(output_dir, f'transcript_selenium_{timestamp}.txt'))
        
        # Lưu riêng metadata
        self.save_to_json(result['metadata'], os.path.join(output_dir, f'metadata_selenium_{timestamp}.json'))
        
        print("\n📊 Tóm tắt:")
        print(f"  - Title: {result['metadata']['title']}")
        print(f"  - URL: {result['metadata']['url']}")
        print(f"  - Transcript length: {len(result['transcript'])} characters")
        
        return result


def main():
    """Hàm chính để chạy crawler"""
    
    # URL của Loom video cần crawl
    LOOM_URL = "https://www.loom.com/share/52de32bd994e4c53a4ee5419ef33ddb6?sid=19145805-a451-474d-9209-8459616ee07d"
    
    # Khởi tạo crawler
    crawler = SeleniumLoomCrawler(headless=True)
    
    try:
        # Crawl và lưu thông tin
        result = crawler.crawl_and_save(LOOM_URL, output_dir='./loom_output')
        
        print("\n✨ Hoàn thành!")
        
    except Exception as e:
        print(f"\n❌ Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Đóng browser
        crawler.close_driver()


if __name__ == "__main__":
    main()

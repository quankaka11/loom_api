# Loom Video Crawler với Firecrawl API

Script Python để crawl transcripts và toàn bộ thông tin từ Loom videos sử dụng Firecrawl API.

## 🚀 Tính năng

- ✅ Crawl transcript từ Loom video
- ✅ Trích xuất metadata (title, description, author, etc.)
- ✅ Lấy toàn bộ nội dung (markdown, HTML)
- ✅ Trích xuất tất cả links trong video
- ✅ Lưu kết quả dưới nhiều định dạng (JSON, TXT)
- ✅ Hỗ trợ tiếng Việt

## 📋 Yêu cầu

- Python 3.7+
- Firecrawl API key (đăng ký miễn phí tại [firecrawl.dev](https://www.firecrawl.dev/))

## 🔧 Cài đặt

1. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

2. **Cấu hình API key:**

Tạo file `.env` từ `.env.example`:
```bash
copy .env.example .env
```

Sau đó mở file `.env` và thay `your-api-key-here` bằng API key của bạn:
```
FIRECRAWL_API_KEY=fc-your-actual-api-key
```

**Hoặc** set biến môi trường trực tiếp:
```bash
# Windows (PowerShell)
$env:FIRECRAWL_API_KEY="fc-your-api-key"

# Windows (CMD)
set FIRECRAWL_API_KEY=fc-your-api-key

# Linux/Mac
export FIRECRAWL_API_KEY=fc-your-api-key
```

## 📖 Cách sử dụng

### Cách 1: Chạy script mặc định

```bash
python firecrawl_loom.py
```

Script sẽ crawl URL mặc định trong code và lưu kết quả vào thư mục `loom_output/`.

### Cách 2: Sử dụng như một module

```python
from firecrawl_loom import LoomCrawler

# Khởi tạo crawler
crawler = LoomCrawler()  # Lấy API key từ biến môi trường
# Hoặc: crawler = LoomCrawler(api_key="your-api-key")

# Crawl một video
url = "https://www.loom.com/share/your-video-id"
result = crawler.crawl_and_save(url, output_dir='./output')

# Hoặc chỉ crawl mà không lưu
crawl_result = crawler.crawl_loom_video(url)
transcript = crawler.extract_transcript(crawl_result)
metadata = crawler.extract_metadata(crawl_result)

print(f"Title: {metadata['title']}")
print(f"Transcript: {transcript[:200]}...")
```

### Cách 3: Crawl nhiều video

```python
from firecrawl_loom import LoomCrawler

crawler = LoomCrawler()

urls = [
    "https://www.loom.com/share/video1",
    "https://www.loom.com/share/video2",
    "https://www.loom.com/share/video3",
]

for url in urls:
    try:
        result = crawler.crawl_and_save(url, output_dir='./batch_output')
        print(f"✅ Crawled: {url}")
    except Exception as e:
        print(f"❌ Failed {url}: {e}")
```

## 📁 Cấu trúc output

Sau khi chạy, script sẽ tạo các file trong thư mục output:

```
loom_output/
├── loom_full_20260124_221530.json      # Toàn bộ dữ liệu
├── transcript_20260124_221530.txt      # Chỉ transcript
└── metadata_20260124_221530.json       # Chỉ metadata
```

### Nội dung file JSON đầy đủ:

```json
{
  "metadata": {
    "title": "Video title",
    "description": "Video description",
    "url": "https://...",
    "author": "Author name",
    "crawled_at": "2026-01-24T22:15:30"
  },
  "transcript": "Full transcript text...",
  "markdown": "Full markdown content...",
  "html": "Full HTML content...",
  "links": ["link1", "link2", ...]
}
```

## 🎯 Ví dụ với URL cụ thể

```python
from firecrawl_loom import LoomCrawler

# URL từ yêu cầu
url = "https://www.loom.com/share/52de32bd994e4c53a4ee5419ef33ddb6?sid=19145805-a451-474d-9209-8459616ee07d"

crawler = LoomCrawler()
result = crawler.crawl_and_save(url)

# Kết quả sẽ được lưu vào ./loom_output/
```

## 🔍 API Reference

### `LoomCrawler`

#### `__init__(api_key=None)`
Khởi tạo crawler với API key (tùy chọn, mặc định lấy từ biến môi trường).

#### `crawl_loom_video(url, formats=['markdown', 'html'])`
Crawl một Loom video và trả về kết quả đầy đủ.

**Parameters:**
- `url` (str): URL của Loom video
- `formats` (list): Danh sách format cần lấy

**Returns:** Dictionary chứa toàn bộ dữ liệu crawl

#### `extract_transcript(crawl_result)`
Trích xuất transcript từ kết quả crawl.

#### `extract_metadata(crawl_result)`
Trích xuất metadata từ kết quả crawl.

#### `crawl_and_save(url, output_dir='./output')`
Crawl video và tự động lưu tất cả thông tin vào files.

## ⚠️ Lưu ý

1. **API Key**: Bạn cần đăng ký tài khoản Firecrawl để lấy API key
2. **Rate Limits**: Firecrawl có giới hạn số lượng request tùy theo gói dịch vụ
3. **Transcript**: Một số video có thể không có transcript hoặc transcript được load động

## 🐛 Troubleshooting

### Lỗi: "Firecrawl API key is required"
- Đảm bảo bạn đã set biến môi trường `FIRECRAWL_API_KEY`
- Hoặc truyền API key trực tiếp: `LoomCrawler(api_key="your-key")`

### Lỗi: "Module not found: firecrawl"
```bash
pip install firecrawl-py
```

### Transcript trống hoặc không đầy đủ
- Một số video Loom load transcript qua JavaScript, có thể cần tăng `waitFor` parameter
- Thử crawl lại với `waitFor` lớn hơn

## 📚 Tài liệu tham khảo

- [Firecrawl Documentation](https://docs.firecrawl.dev/)
- [Firecrawl Python SDK](https://github.com/mendableai/firecrawl)

## 📝 License

MIT License - Free to use and modify


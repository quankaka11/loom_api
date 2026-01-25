# Loom Transcript API - Deployment Guide

API để crawl transcript từ Loom videos sử dụng Selenium.

## 🚀 Deploy lên Render

### Bước 1: Chuẩn bị Git Repository

```bash
# Khởi tạo git (nếu chưa có)
git init

# Thêm tất cả files
git add .

# Commit
git commit -m "Initial commit - Loom Transcript API"

# Tạo repository trên GitHub và push
git remote add origin https://github.com/YOUR_USERNAME/loom-transcript-api.git
git branch -M main
git push -u origin main
```

### Bước 2: Deploy trên Render

1. **Đăng nhập Render**: Truy cập https://render.com và đăng nhập
2. **Tạo Web Service mới**:
   - Click "New +" → "Web Service"
   - Connect GitHub repository của bạn
   - Chọn repository `loom-transcript-api`

3. **Cấu hình Service**:
   - **Name**: `loom-transcript-api` (hoặc tên bạn muốn)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium
     ```
   - **Start Command**: 
     ```bash
     gunicorn loom_api:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1
     ```
   - **Instance Type**: Chọn `Free` (hoặc plan phù hợp)

4. **Environment Variables** (Optional):
   - `PYTHON_VERSION`: `3.11.0`

5. **Click "Create Web Service"**

### Bước 3: Đợi Deploy

Render sẽ:
- Clone repository
- Cài đặt dependencies từ `requirements.txt`
- Cài đặt Chromium browser
- Khởi động ứng dụng

Quá trình này mất khoảng 5-10 phút.

## 📡 Sử dụng API

### Health Check

```bash
curl https://your-app-name.onrender.com/health
```

Response:
```json
{
  "status": "ok",
  "service": "Loom Transcript API"
}
```

### Crawl Loom Video

```bash
curl -X POST https://your-app-name.onrender.com/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.loom.com/share/YOUR_VIDEO_ID"
  }'
```

Response:
```json
{
  "success": true,
  "transcript": "Full transcript text...",
  "metadata": {
    "title": "Video Title",
    "description": "Video Description",
    "url": "https://www.loom.com/share/...",
    "crawled_at": "2026-01-25T11:55:25.123456"
  },
  "crawled_at": "2026-01-25T11:55:25.123456"
}
```

## 🔧 Local Development

### Cài đặt

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Cài đặt Chrome driver (nếu chưa có)
# Download từ: https://chromedriver.chromium.org/
```

### Chạy local

```bash
python loom_api.py
```

API sẽ chạy tại: `http://localhost:5000`

## ⚠️ Lưu ý

1. **Free Tier Render**:
   - Service sẽ sleep sau 15 phút không hoạt động
   - Request đầu tiên sau khi sleep sẽ mất ~30s để wake up
   - Giới hạn 750 giờ/tháng

2. **Timeout**:
   - Mỗi request crawl mất khoảng 20-40 giây
   - Đã set timeout 120s cho gunicorn

3. **Rate Limiting**:
   - Nên implement rate limiting nếu dùng production
   - Tránh crawl quá nhiều video cùng lúc

## 🐛 Troubleshooting

### Chrome không khởi động được
- Kiểm tra logs trên Render Dashboard
- Đảm bảo đã cài đặt `playwright install-deps chromium`

### Timeout khi crawl
- Tăng timeout trong gunicorn command
- Kiểm tra URL Loom có hợp lệ không

### Memory issues
- Upgrade instance type trên Render
- Giảm số workers xuống 1

## 📝 Files Structure

```
Loom/
├── loom_api.py           # Flask API
├── selenium_loom.py      # Selenium crawler
├── requirements.txt      # Python dependencies
├── render.yaml          # Render configuration
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🔗 Links

- Render Dashboard: https://dashboard.render.com
- API Documentation: (Your API URL)/health

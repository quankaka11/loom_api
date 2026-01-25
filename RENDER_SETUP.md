# 🚀 Hướng dẫn Deploy lên Render - QUAN TRỌNG

## ⚠️ Lỗi hiện tại
Build command trên Render Dashboard vẫn chứa lệnh `playwright` cũ. Bạn cần cập nhật lại.

## 📋 Các bước thực hiện

### Bước 1: Truy cập Render Dashboard
1. Đăng nhập vào https://dashboard.render.com
2. Tìm service **loom-transcript-api** (hoặc tên bạn đã đặt)
3. Click vào service đó

### Bước 2: Cập nhật Build Command
1. Trong trang service, tìm phần **Settings** (hoặc **Environment**)
2. Tìm mục **Build Command**
3. **XÓA** build command cũ (có chứa `playwright`)
4. **THAY BẰNG** build command mới:

```bash
pip install -r requirements.txt
```

**QUAN TRỌNG**: Chỉ cần dòng này thôi, KHÔNG thêm gì khác!

### Bước 3: Cập nhật Start Command (nếu cần)
Đảm bảo **Start Command** là:

```bash
gunicorn loom_api:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1
```

### Bước 4: Lưu và Deploy lại
1. Click **Save Changes**
2. Click **Manual Deploy** → **Deploy latest commit**
3. Đợi khoảng 3-5 phút

## ✅ Kiểm tra Deploy thành công

Sau khi deploy xong, bạn sẽ thấy:
- ✅ Build completed successfully
- ✅ Service is live

### Test API:

**Health Check:**
```bash
curl https://your-app-name.onrender.com/health
```

Kết quả mong đợi:
```json
{
  "status": "ok",
  "service": "Loom Transcript API"
}
```

**Crawl Video:**
```bash
curl -X POST https://your-app-name.onrender.com/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.loom.com/share/52de32bd994e4c53a4ee5419ef33ddb6"
  }'
```

## 🔧 Cấu hình chi tiết trên Render Dashboard

### Environment Variables (Optional)
Không cần thiết lập gì thêm, nhưng nếu muốn có thể thêm:
- `PYTHON_VERSION`: `3.11.0`

### Instance Type
- **Free**: Đủ để test, nhưng sẽ sleep sau 15 phút không dùng
- **Starter ($7/month)**: Không sleep, tốt hơn cho production

## 🐛 Troubleshooting

### Lỗi: "playwright: command not found"
➡️ **Giải pháp**: Cập nhật Build Command như hướng dẫn ở Bước 2

### Lỗi: "ChromeDriver not found"
➡️ **Giải pháp**: Đã fix bằng `webdriver-manager` trong code, không cần làm gì thêm

### Lỗi: Timeout khi crawl
➡️ **Giải pháp**: 
- Kiểm tra URL Loom có hợp lệ không
- Tăng timeout trong Start Command lên `--timeout 180`

### Service sleep (Free tier)
➡️ **Giải pháp**: 
- Request đầu tiên sau khi sleep sẽ mất ~30s
- Upgrade lên Starter plan để tránh sleep

## 📝 Tóm tắt các file quan trọng

```
Loom/
├── loom_api.py              # Flask API
├── selenium_loom.py         # Selenium crawler (đã update)
├── requirements.txt         # Dependencies (đã update)
├── render.yaml             # Render config (tham khảo)
├── Procfile                # Process config (tham khảo)
└── RENDER_SETUP.md         # File này
```

## 🎯 Checklist Deploy

- [ ] Code đã push lên GitHub
- [ ] Đã cập nhật Build Command trên Render Dashboard
- [ ] Đã cập nhật Start Command trên Render Dashboard
- [ ] Đã click "Manual Deploy"
- [ ] Đợi build xong (3-5 phút)
- [ ] Test `/health` endpoint
- [ ] Test `/crawl` endpoint với Loom URL

## 🔗 Links hữu ích

- Render Dashboard: https://dashboard.render.com
- GitHub Repo: https://github.com/quankaka11/loom_api
- Render Docs: https://render.com/docs

---

**Lưu ý**: Sau khi cập nhật Build Command, nhớ click **Manual Deploy** để deploy lại với cấu hình mới!

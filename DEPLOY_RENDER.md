# Hướng Dẫn Deploy Bot Lên Render

## Bước 1: Chuẩn Bị File

Đã tạo các file cần thiết:
- ✅ `n.py` - Bot code (đã cập nhật dùng env variables)
- ✅ `requirements.txt` - Dependencies

## Bước 2: Tạo GitHub Repository (Nếu chưa có)

1. Tạo repository mới trên GitHub
2. Upload các file sau:
   - `n.py`
   - `requirements.txt`

## Bước 3: Tạo Web Service Trên Render

1. Vào https://render.com và đăng nhập
2. Click **"New +"** → chọn **"Web Service"** (QUAN TRỌNG!)
3. Connect GitHub repository của bạn
4. Điền thông tin:
   - **Name**: `bongx-bot` hoặc tên bạn muốn
   - **Region**: Singapore (gần Việt Nam nhất)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python n.py`
   - **Plan**: Free

> ✅ **Bot đã tích hợp web server** nên sẽ chạy 24/7 không ngủ!

## Bước 4: Cấu Hình Environment Variables

Trong phần **Environment Variables**, thêm:

```
BOT_TOKEN = 8241173486:AAEfmZ4pwqIq7L4vaWidg0i7OQfSTqh5AIY
```

> ⚠️ **Quan trọng**: Đừng để BOT_TOKEN public trên GitHub!

## Bước 5: Deploy

1. Click **"Create Web Service"**
2. Đợi Render build và deploy (2-3 phút)
3. Bot sẽ tự động chạy 24/7

## Bước 6: Kiểm Tra

- Vào tab **"Logs"** để xem bot có chạy không
- Thử gửi `/start` cho bot trên Telegram
- Nếu thấy log "BOT BÓNG X ĐANG CHẠY..." là thành công!

## Lưu Ý Quan Trọng

✅ **Bot Chạy 24/7**:
- Bot đã tích hợp Flask web server
- Render sẽ giữ bot hoạt động liên tục
- Không cần UptimeRobot hay công cụ ping khác
- Free plan: 750 giờ/tháng (đủ dùng cả tháng!)

🌐 **Truy Cập Web Interface**:
- URL: `https://your-app-name.onrender.com`
- Xem trạng thái bot đẹp mắt
- Health check: `https://your-app-name.onrender.com/health`

💡 **Khuyến nghị**:
- Bot sẽ tự động chạy liên tục
- Không cần cấu hình thêm gì
- Nâng cấp lên Paid Plan ($7/tháng) nếu cần nhiều tài nguyên hơn

## Troubleshooting

### Bot không chạy?
1. Kiểm tra Logs trên Render
2. Đảm bảo `BOT_TOKEN` đã set đúng trong Environment Variables
3. Kiểm tra Build Command và Start Command

### Bot bị conflict?
- Chỉ chạy 1 instance duy nhất
- Tắt bot local trước khi deploy Render

## Support

Nếu cần hỗ trợ gì thêm, hãy hỏi nhé! 🚀

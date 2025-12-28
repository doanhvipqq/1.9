import telebot
import requests
import time
import threading
import os
from flask import Flask

# ==============================================================
# CẤU HÌNH BOT
# ==============================================================
# Lấy token từ biến môi trường (bảo mật cho Render)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8241173486:AAEfmZ4pwqIq7L4vaWidg0i7OQfSTqh5AIY")

# Cấu hình Bóng X
BONGX_SITE_KEY = "6LeEge4rAAAAAPJ7vKCvI9-DcHBNh7B_92UcK2y6"
BONGX_PAGE_URL = "https://meobypass.com/" 

bot = telebot.TeleBot(BOT_TOKEN)

# ==============================================================
# 1. CLASS GIẢI CAPTCHA
# ==============================================================
class CaptchaSolver:
    @staticmethod
    def solve_recaptchav2(page_url, site_key, api_key):
        try:
            # Tạo Task giải Captcha
            r = requests.get("https://anticaptcha.top/in.php", params={
                "key": api_key, 
                "method": "userrecaptcha", 
                "googlekey": site_key, 
                "pageurl": page_url, 
                "json": "1"
            }, timeout=30)
            
            try: resp = r.json()
            except: return None, "API Key sai hoặc Web lỗi."

            if resp.get("status") != 1:
                return None, f"Lỗi Key: {resp.get('request', 'Unknown')}"
            
            task_id = resp["request"]
            
            # Đợi kết quả
            for _ in range(60): 
                time.sleep(3)
                r2 = requests.get("https://anticaptcha.top/res.php", params={
                    "key": api_key, "action": "get", "id": task_id, "json": "1"
                }, timeout=30)
                resp2 = r2.json()
                if resp2["status"] == 1:
                    return resp2["request"], "Success"
                if resp2.get("request") != "CAPCHA_NOT_READY": 
                    return None, "Lỗi khi chờ kết quả."
        except Exception as e: 
            return None, str(e)
        return None, "Timeout."

# ==============================================================
# 2. LOGIC BYPASS
# ==============================================================
def bypass_logic(target_url, captcha_token, status_callback):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": BONGX_PAGE_URL,
    })
    api_submit = "https://api.meobypass.click/public/bypass"
    
    try:
        status_callback("🔵 **Đang kết nối**\n📡 Gửi dữ liệu lên Server Bóng X...")
        r = session.get(api_submit, params={"url": target_url, "captcha": captcha_token}, timeout=30)
        data = r.json()
        
        task_id = data.get("task_id")
        if not task_id:
            if data.get("status") == "success": return data.get("result"), "Success"
            return None, f"Lỗi lấy Task ID: {data.get('message')}"

        status_callback(f"🔵 **Đang xử lý**\n⏳ Task ID: `{task_id}`\n⚙️ Vui lòng chờ...")
        
        for i in range(120):
            time.sleep(1)
            try:
                r_check = session.get(f"https://api.meobypass.click/taskid/{task_id}", timeout=10)
                d_check = r_check.json()
                status = d_check.get("status")
                
                if status == "success": return d_check.get("result"), "Success"
                elif status in ["error", "fail"]: return None, d_check.get("message")
                
                if i % 5 == 0: 
                    progress = "▓" * (i // 10) + "░" * (12 - i // 10)
                    status_callback(f"🟡 **Đang xử lý** ({i}s)\n{progress}\n📊 Trạng thái: `{status}`")
            except: continue
        return None, "Timeout."
    except Exception as e: return None, str(e)

# ==============================================================
# 3. XỬ LÝ BOT TELEGRAM (LUỒNG HỎI KEY)
# ==============================================================

# Hàm chạy thread xử lý (được gọi sau khi đã có Link và Key)
def run_bypass_thread(message, url, api_key, key_msg_id):
    chat_id = message.chat.id
    chat_type = message.chat.type  # 'private', 'group', or 'supergroup'
    
    # 🔒 XÓA TIN NHẮN CHỨA API KEY ĐỂ BẢO MẬT (Cả Private và Group Chat)
    deleted_successfully = False
    try:
        bot.delete_message(chat_id, key_msg_id)
        deleted_successfully = True
        
        # Thông báo khác nhau cho private chat và group chat
        if chat_type == 'private':
            security_msg = bot.send_message(
                chat_id, 
                "🔒 **Bảo mật:**\n✅ Tin nhắn chứa API Key đã được xóa tự động!",
                parse_mode="Markdown"
            )
        else:  # group or supergroup
            security_msg = bot.send_message(
                chat_id, 
                "🔒 **Bảo mật nhóm:**\n✅ Tin nhắn API Key đã xóa tự động!\n💡 Bot đã có quyền xóa tin nhắn",
                parse_mode="Markdown",
                reply_to_message_id=message.message_id
            )
        
        time.sleep(2)
        bot.delete_message(chat_id, security_msg.message_id)
    except Exception as e:
        # Nếu không xóa được (thiếu quyền trong group)
        if chat_type in ['group', 'supergroup'] and not deleted_successfully:
            try:
                warning_msg = bot.send_message(
                    chat_id,
                    "⚠️ **CẢNH BÁO BẢO MẬT:**\n"
                    "Bot không có quyền xóa tin nhắn trong nhóm!\n\n"
                    "🔧 **Cách khắc phục:**\n"
                    "1️⃣ Vào Group Settings → Administrators\n"
                    "2️⃣ Chọn bot trong danh sách\n"
                    "3️⃣ Bật quyền 'Delete Messages'\n\n"
                    "🔒 Hoặc sử dụng bot trong chat riêng để bảo mật hơn!",
                    parse_mode="Markdown",
                    reply_to_message_id=message.message_id
                )
                time.sleep(6)
                try:
                    bot.delete_message(chat_id, warning_msg.message_id)
                except:
                    pass
            except:
                pass
    
    msg_status = bot.send_message(chat_id, "━━━━━━━━━━━━━━━━━━\n🚀 **BẮT ĐẦU XỬ LÝ**\n━━━━━━━━━━━━━━━━━━", parse_mode="Markdown")

    def update_status(text):
        try: bot.edit_message_text(f"━━━━━━━━━━━━━━━━━━\n{text}\n━━━━━━━━━━━━━━━━━━", chat_id, msg_status.message_id, parse_mode="Markdown")
        except: pass 

    # 1. Giải Captcha
    update_status("🤖 **ĐANG GIẢI CAPTCHA**\n⏰ Vui lòng đợi trong giây lát...")
    token, cap_msg = CaptchaSolver.solve_recaptchav2(BONGX_PAGE_URL, BONGX_SITE_KEY, api_key)

    if not token:
        update_status(f"🔴 **LỖI CAPTCHA**\n\n❌ Chi tiết: `{cap_msg}`\n\n💡 Kiểm tra lại API Key và thử lại!")
        return

    update_status("🟢 **CAPTCHA HOÀN TẤT**\n✅ Token đã được lấy thành công!")
    time.sleep(1)

    # 2. Bypass
    result_link, bypass_msg = bypass_logic(url, token, update_status)

    if result_link:
        bot.delete_message(chat_id, msg_status.message_id)
        success_msg = (
            "━━━━━━━━━━━━━━━━━━\n"
            "🟢 **THÀNH CÔNG!**\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🔗 **Link kết quả:**\n`{result_link}`\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "✨ Chúc bạn sử dụng vui vẻ!"
        )
        bot.send_message(chat_id, success_msg, parse_mode="Markdown")
    else:
        update_status(f"🔴 **THẤT BẠI**\n\n❌ Lỗi: `{bypass_msg}`\n\n💡 Vui lòng thử lại sau!")

# BƯỚC 2: NHẬN KEY TỪ NGƯỜI DÙNG
def step_receive_key(message, target_url):
    api_key = message.text.strip()
    key_msg_id = message.message_id
    
    # Kiểm tra sơ bộ key
    if len(api_key) < 10:
        bot.reply_to(message, "━━━━━━━━━━━━━━━━━━\n🔴 **LỖI**\n━━━━━━━━━━━━━━━━━━\n\n❌ API Key quá ngắn!\n💡 Vui lòng gửi lại link để thử lại.", parse_mode="Markdown")
        return

    # Chạy thread xử lý
    threading.Thread(target=run_bypass_thread, args=(message, target_url, api_key, key_msg_id)).start()

# LỆNH /start - WELCOME MESSAGE
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "━━━━━━━━━━━━━━━━━━\n"
        "🤖 **BOT BÓNG X**\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "👋 Xin chào! Tôi là bot hỗ trợ bypass link.\n\n"
        "📋 **HƯỚNG DẪN SỬ DỤNG:**\n"
        "1️⃣ Gửi link cần bypass\n"
        "2️⃣ Nhập API Key AntiCaptcha\n"
        "3️⃣ Chờ bot xử lý\n"
        "4️⃣ Nhận link kết quả\n\n"
        "🔒 **BẢO MẬT:**\n"
        "• API Key được xóa tự động sau khi nhập\n"
        "• Hoạt động cả trong chat riêng và nhóm\n"
        "• Đảm bảo an toàn thông tin tuyệt đối\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "✨ Hãy gửi link để bắt đầu!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# BƯỚC 1: NHẬN LINK
@bot.message_handler(func=lambda message: True)
def handle_link_step(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(
            message, 
            "━━━━━━━━━━━━━━━━━━\n"
            "🔵 **THÔNG BÁO**\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "👋 Chào bạn!\n\n"
            "💡 Vui lòng gửi link cần bypass\n"
            "(Bắt đầu bằng http:// hoặc https://)\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "📝 Gõ /start để xem hướng dẫn",
            parse_mode="Markdown"
        )
        return

    # Gửi tin nhắn hỏi key và chuyển sang bước tiếp theo
    msg = bot.reply_to(
        message, 
        "━━━━━━━━━━━━━━━━━━\n"
        "🔑 **YÊU CẦU API KEY**\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "📝 Vui lòng nhập API Key AntiCaptcha:\n\n"
        "🔒 _Tin nhắn sẽ được xóa tự động để bảo mật_\n"
        "✅ Hoạt động cả trong nhóm chat\n\n"
        "━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )
    
    # Đăng ký hàm tiếp theo sẽ xử lý tin nhắn trả lời của người dùng
    bot.register_next_step_handler(msg, step_receive_key, url)


# ==============================================================
# 4. FLASK WEB SERVER (Để Render không cho bot ngủ)
# ==============================================================
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>Bot Bóng X</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    text-align: center;
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                }
                h1 { font-size: 3em; margin: 0; }
                p { font-size: 1.2em; }
                .status { color: #4ade80; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Bot Bóng X</h1>
                <p class="status">✅ Bot đang hoạt động!</p>
                <p>Telegram Bypass Bot</p>
                <p>🔒 Bảo mật | 💬 Hỗ trợ nhóm | ⚡ Nhanh chóng</p>
            </div>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'ok', 'bot': 'running'}, 200

def run_flask():
    """Chạy Flask server trên thread riêng"""
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    # Fix Windows console encoding
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 30)
    print("🤖 BOT BÓNG X ĐANG CHẠY...")
    print("=" * 30)
    print("✅ Sẵn sàng nhận lệnh!")
    print("🔒 Bảo mật: Tự động xóa API Key")
    print("💬 Hỗ trợ: Chat riêng & Nhóm")
    print("🌐 Web Server: Đang chạy")
    print("=" * 30)
    
    # Chạy Flask server trên thread riêng
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("🌐 Flask server started on port", os.getenv("PORT", 10000))
    
    # Chạy bot
    bot.infinity_polling()


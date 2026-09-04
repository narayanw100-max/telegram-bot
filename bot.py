import os
import asyncio
import urllib.parse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# पर्यावरण चर (Environment Variable) से टोकन लें या सीधे यहाँ डालें
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8892813800:AAFXmYjyhEMC1AcWxHSK8gBsNWC4mgL4i1Y")
PORT = int(os.getenv("PORT", 10000))

# Render/Koyeb के लिए Health Check Server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive and running 24/7!")

def run_health_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    server.serve_forever()

# AI से उत्तर पाने का फंक्शन
def query_ai(prompt, model_type="openai"):
    try:
        encoded = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded}?model={model_type}"
        res = requests.get(url, timeout=30)
        return res.text if res.status_code == 200 else "⚠️ AI Server Busy. Please try again."
    except Exception as e:
        return "⚠️ तकनीक समस्या के कारण उत्तर नहीं मिल सका।"

# /start कमांड (ग्लोबल यूजर्स के लिए)
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    msg = (
        f"👋 **Hello {user_name}! Welcome to Hybrid AI Bot.**\n\n"
        "यह बोट दुनिया के किसी भी कोने से यूज़ किया जा सकता है:\n\n"
        "🔸 `/gpt <prompt>` - ChatGPT से पूछें\n"
        "🔸 `/claude <prompt>` - Claude AI से पूछें\n"
        "🔸 `/gemini <prompt>` - Gemini AI से पूछें\n"
        "🔸 `/imagine <prompt>` - फोटो जनरेट करें\n\n"
        "या सीधे कोई भी सवाल टाइप करके भेजें!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# AI Commands
async def gpt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Please write a prompt! Example: `/gpt Hello`", parse_mode="Markdown")
        return
    ans = query_ai(text, "openai")
    await update.message.reply_text(f"🟢 **ChatGPT:**\n\n{ans}")

async def claude_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Please write a prompt!", parse_mode="Markdown")
        return
    ans = query_ai(text, "claude")
    await update.message.reply_text(f"🟠 **Claude:**\n\n{ans}")

async def gemini_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Please write a prompt!", parse_mode="Markdown")
        return
    ans = query_ai(text, "gemini")
    await update.message.reply_text(f"🔵 **Gemini:**\n\n{ans}")

# /imagine कमांड
async def imagine_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Please give image description!", parse_mode="Markdown")
        return
    encoded = urllib.parse.quote(prompt)
    img_url = f"https://image.pollinations.ai/prompt/{encoded}"
    await update.message.reply_photo(photo=img_url, caption=f"✨ **Prompt:** {prompt}")

# डायरेक्ट मैसेज का जवाब
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = query_ai(update.message.text, "openai")
    await update.message.reply_text(ans)

def main():
    # 24/7 वेब सर्वर चालू करें
    threading.Thread(target=run_health_server, daemon=True).start()
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("gpt", gpt_cmd))
    app.add_handler(CommandHandler("claude", claude_cmd))
    app.add_handler(CommandHandler("gemini", gemini_cmd))
    app.add_handler(CommandHandler("imagine", imagine_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running globally...")
    app.run_polling()

if __name__ == "__main__":
    main()

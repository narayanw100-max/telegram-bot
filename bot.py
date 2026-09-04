import asyncio
import urllib.parse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8892813800:AAFXmYjyhEMC1AcWxHSK8gBsNWC4mgL4i1Y"

# Health check server for Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

def query_ai(prompt, model_type="openai"):
    try:
        encoded = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded}?model={model_type}"
        res = requests.get(url, timeout=30)
        return res.text if res.status_code == 200 else "⚠️ AI Server Busy."
    except Exception as e:
        return f"Error: {e}"

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🤖 **Hybrid AI Bot Ready!**\n\n"
        "🔸 `/gpt <prompt>` - Ask ChatGPT\n"
        "🔸 `/claude <prompt>` - Ask Claude\n"
        "🔸 `/gemini <prompt>` - Ask Gemini\n"
        "🔸 `/imagine <prompt>` - Generate Photo"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def gpt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Please provide a prompt! Example: `/gpt Hello`", parse_mode="Markdown")
        return
    ans = query_ai(text, "openai")
    await update.message.reply_text(f"🟢 **ChatGPT:**\n\n{ans}")

async def claude_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Please provide a prompt!", parse_mode="Markdown")
        return
    ans = query_ai(text, "claude")
    await update.message.reply_text(f"🟠 **Claude:**\n\n{ans}")

async def gemini_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Please provide a prompt!", parse_mode="Markdown")
        return
    ans = query_ai(text, "gemini")
    await update.message.reply_text(f"🔵 **Gemini:**\n\n{ans}")

async def imagine_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Please give image description!", parse_mode="Markdown")
        return
    encoded = urllib.parse.quote(prompt)
    img_url = f"https://image.pollinations.ai/prompt/{encoded}"
    await update.message.reply_photo(photo=img_url, caption=f"✨ **Prompt:** {prompt}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = query_ai(update.message.text, "openai")
    await update.message.reply_text(ans)

if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("gpt", gpt_cmd))
    app.add_handler(CommandHandler("claude", claude_cmd))
    app.add_handler(CommandHandler("gemini", gemini_cmd))
    app.add_handler(CommandHandler("imagine", imagine_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

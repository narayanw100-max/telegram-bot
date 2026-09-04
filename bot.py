hereimport asyncio
import requests
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8892813800:AAFXmYjyhEMC1AcWxHSK8gBsNWC4mgL4i1Y"

# Render Health Check Server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hybrid AI Bot Running 24/7 Free!")

def run_health_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

# Free Hybrid AI Router API (100% Free & Unlimited)
def query_hybrid_ai(prompt: str, model_type: str = "openai") -> str:
    try:
        # Open-source Free Endpoint mapped to multi-models
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}?model={model_type}"
        
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.text
        return "⚠️ AI Response Error. Please try again."
    except Exception as e:
        return f"Error connecting to {model_type}: {e}"

# Free Image Generation (Flux / SD)
def generate_free_image(prompt: str) -> str:
    encoded_prompt = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

# Bot Command Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 **Welcome to Ultimate Hybrid AI Bot!** 100% Free 24/7\n\n"
        "आप इन कमांड्स का उपयोग कर सकते हैं:\n"
        "🔹 `/gpt <सवाल>` - ChatGPT (GPT-4o) से पूछें\n"
        "🔹 `/claude <सवाल>` - Claude 3.5 Sonnet से पूछें\n"
        "🔹 `/gemini <सवाल>` - Google Gemini से पूछें\n"
        "🔹 `/imagine <प्रॉम्प्ट>` - AI फोटो / इमेजेस जनरेट करें\n\n"
        "या बस डायरेक्ट मैसेज भेजें, डिफ़ॉल्ट रूप से **Hybrid AI** जवाब देगा!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def gpt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = " ".join(context.args)
    if not user_query:
        await update.message.reply_text("कृपया सवाल भी लिखें! उदाहरण: `/gpt AI का भविष्य क्या है?`", parse_mode="Markdown")
        return
    await update.message.reply_text("🧠 ChatGPT सोच रहा है...")
    ans = query_hybrid_ai(user_query, model_type="openai")
    await update.message.reply_text(f"🟢 **ChatGPT Response:**\n\n{ans}")

async def claude_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = " ".join(context.args)
    if not user_query:
        await update.message.reply_text("कृपया सवाल लिखें! उदाहरण: `/claude एक कोड लिखो`", parse_mode="Markdown")
        return
    await update.message.reply_text("🟧 Claude AI प्रोसेसिंग कर रहा है...")
    ans = query_hybrid_ai(user_query, model_type="claude")
    await update.message.reply_text(f"🟠 **Claude Response:**\n\n{ans}")

async def gemini_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = " ".join(context.args)
    if not user_query:
        await update.message.reply_text("कृपया सवाल लिखें!", parse_mode="Markdown")
        return
    await update.message.reply_text("🔷 Gemini AI उत्तर ढूंढ रहा है...")
    ans = query_hybrid_ai(user_query, model_type="gemini")
    await update.message.reply_text(f"🔵 **Gemini Response:**\n\n{ans}")

async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = " ".join(context.args)
    if not user_prompt:
        await update.message.reply_text("कृपया फोटो का विवरण दें! उदाहरण: `/imagine futuristic cybernetic city`", parse_mode="Markdown")
        return
    await update.message.reply_text("🎨 AI इमेज बनाई जा रही है, कृपया 5 सेकंड रुकें...")
    img_url = generate_free_image(user_prompt)
    await update.message.reply_photo(photo=img_url, caption=f"✨ **Prompt:** {user_prompt}")

async def default_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    ans = query_hybrid_ai(user_text, model_type="openai")
    await update.message.reply_text(ans)

def main():
    threading.Thread(target=run_health_server, daemon=True).start()
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("gpt", gpt_handler))
    app.add_handler(CommandHandler("claude", claude_handler))
    app.add_handler(CommandHandler("gemini", gemini_handler))
    app.add_handler(CommandHandler("imagine", image_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, default_chat_handler))
    
    print("Hybrid AI Telegram Bot is Running...")
    app.run_polling()

if __name__ == "__main__":
    main()

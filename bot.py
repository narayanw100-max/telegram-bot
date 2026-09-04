import os
import asyncio
import urllib.parse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from pyrogram import Client, filters

# Telegram Configuration
TELEGRAM_TOKEN = "8892813800:AAFXmYjyhEMC1AcWxHSK8gBsNWC4mgL4i1Y"

# Render Web Server for 24/7 Alive
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is active!")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# AI Request Helper
def query_ai(prompt, model_type="openai"):
    try:
        encoded = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded}?model={model_type}"
        res = requests.get(url, timeout=30)
        return res.text if res.status_code == 200 else "⚠️ AI Server Busy."
    except Exception as e:
        return f"Error: {e}"

# AI Commands Setup
async def main():
    threading.Thread(target=run_health_server, daemon=True).start()
    
    app = Client(
        "hybrid_ai_bot",
        bot_token=TELEGRAM_TOKEN,
        api_id=6,
        api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e"
    )

    @app.on_message(filters.command("start"))
    async def start_cmd(client, message):
        msg = (
            "🤖 **Hybrid AI Bot Ready!**\n\n"
            "🔸 `/gpt <prompt>` - Ask ChatGPT\n"
            "🔸 `/claude <prompt>` - Ask Claude\n"
            "🔸 `/gemini <prompt>` - Ask Gemini\n"
            "🔸 `/imagine <prompt>` - Generate Photo"
        )
        await message.reply_text(msg)

    @app.on_message(filters.command("gpt"))
    async def gpt_cmd(client, message):
        text = " ".join(message.command[1:])
        if not text:
            await message.reply_text("Please provide a prompt! Example: `/gpt Hello`")
            return
        ans = query_ai(text, "openai")
        await message.reply_text(f"🟢 **ChatGPT:**\n\n{ans}")

    @app.on_message(filters.command("claude"))
    async def claude_cmd(client, message):
        text = " ".join(message.command[1:])
        if not text:
            await message.reply_text("Please provide a prompt!")
            return
        ans = query_ai(text, "claude")
        await message.reply_text(f"🟠 **Claude:**\n\n{ans}")

    @app.on_message(filters.command("gemini"))
    async def gemini_cmd(client, message):
        text = " ".join(message.command[1:])
        if not text:
            await message.reply_text("Please provide a prompt!")
            return
        ans = query_ai(text, "gemini")
        await message.reply_text(f"🔵 **Gemini:**\n\n{ans}")

    @app.on_message(filters.command("imagine"))
    async def imagine_cmd(client, message):
        prompt = " ".join(message.command[1:])
        if not prompt:
            await message.reply_text("Please give image description!")
            return
        encoded = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{encoded}"
        await message.reply_photo(photo=img_url, caption=f"✨ **Prompt:** {prompt}")

    @app.on_message(filters.text & ~filters.service)
    async def handle_message(client, message):
        if message.text.startswith("/"):
            return
        ans = query_ai(message.text, "openai")
        await message.reply_text(ans)

    print("Bot starting with Pyrofork...")
    await app.start()
    print("Bot is LIVE!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

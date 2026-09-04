import os
import io
import hashlib
import random
import string
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

import requests
import qrcode
from pyrogram import Client, filters

# ---------------- Telegram Configuration ----------------
TELEGRAM_TOKEN = "8892813800:AAFXmYjyhEMC1AcWxHSK8gBsNWC4mgL4i1Y"
# NOTE: No chat_id was present in the code you shared — add one below if you
# want the bot to send startup/log notifications to a specific chat.
# ADMIN_CHAT_ID = 123456789

# ---------------- Render/Host Health Check (24/7 alive) ----------------
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

# ---------------- App ----------------
app = Client(
    "universal_utility_bot",
    bot_token=TELEGRAM_TOKEN,
    api_id=6,
    api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e"
)

HELP_TEXT = (
    "🛠 **Universal Utility Bot**\n\n"
    "🔸 `/qr <text>` — QR code बनाएं\n"
    "🔸 `/pass <length>` — Strong password generate करें\n"
    "🔸 `/hash <md5|sha256> <text>` — Text hash करें\n"
    "🔸 `/currency <amount> <from> <to>` — जैसे `/currency 100 USD INR`\n"
    "🔸 `/calc <expression>` — जैसे `/calc (25*4)+10`\n"
    "🔸 `/count <text>` — Word/char count\n"
    "🔸 `/case <upper|lower|title> <text>` — Text case बदलें\n"
    "🔸 `/time <timezone>` — जैसे `/time Asia/Kolkata`"
)

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_text(HELP_TEXT)

@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    await message.reply_text(HELP_TEXT)

@app.on_message(filters.command("qr"))
async def qr_cmd(client, message):
    text = " ".join(message.command[1:])
    if not text:
        await message.reply_text("उदाहरण: `/qr https://pdfhub.space`")
        return
    img = qrcode.make(text)
    buf = io.BytesIO()
    buf.name = "qr.png"
    img.save(buf, "PNG")
    buf.seek(0)
    await message.reply_photo(photo=buf, caption=f"✅ QR for: {text}")

@app.on_message(filters.command("pass"))
async def pass_cmd(client, message):
    try:
        length = int(message.command[1]) if len(message.command) > 1 else 12
        length = max(6, min(length, 64))
    except ValueError:
        length = 12
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    pwd = "".join(random.choice(chars) for _ in range(length))
    await message.reply_text(f"🔑 **Password ({length} chars):**\n`{pwd}`")

@app.on_message(filters.command("hash"))
async def hash_cmd(client, message):
    if len(message.command) < 3:
        await message.reply_text("उदाहरण: `/hash sha256 hello world`")
        return
    algo = message.command[1].lower()
    text = " ".join(message.command[2:])
    if algo not in ("md5", "sha256"):
        await message.reply_text("Supported: md5, sha256")
        return
    h = hashlib.md5(text.encode()) if algo == "md5" else hashlib.sha256(text.encode())
    await message.reply_text(f"🔐 **{algo.upper()}:**\n`{h.hexdigest()}`")

@app.on_message(filters.command("currency"))
async def currency_cmd(client, message):
    if len(message.command) < 4:
        await message.reply_text("उदाहरण: `/currency 100 USD INR`")
        return
    try:
        amount = float(message.command[1])
        frm = message.command[2].upper()
        to = message.command[3].upper()
        res = requests.get(f"https://open.er-api.com/v6/latest/{frm}", timeout=10).json()
        if res.get("result") != "success":
            await message.reply_text("⚠️ Currency data नहीं मिल पाया।")
            return
        rate = res["rates"].get(to)
        if not rate:
            await message.reply_text("⚠️ अज्ञात currency code।")
            return
        converted = amount * rate
        await message.reply_text(f"💱 {amount} {frm} = **{converted:.2f} {to}**")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@app.on_message(filters.command("calc"))
async def calc_cmd(client, message):
    expr = " ".join(message.command[1:])
    if not expr:
        await message.reply_text("उदाहरण: `/calc (25*4)+10`")
        return
    allowed = set("0123456789+-*/(). ")
    if not set(expr) <= allowed:
        await message.reply_text("⚠️ केवल संख्याएं और + - * / ( ) इस्तेमाल करें।")
        return
    try:
        result = eval(expr, {"__builtins__": {}}, {})
        await message.reply_text(f"🧮 **Result:** {result}")
    except Exception:
        await message.reply_text("⚠️ Invalid expression।")

@app.on_message(filters.command("count"))
async def count_cmd(client, message):
    text = " ".join(message.command[1:])
    if not text:
        await message.reply_text("उदाहरण: `/count Hello world`")
        return
    words = len(text.split())
    chars = len(text)
    await message.reply_text(f"📊 Words: **{words}** | Characters: **{chars}**")

@app.on_message(filters.command("case"))
async def case_cmd(client, message):
    if len(message.command) < 3:
        await message.reply_text("उदाहरण: `/case upper hello world`")
        return
    mode = message.command[1].lower()
    text = " ".join(message.command[2:])
    if mode == "upper":
        out = text.upper()
    elif mode == "lower":
        out = text.lower()
    elif mode == "title":
        out = text.title()
    else:
        await message.reply_text("Supported: upper, lower, title")
        return
    await message.reply_text(f"✅ {out}")

@app.on_message(filters.command("time"))
async def time_cmd(client, message):
    if len(message.command) < 2:
        await message.reply_text("उदाहरण: `/time Asia/Kolkata`")
        return
    try:
        from zoneinfo import ZoneInfo
        tz = message.command[1]
        now = datetime.now(ZoneInfo(tz))
        await message.reply_text(f"🕒 **{tz}:** {now.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception:
        await message.reply_text("⚠️ अमान्य timezone (जैसे Asia/Kolkata, America/New_York)")

if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    print("Universal Utility Bot starting...")
    app.run()

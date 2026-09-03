import asyncio
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Bot

TELEGRAM_TOKEN = "8892813800:AAFXmYjyhEMC1AcWxHSK8gBsNWC4mgL4i1Y"
CHAT_ID = "7815873110"

# Render के Health Check के लिए Dummy HTTP Server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is active and running 24/7!")

def run_health_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

def get_latest_news():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    try:
        response = requests.get(url).json()
        top_story_id = response[0]
        
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{top_story_id}.json"
        story_data = requests.get(story_url).json()
        
        title = story_data.get("title", "No Title")
        link = story_data.get("url", "No Link Available")
        
        return f"🔥 **InsightPulse AI Update** 🔥\n\n📌 **Title:** {title}\n\n🔗 **Read More:** {link}"
    except Exception as e:
        return f"Error fetching news: {e}"

async def main():
    # Background Thread में HTTP Server स्टार्ट करें
    threading.Thread(target=run_health_server, daemon=True).start()
    
    bot = Bot(token=TELEGRAM_TOKEN)
    print("Automated Bot Started...")
    while True:
        try:
            message = get_latest_news()
            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
            print("Update sent successfully!")
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())

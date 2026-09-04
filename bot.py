hereimport asyncio
import requests
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Bot

TELEGRAM_TOKEN = "8892813800:AAFXmYjyhEMC1AcWxHSK8gBsNWC4mgL4i1Y"
CHAT_ID = "7815873110"

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"InsightPulse AI Monetization Bot Running!")

def run_health_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

def get_viral_global_news():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    try:
        response = requests.get(url).json()
        
        # व्यापक ग्लोबल रीच के लिए टॉप 30 ट्रेंडिंग स्टोरीज में से रैंडम चुनाव
        top_stories = response[:30]
        selected_id = random.choice(top_stories)
        
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{selected_id}.json"
        story_data = requests.get(story_url).json()
        
        title = story_data.get("title", "Global Tech Breakthrough")
        link = story_data.get("url", "https://news.ycombinator.com")
        
        # High Click-Through Rate (CTR) Format for Viral Reach & Traffic
        return (
            f"⚡ **VIRAL GLOBAL TREND** ⚡\n\n"
            f"🧠 **{title}**\n\n"
            f"🌍 *Must-Read Evergeen Insight for Everyone*\n\n"
            f"👇 **Click to Read Full Story:**\n"
            f"🔗 {link}"
        )
    except Exception as e:
        print(f"Error fetching viral news: {e}")
        return None

async def main():
    threading.Thread(target=run_health_server, daemon=True).start()
    bot = Bot(token=TELEGRAM_TOKEN)
    print("Monetization Bot Active...")
    
    while True:
        try:
            message = get_viral_global_news()
            if message:
                await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
                print("Viral news update sent!")
            
            # हर 1 घंटे (3600 सेकंड) में नया अपडेट
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())

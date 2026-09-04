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
        self.wfile.write(b"InsightPulse AI is Active!")

def run_health_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

def get_evergreen_global_news():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    try:
        response = requests.get(url).json()
        
        # व्यापक वैरायटी के लिए टॉप 30 ग्लोबल स्टोरीज में से एक रैंडम चुनें
        top_stories = response[:30]
        selected_id = random.choice(top_stories)
        
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{selected_id}.json"
        story_data = requests.get(story_url).json()
        
        title = story_data.get("title", "Global Tech Insight")
        link = story_data.get("url", "https://news.ycombinator.com")
        
        return (
            f"🌍 **InsightPulse AI | Global Trends**\n\n"
            f"📌 **Title:** {title}\n\n"
            f"💡 *Evergreen Tech & Innovation Insight*\n\n"
            f"🔗 **Explore:** {link}"
        )
    except Exception as e:
        print(f"Error fetching news: {e}")
        return None

async def main():
    threading.Thread(target=run_health_server, daemon=True).start()
    bot = Bot(token=TELEGRAM_TOKEN)
    print("InsightPulse AI Bot Running...")
    
    while True:
        try:
            message = get_evergreen_global_news()
            if message:
                await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
                print("Global evergreen update sent successfully!")
            
            # हर 1 घंटे (3600 सेकंड) में एक नया अपडेट
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())

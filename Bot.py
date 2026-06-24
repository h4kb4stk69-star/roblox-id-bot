import urllib.request
import json
import re
import time
import random
import os

TOKEN = "8835111114:AAFewM2CDT6Qgl9kbUlfrqdaIfHGDMIxe7w"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

EMOJIS = {
    "success": "✅", "error": "❌", "loading": "🔄", "id": "🆔",
    "link": "📎", "star": "⭐", "fire": "🔥", "diamond": "💎",
    "rocket": "🚀", "crown": "👑", "gem": "💠", "sparkle": "✨",
    "magic": "🔮", "robot": "🤖", "heart": "❤️", "thunder": "⚡",
    "info": "📌", "settings": "⚙️", "search": "🔍", "target": "🎯",
    "gift": "🎁", "box": "📦", "label": "🏷️", "check": "✔️"
}

class IDExtractor:
    def __init__(self):
        self.cache = {}
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        ]
    
    def extract_code(self, url):
        patterns = [r'code=([a-f0-9]+)', r'code=([A-Za-z0-9]+)', r'shareCode=([a-f0-9]+)']
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def extract_id_direct(self, url):
        patterns = [
            r'itemId=(\d+)', r'assetId=(\d+)', r'assetid=(\d+)',
            r'id=(\d+)', r'catalog/(\d+)/', r'items/(\d+)/',
            r'asset/(\d+)/', r'item/(\d+)/', r'\/(\d{8,})\/'
        ]
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def fetch_id_from_code(self, code):
        if code in self.cache:
            return self.cache[code]
        try:
            url = f"https://www.roblox.com/share?code={code}&type=AvatarItemDetails"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', random.choice(self.user_agents))
            with urllib.request.urlopen(req, timeout=8) as response:
                html = response.read().decode('utf-8')
                patterns = [
                    r'"assetId":(\d+)', r'"itemId":(\d+)', r'"AssetId":(\d+)',
                    r'"ItemId":(\d+)', r'assetid=(\d+)', r'itemid=(\d+)',
                    r'data-asset-id="(\d+)"', r'data-item-id="(\d+)"'
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        self.cache[code] = match.group(1)
                        return match.group(1)
                numbers = re.findall(r'\b(\d{8,})\b', html)
                if numbers:
                    self.cache[code] = numbers[0]
                    return numbers[0]
                return None
        except:
            return None
    
    def get_item_id(self, url):
        url = url.strip()
        direct_id = self.extract_id_direct(url)
        if direct_id:
            return direct_id, "مباشر"
        code = self.extract_code(url)
        if code:
            item_id = self.fetch_id_from_code(code)
            if item_id:
                return item_id, "من الكود"
        numbers = re.findall(r'\b(\d{8,})\b', url)
        if numbers:
            return numbers[0], "من الرابط"
        return None, None

extractor = IDExtractor()

def send_message(chat_id, text):
    try:
        url = BASE_URL + "sendMessage"
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
        data_bytes = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, method='POST')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_loading(chat_id):
    return send_message(chat_id, f"{EMOJIS['loading']} جاري استخراج الـ ID... ⏳")

def get_updates(offset=None):
    try:
        url = BASE_URL + "getUpdates"
        if offset:
            url += f"?offset={offset}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode()).get('result', [])
    except Exception as e:
        print(f"Error: {e}")
        return []

def handle_message(message):
    chat_id = message['chat']['id']
    text = message.get('text', '')
    first_name = message['chat'].get('first_name', 'صديق')
    
    print(f"📩 {first_name}: {text[:50]}...")
    
    if text == '/start':
        reply = f"""
{EMOJIS['sparkle']} <b>مرحباً بك في البوت الذهبي!</b> {EMOJIS['crown']}

{EMOJIS['robot']} أنا هنا لاستخراج <b>ID</b> أي عنصر في روبلوكس!

{EMOJIS['info']} <b>كيفية الاستخدام:</b>
• أرسل لي رابط أي عنصر
• سأستخرج الـ ID خلال ثوانٍ

{EMOJIS['star']} <b>الأوامر:</b>
/start - عرض هذه الرسالة
/help - عرض المساعدة
/about - معلومات عن البوت

{EMOJIS['rocket']} <b>جاهز للانطلاق!</b>
"""
        send_message(chat_id, reply)
    
    elif text == '/help':
        reply = f"""
{EMOJIS['info']} <b>المساعدة الكاملة</b>

{EMOJIS['magic']} <b>كيفية الاستخدام:</b>
1. انسخ رابط عنصر من روبلوكس
2. أرسله لي في الدردشة
3. سأستخرج الـ ID وأرسله لك

{EMOJIS['box']} <b>الروابط المدعومة:</b>
{EMOJIS['check']} روابط المشاركة (share?code=...)
{EMOJIS['check']} روابط الكتالوج (catalog/ID/)
{EMOJIS['check']} روابط العناصر (itemId=ID)
"""
        send_message(chat_id, reply)
    
    elif text == '/about':
        reply = f"""
{EMOJIS['robot']} <b>عن البوت الذهبي</b>

{EMOJIS['diamond']} <b>الاسم:</b> Roblox ID Extractor PRO
{EMOJIS['gem']} <b>الإصدار:</b> 2.0
{EMOJIS['fire']} <b>اللغة:</b> Python 3
{EMOJIS['crown']} <b>المطور:</b> @YourUsername

{EMOJIS['star']} <b>المميزات:</b>
{EMOJIS['check']} استخراج ID من أي رابط
{EMOJIS['check']} سرعة فائقة
{EMOJIS['check']} إيموجيات جميلة
"""
        send_message(chat_id, reply)
    
    elif 'roblox.com' in text or 'http' in text:
        send_loading(chat_id)
        start_time = time.time()
        item_id, method = extractor.get_item_id(text)
        elapsed = (time.time() - start_time) * 1000
        
        if item_id:
            reply = f"""
{EMOJIS['success']} <b>تم استخراج الـ ID بنجاح!</b> {EMOJIS['sparkle']}

{EMOJIS['id']} <b>الـ ID:</b> <code>{item_id}</code>
{EMOJIS['label']} <b>طريقة الاستخراج:</b> {method}
{EMOJIS['thunder']} <b>الوقت:</b> {elapsed:.0f} مللي ثانية

{EMOJIS['link']} <b>رابط العنصر بالـ ID:</b>
<code>https://www.roblox.com/catalog/{item_id}/</code>

{EMOJIS['diamond']} استمتع باستخدام الـ ID! 🎯
"""
            send_message(chat_id, reply)
        else:
            reply = f"""
{EMOJIS['error']} <b>لم نتمكن من استخراج الـ ID</b>

{EMOJIS['info']} <b>الأسباب المحتملة:</b>
• الرابط غير صحيح
• الرابط ليس لعنصر في روبلوكس

{EMOJIS['robot']} جرب رابطاً آخر!
"""
            send_message(chat_id, reply)
    
    else:
        reply = f"""
{EMOJIS['robot']} 👋 <b>مرحباً {first_name}!</b>

{EMOJIS['search']} أرسل لي رابط عنصر من روبلوكس
وسأستخرج الـ {EMOJIS['id']} <b>ID</b> الخاص به!

{EMOJIS['sparkle']} أو استخدم /help للمساعدة! 🚀
"""
        send_message(chat_id, reply)

def main():
    print("=" * 60)
    print("🤖 ROBLOX ID EXTRACTOR PRO - DEPLOYED")
    print("=" * 60)
    print("🚀 Bot is running...")
    print("📡 Listening for messages...")
    print()
    
    last_update_id = 0
    while True:
        try:
            updates = get_updates(last_update_id + 1)
            for update in updates:
                if 'message' in update:
                    handle_message(update['message'])
                    last_update_id = update['update_id']
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

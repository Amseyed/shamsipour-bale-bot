
import os
import json
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

RSS_URL = "https://shamsipour.tvu.ac.ir/?a=content.q.rss&lang=fa"

BALE_TOKEN = os.getenv("BALE_TOKEN", "806811347:SzjGJ10jkbiR9ONnN276kGeQZyfC6zvQKGA").strip()
BALE_CHAT_ID = os.getenv("BALE_CHAT_ID", "120706908").strip()

STATE_FILE = Path(__file__).with_name("state.json")
CHECK_INTERVAL = 600  # هر ۱۰ دقیقه


def read_rss():
    request = urllib.request.Request(
        RSS_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        content = response.read()

    root = ET.fromstring(content)
    items = []

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        guid = item.findtext("guid", "").strip()

        if title and link:
            items.append({
                "id": guid or link,
                "title": title,
                "link": link
            })

    return items


def send_bale(message):
    url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": BALE_CHAT_ID,
        "text": message
    }).encode("utf-8")

    request = urllib.request.Request(url, data=data)

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)

    if not result.get("ok"):
        raise RuntimeError(f"خطای بله: {result}")

    return result


def load_seen():
    if not STATE_FILE.exists():
        return None

    with STATE_FILE.open("r", encoding="utf-8") as file:
        return set(json.load(file))


def save_seen(seen):
    with STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(sorted(seen), file, ensure_ascii=False, indent=2)


def check_news():
    items = read_rss()
    print(f"تعداد اطلاعیه‌های RSS: {len(items)}", flush=True)

    seen = load_seen()

    if seen is None:
        save_seen({item["id"] for item in items})
        print("اطلاعیه‌های فعلی ثبت شدند؛ منتظر اطلاعیه جدید هستیم.")
        return

    new_items = [
        item for item in reversed(items)
        if item["id"] not in seen
    ]

    for item in new_items:
        message = (
            "📢 اطلاعیه جدید دانشگاه شمس‌پور\n\n"
            f"{item['title']}\n\n"
            f"🔗 {item['link']}"
        )

        send_bale(message)
        print(f"ارسال شد: {item['title']}", flush=True)

        seen.add(item["id"])
        save_seen(seen)


def main():
    if not BALE_TOKEN or not BALE_CHAT_ID:
        print("خطا: BALE_TOKEN و BALE_CHAT_ID تنظیم نشده‌اند.")
        return

    print("ربات شمس‌پور شروع به کار کرد.", flush=True)

    send_bale("✅ ربات اطلاعیه‌های شمس‌پور فعال شد.")
    
    

    while True:
        try:
            check_news()
        except Exception as error:
            print(f"خطا: {error}", flush=True)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()

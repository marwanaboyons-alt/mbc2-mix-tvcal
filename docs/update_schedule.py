
# update_schedule.py
# سكربت يجلب الجداول ويخزنها في docs/schedule.json
import requests, json, os, sys
from bs4 import BeautifulSoup
from datetime import datetime

# — ضع هنا روابط صفحات الجدول لكل قناة (غيّر الروابط لو عندك صفحات أخرى)
channels = {
    "MBC2": "https://elcinema.com/en/tvguide/1128/",
    "Mix":  "https://elcinema.com/en/tvguide/1355/"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

def parse_elcinema(url):
    """
    محاولة مرنة لالتقاط مواعيد من صفحات elcinema:
    - يبحث عن جداول بصنف timeTable
    - وإذا لم يجد يجرب عناصر tvguide-episode
    يرجع قائمة من (date, time, title)
    """
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"ERROR: failed to fetch {url} -> {e}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    items = []

    # محاولة 1: جداول .timeTable
    tables = soup.select(".timeTable, table.timeTable")
    for table in tables:
        # بعض الجداول على elCinema تستخدم head/h3 للـ date
        date_header = table.find_previous("h3")
        date_text = date_header.get_text(strip=True) if date_header else ""
        for tr in table.select("tr"):
            cols = tr.find_all("td")
            if len(cols) >= 2:
                time = cols[0].get_text(strip=True)
                title = cols[1].get_text(strip=True)
                items.append((date_text, time, title))

    if items:
        return items

    # محاولة 2: عناصر .tvguide-episode (نسق مختلف)
    for ep in soup.select(".tvguide-episode"):
        title_el = ep.select_one(".tvguide-episode-title")
        time_el = ep.select_one(".tvguide-episode-time")
        if title_el and time_el:
            title = title_el.get_text(strip=True)
            time = time_el.get_text(strip=True)
            # لا نملك تاريخ لكل عنصر هنا — نضع اليوم كقيمة افتراضية
            date_text = datetime.now().strftime("%Y-%m-%d")
            items.append((date_text, time, title))

    return items

def main():
    results = []
    for channel_name, url in channels.items():
        print(f"Fetching {channel_name} from {url} ...")
        shows = parse_elcinema(url)
        if not shows:
            print(f"  Warning: no shows found for {channel_name}")
        for date_text, time, title in shows:
            # نكتب التاريخ مع الوقت كسلسلة بسيطة (يمكن تعديل لاحقًا)
            combined_time = f"{date_text} {time}".strip()
            results.append({
                "channel": channel_name,
                "movie": title,
                "time": combined_time,
                "date": date_text
            })

    # اكتب الملف داخل docs
    os.makedirs("docs", exist_ok=True)
    out_path = os.path.join("docs", "schedule.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(results)} items to {out_path}")

if __name__ == "__main__":
    main()

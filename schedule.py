import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from ics import Calendar, Event
import pytz

# القنوات وروابطها في elCinema
channels = {
    "MBC2": "https://elcinema.com/en/tvguide/1128/",
    "Mix": "https://elcinema.com/en/tvguide/1355/"
}

# توقيت القاهرة
tz = pytz.timezone("Africa/Cairo")

def fetch_schedule(url, channel_name):
    events = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    for item in soup.select(".tvguide-episode"):
        title_tag = item.select_one(".tvguide-episode-title")
        time_tag = item.select_one(".tvguide-episode-time")
        desc_tag = item.select_one(".tvguide-episode-info")

        if not title_tag or not time_tag:
            continue

        title = f"{channel_name}: {title_tag.get_text(strip=True)}"
        time_str = time_tag.get_text(strip=True)
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        try:
            start_time = datetime.strptime(time_str, "%I:%M %p").replace(
                year=datetime.now().year,
                month=datetime.now().month,
                day=datetime.now().day
            )
            start_time = tz.localize(start_time)
        except:
            continue

        events.append({
            "title": title,
            "start": start_time,
            "description": description
        })

    return events

# إنشاء التقويم
cal = Calendar()
for channel, url in channels.items():
    schedule = fetch_schedule(url, channel)
    for show in schedule:
        e = Event()
        e.name = show["title"]
        e.begin = show["start"]
        e.end = show["start"] + timedelta(hours=2)
        e.description = show["description"]
        cal.events.add(e)

# حفظ ملف ICS
with open("tv_schedule.ics", "w", encoding="utf-8") as f:
    f.writelines(cal)

print("تم إنشاء ملف tv_schedule.ics بنجاح!")

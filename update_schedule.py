import requests
from bs4 import BeautifulSoup

channels = {
    "MBC2": "https://elcinema.com/en/tvguide/1128/",
    "Mix": "https://elcinema.com/en/tvguide/1783/"
}

def fetch_schedule(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    # محاولة التقاط جداول الوقت في الصفحة
    days = soup.select(".timeTable")
    schedule_data = []
    for day in days:
        h = day.find("h3")
        date = h.text.strip() if h else ""
        for row in day.select("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) >= 2:
                time = cols[0].text.strip()
                movie = cols[1].text.strip()
                schedule_data.append((date, time, movie))
    return schedule_data

all_schedules = {}
for channel, link in channels.items():
    try:
        all_schedules[channel] = fetch_schedule(link)
    except Exception as e:
        all_schedules[channel] = [("Error", "-", f"Failed: {e}")]

# بناء HTML للجدول
table_html = ""
for channel, shows in all_schedules.items():
    table_html += f"<h2>{channel}</h2>"
    table_html += "<table><tr><th>التاريخ</th><th>الوقت</th><th>الفيلم</th></tr>"
    for date, time, movie in shows:
        table_html += f"<tr><td>{date}</td><td>{time}</td><td>{movie}</td></tr>"
    table_html += "</table><br>"

# استبدال الجزء المؤقت في index.html
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

new_html = html_content.replace(
    '<div id="schedule">\n    <p>جارٍ تحميل الجدول...</p>\n  </div>',
    f'<div id="schedule">{table_html}</div>'
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(new_html)

print("تم تحديث الجدول بنجاح ✅")

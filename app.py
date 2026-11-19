import json
import os
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request

app = Flask(__name__)

LOG_FILE = "visits_log.json"
IST = timezone(timedelta(hours=5, minutes=30))


def load_data():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"total_visits": 0, "recent_visits": []}


def save_data(data):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def detect_device(user_agent: str) -> str:
    ua = user_agent.lower()
    if "android" in ua:
        device = "Android Mobile"
    elif "iphone" in ua or "ipad" in ua:
        device = "iPhone / iPad"
    elif "windows" in ua:
        device = "Windows PC"
    elif "macintosh" in ua or "mac os" in ua:
        device = "Mac"
    elif "linux" in ua:
        device = "Linux"
    else:
        device = "Unknown Device"

    if "edg" in ua:
        browser = "Edge"
    elif "chrome" in ua and "edg" not in ua:
        browser = "Chrome"
    elif "safari" in ua and "chrome" not in ua:
        browser = "Safari"
    elif "firefox" in ua:
        browser = "Firefox"
    else:
        browser = "Browser"

    return f"{device} ({browser})"


@app.route("/", methods=["GET", "POST"])
def home():
    data = load_data()

    # Bot/health-check requests ko ignore karne ke liye basic filter
    ua_string = request.headers.get("User-Agent", "")
    if "render" not in ua_string.lower() and "bot" not in ua_string.lower():
        data["total_visits"] += 1
        now_ist = datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")
        visit_entry = {
            "time": now_ist,
            "device": detect_device(ua_string),
        }
        data["recent_visits"].insert(0, visit_entry)
        # Sirf latest 10 visits hi list mein rakhenge taaki page clean rahe
        data["recent_visits"] = data["recent_visits"][:10]
        save_data(data)

    return render_template(
        "index.html",
        total_visits=data["total_visits"],
        recent_visits=data["recent_visits"],
    )


if __name__ == "__main__":
    app.run(debug=True)

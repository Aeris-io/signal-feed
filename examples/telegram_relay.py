"""Relay new Signal Feed alerts to a Telegram chat.

Run it from cron every few minutes. It remembers which alerts it has already sent
in a small state file, so each alert is posted once.

Environment:
  TELEGRAM_BOT_TOKEN   token from @BotFather
  TELEGRAM_CHAT_ID     chat or channel id the bot can post to
  MIN_SEVERITY         optional: info, low, medium (default) or high
  STATE_FILE           optional: default ./signal_feed_seen.json

On the very first run it only records what is already in the feed and sends nothing,
so a new chat isn't flooded with history.

Standard library only.
"""
import json
import os
import urllib.parse
import urllib.request
from urllib.parse import urljoin

FEED = "https://aerisvalidator.space/alerts/api/alerts_feed.json"
PAGE = "https://aerisvalidator.space/alerts/"
RANK = {"info": 0, "low": 1, "medium": 2, "high": 3}


def fetch_feed() -> dict:
    with urllib.request.urlopen(FEED, timeout=30) as resp:
        return json.load(resp)


def send(token: str, chat_id: str, text: str) -> None:
    body = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    with urllib.request.urlopen(url, data=body, timeout=30) as resp:
        resp.read()


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_alert(a: dict) -> str:
    link = urljoin(PAGE, a.get("source_url") or "")
    return (
        f"<b>[{a['severity'].upper()}] {escape(a['title'])}</b>\n"
        f"{escape(a.get('summary', ''))}\n"
        f"<i>{escape(a['category'])} · {a['ts_utc'][:16].replace('T', ' ')} UTC</i>\n"
        f"{link}"
    )


def main() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    min_rank = RANK[os.environ.get("MIN_SEVERITY", "medium")]
    state_file = os.environ.get("STATE_FILE", "signal_feed_seen.json")

    first_run = not os.path.exists(state_file)
    seen = set() if first_run else set(json.load(open(state_file, encoding="utf-8")))

    alerts = sorted(fetch_feed()["alerts"], key=lambda a: a["ts_utc"])
    for a in alerts:
        if a["id"] in seen:
            continue
        if not first_run and RANK.get(a["severity"], 0) >= min_rank:
            send(token, chat_id, format_alert(a))
        seen.add(a["id"])

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(sorted(seen), f)


if __name__ == "__main__":
    main()

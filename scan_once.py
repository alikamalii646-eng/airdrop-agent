import os, re, json, hashlib
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

STATE = os.getenv("DATABASE_PATH", "data/state.json")
MIN_SCORE = int(os.getenv("MIN_GOOD_SCORE", "6"))

def load_state():
    try:
        with open(STATE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"seen": {}, "sent": {}}

def save_state(s):
    os.makedirs(os.path.dirname(STATE) or ".", exist_ok=True)
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)

def telegram(msg):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print(msg)
        return
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat, "text": msg, "disable_web_page_preview": False},
        timeout=20,
    )
    r.raise_for_status()

def score(title, text):
    t = (title + " " + text).lower()
    score = 0
    reasons = []
    # Free/no-deposit filter
    if any(x in t for x in ["no investment", "no deposit", "free airdrop", "free to participate", "no purchase"]):
        score += 3; reasons.append("بدون سرمایه/دپازیت طبق متن منبع")
    if any(x in t for x in ["deposit", "top up", "stake", "trade $", "buy crypto", "purchase required"]):
        score -= 6
    # Task friendliness
    if any(x in t for x in ["social", "twitter", "discord", "telegram", "quest", "testnet", "points"]):
        score += 2; reasons.append("کارهای رایگان/اجتماعی یا تست‌نت")
    # Project-quality signals
    if any(x in t for x in ["funding", "$1m", "$5m", "$10m", "$20m", "$30m", "funded"]):
        score += 2; reasons.append("سیگنال فاندینگ/سرمایه‌گذاری")
    if any(x in t for x in ["mainnet", "network", "protocol", "layer 1", "layer 2"]):
        score += 1; reasons.append("پروژه/پروتکل مشخص")
    # Risk penalties
    if any(x in t for x in ["send crypto", "private key", "seed phrase", "guaranteed profit", "double your"]):
        score -= 10
    return score, reasons

def extract(page_url, html):
    soup = BeautifulSoup(html, "html.parser")
    text = " ".join(soup.stripped_strings)
    items = []
    # Generic extraction: links whose surrounding text resembles an airdrop entry.
    for a in soup.find_all("a", href=True):
        title = " ".join(a.stripped_strings).strip()
        if len(title) < 3:
            continue
        href = a["href"]
        if href.startswith("/"):
            from urllib.parse import urljoin
            href = urljoin(page_url, href)
        parent = a.parent
        context = " ".join(parent.stripped_strings) if parent else title
        if any(k in (title + " " + context).lower() for k in
               ["airdrop", "drop", "points", "quest", "testnet", "whitelist", "mint"]):
            items.append((title[:180], href, context[:1200]))
    return items

def run():
    urls = [x.strip() for x in os.getenv("DISCOVERY_URLS", "").split(",") if x.strip()]
    state = load_state()
    found = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for u in urls:
            try:
                page.goto(u, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1500)
                found += [(u, *x) for x in extract(u, page.content())]
            except Exception as e:
                print("SOURCE_ERROR", u, e)
        browser.close()

    now = datetime.now(timezone.utc).isoformat()
    new_good = []
    for source, title, url, context in found:
        sc, reasons = score(title, context)
        if sc < MIN_SCORE:
            continue
        # Stable ID avoids duplicate Telegram alerts.
        key = hashlib.sha256((title + "|" + url).encode()).hexdigest()[:16]
        if key in state["sent"]:
            continue
        state["sent"][key] = now
        state["seen"][key] = {
            "title": title, "url": url, "source": source,
            "score": sc, "reasons": reasons, "found_at": now
        }
        new_good.append((title, url, sc, reasons))

    for title, url, sc, reasons in new_good[:10]:
        msg = (
            "🟢 ایردراپ جدید پیدا شد\n\n"
            f"📌 {title}\n"
            f"⭐ امتیاز فیلتر: {sc}/10+\n"
            "🆓 فقط مواردی که در متن منبع نشانه‌ای از مشارکت رایگان دارند وارد این لیست شده‌اند.\n"
            f"🔎 دلیل‌ها: {', '.join(reasons) if reasons else 'سیگنال کافی'}\n"
            f"🔗 {url}\n\n"
            "⚠️ قبل از اتصال والت/امضا، لینک رسمی پروژه را بررسی کن. من Seed Phrase/Private Key نمی‌خواهم."
        )
        telegram(msg)

    save_state(state)
    print(f"found={len(found)} new_good={len(new_good)}")

if __name__ == "__main__":
    run()

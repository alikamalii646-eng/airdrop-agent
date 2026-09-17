# Airdrop Agent v7 — Telegram Free-Airdrop Watcher

این نسخه برای اجرای رایگان روی GitHub Actions ساخته شده است.

کار اصلی:
- هر 15 دقیقه صفحات عمومی آردراپ را بررسی می‌کند.
- فقط فرصت‌هایی را که نشانه‌های مشارکت رایگان/بدون دپازیت دارند فیلتر می‌کند.
- برای «کارهای رایگان» مثل social/Discord/Telegram/quest/testnet امتیاز اضافه می‌کند.
- سیگنال‌های کیفیت مثل funding و مشخص بودن پروژه را در امتیاز دخالت می‌دهد.
- موارد مشکوک مثل seed phrase، private key، ارسال پول یا سود تضمینی را حذف می‌کند.
- مورد جدید را یک‌بار در تلگرام می‌فرستد.
- قبل از wallet connect/signature/transaction هیچ اقدامی انجام نمی‌دهد.

نکته: «خوب» به معنی تضمین سود نیست؛ امتیاز فقط یک فیلتر خودکار بر اساس نشانه‌های قابل مشاهده است.

## Setup
1. یک GitHub repository عمومی بساز.
2. فایل‌های این پروژه را داخلش قرار بده.
3. در Settings → Secrets and variables → Actions:
   - Secret: TELEGRAM_BOT_TOKEN
   - Secret: TELEGRAM_CHAT_ID
   - Variable: DISCOVERY_URLS
     مقدار پیش‌فرض:
     https://alphadrops.net/free-crypto-airdrops,https://www.airdropvillage.io/airdrops
4. Actions را فعال کن.
5. Workflow را یک‌بار با Run workflow اجرا کن.

این «VPS 24/7» نیست؛ یک اسکنر دوره‌ای است که بدون پرداخت و بدون کارت روی GitHub Actions اجرا می‌شود.

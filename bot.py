import asyncio
import random
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN = "8099815200:AAH05Qa5PiHbhdC54UdZiLMf0dNeRt4ETwQ"
ADMIN_ID = 6360110232
API_ID = 33118317
API_HASH = "53aae636122c27a99a6c211ecc5d0c68"

app = Client("iqro_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
scheduler = AsyncIOScheduler()

# Manba kanallar
CHANNELS = [
    "aminnasafiy",
    "hikmatn",
    "arabicuz_nahv_hikmat",
    "Kunhikmat",
    "hikmatlartoplami"
]

GROUP_ID = -1003930688891

# REKLAMA VA SHUBHALI SO'ZLAR FILTRI
STOP_WORDS = [
    "http://", "https://", "t.me/", "tg.me", "bot", 
    "reklama", "aksiya", "chegirma", "tanlov", "homiy", 
    "murojaat", "murojaat uchun", "kanalga obuna", "so'm", "som"
]

def is_ad(text):
    """Matn reklama yoki havola ekanligini tekshirish"""
    text_lower = text.lower()
    for word in STOP_WORDS:
        if word in text_lower:
            return True
    return False

def get_post(channel):
    """Kanalning ochiq sahifasidan eng oxirgi REKLAMASIZ hikmatni olish"""
    urls = [
        f"https://t.me/s/{channel}",
        f"https://tg.i2p.fan/s/{channel}"
    ]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                msgs = soup.find_all('div', class_='tgme_widget_message_text')
                
                # Oxirgi postlardan boshlab tekshirish
                for msg in reversed(msgs):
                    for br in msg.find_all('br'):
                        br.replace_with('\n')
                    text = msg.get_text().strip()
                    
                    # 1. Matn kamida 15 ta belgidan iborat bo'lsin
                    # 2. Ichida reklama yoki link so'zlari bo'lmasin
                    if len(text) > 15 and not is_ad(text):
                        return text
        except Exception:
            continue
    return None

async def fetch_and_send_hikmat():
    print("⏳ Kanallardan toza hikmat qidirilmoqda...")
    random_channels = CHANNELS.copy()
    random.shuffle(random_channels)
    
    content = None
    selected_channel = None

    for chan in random_channels:
        content = await asyncio.to_thread(get_post, chan)
        if content:
            selected_channel = chan
            break

    if content:
        formatted_text = (
            f"{content}\n\n"
            f"✍️ **Manba:** @{selected_channel}\n\n"
            f"©️iqro 📚🕊️"
        )
        try:
            await app.send_message(GROUP_ID, formatted_text, parse_mode=None)
            print(f"✅ TOZA POST YUBORILDI! Manba: @{selected_channel}")
        except Exception as e:
            print(f"❌ Guruhga yuborishda Telegram xatosi: {e}")
    else:
        print("⚠️ Kanallarda mos keladigan toza hikmat topilmadi (barchasi reklama bo'lishi mumkin).")

# /start buyrug'i
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply(
        f"Assalomu alaykum, {message.from_user.first_name}!\n"
        "'Iqro' botiga xush kelibsiz. Savol va takliflaringizni shu yerga yozib qoldiring. "
        "Admin tez orada javob beradi."
    )

# Admin va foydalanuvchi aloqasi
@app.on_message(filters.private & ~filters.me)
async def forward_to_admin(client, message):
    if message.from_user.id != ADMIN_ID:
        info = f"📩 **Yangi xabar!**\n👤 Kimdan: {message.from_user.first_name}\n🆔 ID: `{message.from_user.id}`\n\n"
        await app.send_message(ADMIN_ID, info)
        await message.forward(ADMIN_ID)
        await message.reply("✅ Xabaringiz adminga yetkazildi!")
    else:
        if message.reply_to_message and message.reply_to_message.forward_from:
            user_id = message.reply_to_message.forward_from.id
            await message.copy(chat_id=user_id)
            await message.reply("✅ Javobingiz foydalanuvchiga yuborildi!")

async def main():
    # DOIMIYKUNLIK VAQTLAR:
    scheduler.add_job(fetch_and_send_hikmat, "cron", hour=3, minute=00)   # 04:30
    scheduler.add_job(fetch_and_send_hikmat, "cron", hour=5, minute=00)    # 08:00
    scheduler.add_job(fetch_and_send_hikmat, "cron", hour=14, minute=00)  # 14:30
    scheduler.add_job(fetch_and_send_hikmat, "cron", hour=15, minute=00)  # 18:50
    scheduler.add_job(fetch_and_send_hikmat, "cron", hour=16, minute=00)   # 21:00
    scheduler.add_job(fetch_and_send_hikmat, "cron", hour=23, minute=00)  # 22:40

    scheduler.start()
    await app.start()
    print("🚀 Bot muvaffaqiyatli ishga tushdi (Reklama filtri yoqilgan)!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    app.run(main())


import asyncio
import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN = "8099815200:AAH05Qa5PiHbhdC54UdZiLMf0dNeRt4ETwQ"
API_ID = 33118317
API_HASH = "53aae636122c27a99a6c211ecc5d0c68"
REQUIRED_CHANNEL = "oqivaqotaril"

app = Client("iqro_pro_ultra_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
scheduler = AsyncIOScheduler()

SETTINGS_FILE = "user_settings.json"
PASSED_USERS_FILE = "passed_users.json"
STATES_FILE = "user_states.json"
FEEDBACK_FILE = "feedback.json"

click_timers = {}

PREDEFINED_TOPICS = [
    "Oyat", "Hadis", "Sher", "Hikoya", "Hikmat", 
    "Salovat", "Fiqh", "Tarix", "Ruhiyat", "Motivatsiya",
    "Duolar", "Ilm", "Axloq", "Tafsir", "Hammasi"
]

PREDEFINED_CHANNELS = [
    "@oqivaqotaril", "@annuvr", "@ihruz", "@hikmatlar_hazinasi", "@ilm_nuri",
    "@soliham", "@islomuz", "@quran_uz", "@hadis_uz", "@ziyouz",
    "@siyrat_uz", "@tarix_uz", "@ruhiyat_uz", "@salovatchilar", "@duolar_uz"
]

AVAILABLE_TIMES = [
    "05:00", "05:10", "05:20", "05:30", "06:00", "06:10", "06:20", "06:30",
    "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00", "12:10", "12:20", "12:30", "13:00", "13:30",
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
    "18:00", "18:30", "18:50", "19:00", "19:30", "20:00", "20:30", "21:00",
    "21:30", "22:00", "22:30", "22:40", "23:00", "23:30", "00:00", "00:30"
]

TEXTS = {
    "uz_lot": {
        "about": "✨ **'Iqro Pro Ultra' Avto-Post Tizimi**\n\n📜 **Tizim imkoniyatlari:**\n1. Manba kanallaridan eng sara postlarni saralaydi.\n2. Belgilangan mavzular bo'yicha filtrlaydi.\n3. Kanalingizga avtomatik ravishda tayyorlangan postlarni joylaydi.\n\n⚙️ Sozlashni boshlash uchun quyidagi tugmani bosing:",
        "sub_req": "👋 Botdan to'liq foydalanish va sozlash uchun avval rasmiy kanalimizga a'zo bo'ling:",
        "sub_btn": "📢 Kanalga Obuna Bo'lish",
        "verify_btn": "✅ Obunani Tasdiqlash",
        "too_fast": "❌ Tasdiqlash uchun kamida 2 soniya kuting!",
        "verified": "✅ Obuna tasdiqlandi!",
        "main_menu_btn": "⚙️ Avto-postni Sozlash",
        "step1": "🚀 **1-Bosqich: Matn manbasini (Kanalni) tanlang yoki izlang:**",
        "step2": "📂 **2-Bosqich: Qaysi mavzudagi postlar kerak?**",
        "step3": "📢 **3-Bosqich:** Postlar yuboriladigan kanal yoki guruh `@username`ini kiriting:",
        "step4": "⏳ **4-Bosqich: Post yuborish vaqtlarini belgilang:**\n\n*(Tugmalardan tanlang yoki o'zingiz aniq vaqt kiritishingiz mumkin)*",
        "back_btn": "⬅️ Orqaga",
        "home_btn": "🏠 Bosh Menyu",
        "save_btn": "💾 Saqlash va Ishga tushirish",
        "custom_btn": "🔍 Qo'lda kanal izlash",
        "custom_time_btn": "✍️ O'zim vaqt kiritaman",
        "success": "🎉 **Barcha sozlamalar muvaffaqiyatli saqlandi va tizim ishga tushirildi!**",
        "menu_setup": "⚙️ Sozlash",
        "menu_question": "💬 Savol yuborish",
        "menu_suggestion": "💡 Taklif kiritish",
        "menu_help": "🆘 Yordam & Muammolar",
        "menu_about": "📢 Kanalimiz & Bot Haqida",
        "menu_privacy": "🔒 Maxfiylik Siyosati",
        "menu_lang": "🌐 Tilni o'zgartirish",
        "privacy_text": "🔒 **Maxfiylik Siyosati:**\n\n1. Sizning shaxsiy ma'lumotlaringiz va sozlamalaringiz uchinchi shaxslarga berilmaydi.\n2. Bot faqat siz ruxsat bergan kanallarga post joylash vaqtida ishlaydi.\n3. Ma'lumotlaringiz xavfsiz saqlanishi kafolatlanadi.",
        "about_text": "🤖 **Iqro Pro Ultra Bot Haqida:**\n\nBot Telegram kanallar va guruhlarda avtomatik islomiy va ma'rifiy kontentlarni tarqatish uchun ishlab chiqilgan.\n\n📢 Rasmiy kanalimiz: @oqivaqotaril\n💬 Yordam xizmati: @oqivaqotaril",
        "help_text": "🆘 **Yordam va Tez-tez beriladigan savollar:**\n\n❓ **Bot kanalga post tashlamayapti?**\n- Botni o'sha kanalingizga **Admin** qilganingizga va post joylash ruxsatini berganingizga ishonch hosil qiling.\n\n❓ **Custom vaqt qanday kiritiladi?**\n- Sozlashda '✍️ O'zim vaqt kiritaman' tugmasini bosib, `07:15, 14:30, 21:05` ko'rinishida yozing.",
        "ask_question": "💬 **Savolingizni matn shaklida yuboring:**\nBiz tez orada javob beramiz.",
        "ask_suggestion": "💡 **Loyiha bo'yicha taklifingizni yozib qoldiring:**",
        "thanks_feedback": "✅ Qabul qilindi! E'tiboringiz va taklifingiz uchun tashakkur.",
        "enter_custom_time_prompt": "✍️ **Vaqtlarni HH:MM formatida yozib yuboring.**\n\nMasalan: `07:15, 12:45, 18:30`",
        "invalid_time": "❌ Vaqt formati noto'g'ri. Iltimos `08:30` yoki `14:15, 20:00` ko'rinishida kiriting."
    },
    "uz_kir": {
        "about": "✨ **'Iqro Pro Ultra' Авто-Пост Тизими**\n\n📜 **Тизим имкониятлари:**\n1. Манба каналларидан энг сара постларни саралайди.\n2. Белгиланган мавзулар бўйича фильтрлайди.\n3. Каналингизга автоматик равишда тайёрланган постларни жойлайди.\n\n⚙️ Созлашни бошлаш учун қуйидаги тугмани босинг:",
        "sub_req": "👋 Ботдан тўлиқ фойдаланиш учун аввал расмий каналимизга аъзо бўлинг:",
        "sub_btn": "📢 Каналга Обуна Бўлиш",
        "verify_btn": "✅ Обунани Тасдиқлаш",
        "too_fast": "❌ Тасдиқлаш учун камида 2 сония кутинг!",
        "verified": "✅ Обуна тасдиқланди!",
        "main_menu_btn": "⚙️ Авто-постни Созлаш",
        "step1": "🚀 **1-Босқич: Матн манбасини (Канални) танланг ёки изланг:**",
        "step2": "📂 **2-Босқич: Қайси мавзудаги постлар керак?**",
        "step3": "📢 **3-Босқич:** Постлар юбориладиган канал ёки гуруҳ `@username`ини киритинг:",
        "step4": "⏳ **4-Босқич: Пост юбориш вақтларини белгиланг:**",
        "back_btn": "⬅️ Орқага",
        "home_btn": "🏠 Бош Меню",
        "save_btn": "💾 Сақлаш ва Ишга тушириш",
        "custom_btn": "🔍 Қўлда канал излаш",
        "custom_time_btn": "✍️ Ўзим вақт киритаман",
        "success": "🎉 **Барча созламалар муваффақиятли сақланди ва тизим ишга туширилди!**",
        "menu_setup": "⚙️ Созлаш",
        "menu_question": "💬 Савол юбориш",
        "menu_suggestion": "💡 Таклиф киритиш",
        "menu_help": "🆘 Ғёрдам & Муаммолар",
        "menu_about": "📢 Каналимиз & Бот Ҳақида",
        "menu_privacy": "🔒 Махфийлик Сиёсати",
        "menu_lang": "🌐 Тилни ўзгартириш",
        "privacy_text": "🔒 **Махфийлик Сиёсати:**\n\n1. Сизнинг шахсий маълумотларингиз учинчи шахсларга берилмайди.\n2. Бот фақат сиз рухсат берган каналларга пост жойлаш вақтида ишлайди.",
        "about_text": "🤖 **Iqro Pro Ultra Бот Ҳақида:**\n\nТелеграм каналлар ва гуруҳларда автоматик маърифий контентларни тарқатиш тизими.\n\n📢 Расмий канал: @oqivaqotaril",
        "help_text": "🆘 **Ёрдам ва Тез-тез бериладиган саволлар:**\n\n❓ Бот каналга пост ташламаяпти?\n- Ботни каналингизга **Админ** қилганингизга ишонч ҳосил қилинг.",
        "ask_question": "💬 **Саволингизни матн шаклида юборинг:**",
        "ask_suggestion": "💡 **Таклифингизни ёзиб қолдиринг:**",
        "thanks_feedback": "✅ Қабул қилинди! Ташаккур.",
        "enter_custom_time_prompt": "✍️ **Вақтларни HH:MM форматида ёзиб юборинг.**\n\nМасалан: `07:15, 12:45, 18:30`",
        "invalid_time": "❌ Вақт формати нотўғри."
    },
    "ru": {
        "about": "✨ **Система авто-постинга 'Iqro Pro Ultra'**\n\n📜 **Возможности:**\n1. Отбор лучших постов из каналов-источников.\n2. Фильтрация по темам.\n3. Автоматическая публикация в ваш канал.\n\n⚙️ Нажмите кнопку ниже для настройки:",
        "sub_req": "👋 Подпишитесь на наш official канал для продолжения:",
        "sub_btn": "📢 Подписаться на канал",
        "verify_btn": "✅ Подтвердить подписку",
        "too_fast": "❌ Подождите 2 секунды!",
        "verified": "✅ Подписка подтверждена!",
        "main_menu_btn": "⚙️ Настроить авто-постинг",
        "step1": "🚀 **Шаг 1: Выберите или найдите канал-источник:**",
        "step2": "📂 **Шаг 2: Выберите темы постов:**",
        "step3": "📢 **Шаг 3:** Введите `@username` целевого канала или группы:",
        "step4": "⏳ **Шаг 4: Выберите время публикаций:**",
        "back_btn": "⬅️ Назад",
        "home_btn": "🏠 Главное Меню",
        "save_btn": "💾 Сохранить и Запустить",
        "custom_btn": "🔍 Найти канал вручную",
        "custom_time_btn": "✍️ Ввести своё время",
        "success": "🎉 **Все настройки успешно сохранены и запущены!**",
        "menu_setup": "⚙️ Настройки",
        "menu_question": "💬 Задать вопрос",
        "menu_suggestion": "💡 Предложение",
        "menu_help": "🆘 Помощь и Проблемы",
        "menu_about": "📢 О канале и Боте",
        "menu_privacy": "🔒 Политика конфиденциальности",
        "menu_lang": "🌐 Сменить язык",
        "privacy_text": "🔒 **Политика конфиденциальности:**\n\n1. Ваши личные данные не передаются третьим лицам.\n2. Бот работает строго по заданному расписанию.",
        "about_text": "🤖 **О боте Iqro Pro Ultra:**\n\nАвтоматическая система публикации контента.\n📢 Наш канал: @oqivaqotaril",
        "help_text": "🆘 **Помощь:**\n\n❓ Бот не публикует посты?\n- Убедитесь, что бот является **Администратором** канала.",
        "ask_question": "💬 **Напишите ваш вопрос:**",
        "ask_suggestion": "💡 **Оставьте ваше предложение:**",
        "thanks_feedback": "✅ Ваше сообщение принято! Спасибо.",
        "enter_custom_time_prompt": "✍️ **Введите время в формате ЧЧ:ММ.**\nНапример: `07:15, 12:45, 18:30`",
        "invalid_time": "❌ Неверный формат времени."
    },
    "en": {
        "about": "✨ **'Iqro Pro Ultra' Auto-Post System**\n\n📜 **Features:**\n1. Selects top content from source channels.\n2. Filters by selected topics.\n3. Automatically posts to your target channel.\n\n⚙️ Click below to start configuration:",
        "sub_req": "👋 Please subscribe to our official channel to proceed:",
        "sub_btn": "📢 Subscribe to Channel",
        "verify_btn": "✅ Verify Subscription",
        "too_fast": "❌ Please wait at least 2 seconds!",
        "verified": "✅ Subscription verified!",
        "main_menu_btn": "⚙️ Configure Auto-Post",
        "step1": "🚀 **Step 1: Choose or search source channel:**",
        "step2": "📂 **Step 2: Choose post topics:**",
        "step3": "📢 **Step 3:** Enter target channel or group `@username`:",
        "step4": "⏳ **Step 4: Select posting schedule:**",
        "back_btn": "⬅️ Back",
        "home_btn": "🏠 Main Menu",
        "save_btn": "💾 Save & Launch",
        "custom_btn": "🔍 Search channel manually",
        "custom_time_btn": "✍️ Enter custom time",
        "success": "🎉 **All settings saved and system launched successfully!**",
        "menu_setup": "⚙️ Setup",
        "menu_question": "💬 Ask Question",
        "menu_suggestion": "💡 Suggestion",
        "menu_help": "🆘 Help & Support",
        "menu_about": "📢 About Channel & Bot",
        "menu_privacy": "🔒 Privacy Policy",
        "menu_lang": "🌐 Change Language",
        "privacy_text": "🔒 **Privacy Policy:**\n\n1. Your private data is never shared with third parties.\n2. Bot operates safely under explicit administrative rights.",
        "about_text": "🤖 **About Iqro Pro Ultra Bot:**\n\nAutomated Islamic and educational publishing system.\n📢 Official channel: @oqivaqotaril",
        "help_text": "🆘 **Support & FAQ:**\n\n❓ Bot is not posting?\n- Ensure the bot is added as **Administrator** with posting permissions.",
        "ask_question": "💬 **Please send your question:**",
        "ask_suggestion": "💡 **Submit your feedback or suggestion:**",
        "thanks_feedback": "✅ Received! Thank you for your feedback.",
        "enter_custom_time_prompt": "✍️ **Enter time in HH:MM format.**\nExample: `07:15, 12:45, 18:30`",
        "invalid_time": "❌ Invalid time format."
    },
    "ar": {
        "about": "✨ **نظام النشر التلقائي 'إقرأ برو ألترا'**\n\n📜 **المميزات:**\n١. اختيار أفضل المحتويات من القنوات المصدر.\n٢. التصفية والتنقيب حسب المواضيع.\n٣. النشر التلقائي في قناتك الخاصة.\n\n⚙️ اضغط على الزر أدناه لبدء الإعداد:",
        "sub_req": "👋 يرجى الاشتراك في قناتنا الرسمية للاستمرار:",
        "sub_btn": "📢 الاشتراك في القناة",
        "verify_btn": "✅ تأكيد الاشتراك",
        "too_fast": "❌ يرجى الانتظار ثانيتين على الأقل!",
        "verified": "✅ تم تأكيد الاشتراك بنجاح!",
        "main_menu_btn": "⚙️ إعداد النشر التلقائي",
        "step1": "🚀 **الخطوة ١: اختر أو ابحث عن القناة المصدر:**",
        "step2": "📂 **الخطوة ٢: حدد موضوع المنشورات:**",
        "step3": "📢 **الخطوة ٣:** أدخل معرف القناة المستقبلة `@username`:",
        "step4": "⏳ **الخطوة ٤: حدد أوقات النشر:**",
        "back_btn": "⬅️ رجوع",
        "home_btn": "🏠 القائمة الرئيسية",
        "save_btn": "💾 حفظ وتشغيل النظام",
        "custom_btn": "🔍 البحث عن قناة يدوياً",
        "custom_time_btn": "✍️ أدخل وقتاً مخصصاً",
        "success": "🎉 **تم حفظ جميع الإعدادات وتشغيل النظام بنجاح!**",
        "menu_setup": "⚙️ الإعدادات",
        "menu_question": "💬 إرسال سؤال",
        "menu_suggestion": "💡 تقديم اقتراح",
        "menu_help": "🆘 المساعدة والدعم",
        "menu_about": "📢 عن القناة والبوت",
        "menu_privacy": "🔒 سياسة الخصوصية",
        "menu_lang": "🌐 تغيير اللغة",
        "privacy_text": "🔒 **سياسة الخصوصية:**\n\n١. بياناتك الشخصية محفوظة ولن يتم مشاركتها.\n٢. يعمل البوت وفق الصلاحيات الممنوحة له فقط.",
        "about_text": "🤖 **عن بوت إقرأ برو ألترا:**\n\nنظام نشر تلقائي للمحتوى الإسلامي والتعليمي.\n📢 القناة الرسمية: @oqivaqotaril",
        "help_text": "🆘 **المساعدة:**\n\n❓ البوت لا ينشر؟\n- تأكد من إضافة البوت كـ **مشرف (Admin)** في القناة.",
        "ask_question": "💬 **أرسل سؤالك هنا:**",
        "ask_suggestion": "💡 **أرسل اقتراحك هنا:**",
        "thanks_feedback": "✅ تم الاستلام! شكراً لك.",
        "enter_custom_time_prompt": "✍️ **أدخل الوقت بصيغة HH:MM.**\nمثال: `07:15, 12:45, 18:30`",
        "invalid_time": "❌ صيغة الوقت غير صحيحة."
    }
}

def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_user_state(user_id):
    states = load_json(STATES_FILE)
    return states.get(str(user_id), {"lang": "uz_lot"})

def update_user_state(user_id, key, value):
    states = load_json(STATES_FILE)
    u_id = str(user_id)
    if u_id not in states:
        states[u_id] = {"lang": "uz_lot"}
    states[u_id][key] = value
    save_json(STATES_FILE, states)

def get_reply_keyboard(lang):
    txt = TEXTS.get(lang, TEXTS["uz_lot"])
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(txt["menu_setup"]), KeyboardButton(txt["menu_lang"])],
            [KeyboardButton(txt["menu_question"]), KeyboardButton(txt["menu_suggestion"])],
            [KeyboardButton(txt["menu_help"]), KeyboardButton(txt["menu_about"])],
            [KeyboardButton(txt["menu_privacy"])]
        ],
        resize_keyboard=True
    )

STOP_WORDS = ["http://", "https://", "t.me/", "tg.me", "reklama", "aksiya", "chegirma", "tanlov", "homiy"]

def is_ad(text):
    return any(word in text.lower() for word in STOP_WORDS)

def get_post_by_topics(channel, keywords):
    chan_username = channel.replace("@", "").strip()
    url = f"https://t.me/s/{chan_username}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            msgs = soup.find_all('div', class_='tgme_widget_message_text')
            for msg in reversed(msgs):
                for br in msg.find_all('br'):
                    br.replace_with('\n')
                text = msg.get_text().strip()
                if len(text) > 15 and not is_ad(text):
                    if keywords:
                        if any(word.lower() in text.lower() for word in keywords):
                            return text
                    else:
                        return text
    except Exception:
        pass
    return None

async def cron_checker():
    from datetime import datetime
    now = datetime.now().strftime("%H:%M")
    settings = load_json(SETTINGS_FILE)
    for user_id, config in settings.items():
        user_times = config.get("times", [])
        if now in user_times:
            target_chat = config.get("target_chat")
            source_channel = config.get("source_channel")
            keywords = config.get("keywords", [])
            if not target_chat or not source_channel:
                continue
            content = await asyncio.to_thread(get_post_by_topics, source_channel, keywords)
            if content:
                formatted_text = f"{content}\n\n✍️ **Manba:** {source_channel}\n\n©️iqro 📚🕊️"
                try:
                    await app.send_message(target_chat, formatted_text, parse_mode=None)
                except Exception:
                    pass

@app.on_message(filters.command(["start", "help", "savol", "taklif", "privacy"]) & filters.private)
async def commands_handler(client, message):
    user_id = str(message.from_user.id)
    cmd = message.command[0] if message.command else "start"
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS[lang]

    if cmd == "start":
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🇺🇿 O'zbekcha (Lotin)", callback_data="lang_uz_lot")],
            [InlineKeyboardButton("🇺🇿 Ўзбекча (Кирил)", callback_data="lang_uz_kir")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"), InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")]
        ])
        await message.reply(
            "🌐 **Muloqot tilini tanlang / Выберите язык / Choose language / اختر اللغة:**",
            reply_markup=btn
        )
    elif cmd == "help":
        await message.reply(txt["help_text"], reply_markup=get_reply_keyboard(lang))
    elif cmd == "savol":
        update_user_state(user_id, "expecting", "user_question")
        await message.reply(txt["ask_question"], reply_markup=get_reply_keyboard(lang))
    elif cmd == "taklif":
        update_user_state(user_id, "expecting", "user_suggestion")
        await message.reply(txt["ask_suggestion"], reply_markup=get_reply_keyboard(lang))
    elif cmd == "privacy":
        await message.reply(txt["privacy_text"], reply_markup=get_reply_keyboard(lang))

@app.on_callback_query(filters.regex(r"^lang_"))
async def handle_lang_choice(client, callback):
    lang = callback.data.replace("lang_", "")
    user_id = str(callback.from_user.id)
    
    update_user_state(user_id, "lang", lang)
    passed_users = load_json(PASSED_USERS_FILE)
    
    if user_id in passed_users:
        await callback.message.delete()
        await show_main_menu(callback.message, lang)
    else:
        click_timers[user_id] = time.time()
        txt = TEXTS[lang]
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton(txt["sub_btn"], url=f"https://t.me/{REQUIRED_CHANNEL}")],
            [InlineKeyboardButton(txt["verify_btn"], callback_data="check_subscription")]
        ])
        await callback.message.edit_text(
            f"{txt['about']}\n\n{txt['sub_req']} @{REQUIRED_CHANNEL}",
            reply_markup=btn
        )

@app.on_callback_query(filters.regex("check_subscription"))
async def check_sub_callback(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS[lang]
    
    current_time = time.time()
    start_time = click_timers.get(user_id, current_time)
    
    if (current_time - start_time) < 2.0:
        await callback.answer(txt["too_fast"], show_alert=True)
        return

    passed_users = load_json(PASSED_USERS_FILE)
    passed_users[user_id] = True
    save_json(PASSED_USERS_FILE, passed_users)
    
    await callback.answer(txt["verified"], show_alert=False)
    try: await callback.message.delete()
    except: pass
    
    await show_main_menu(callback.message, lang)

async def show_main_menu(message, lang="uz_lot"):
    txt = TEXTS[lang]
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton(txt["main_menu_btn"], callback_data="step_1_source")]
    ])
    await app.send_message(
        chat_id=message.chat.id,
        text=txt["about"],
        reply_markup=get_reply_keyboard(lang)
    )
    await message.reply(txt["about"], reply_markup=btn)

@app.on_callback_query(filters.regex("step_1_source"))
async def step_1_source(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS[lang]
    
    buttons = []
    for i in range(0, len(PREDEFINED_CHANNELS), 2):
        row = [InlineKeyboardButton(PREDEFINED_CHANNELS[i], callback_data=f"src_{PREDEFINED_CHANNELS[i]}")]
        if i + 1 < len(PREDEFINED_CHANNELS):
            row.append(InlineKeyboardButton(PREDEFINED_CHANNELS[i+1], callback_data=f"src_{PREDEFINED_CHANNELS[i+1]}"))
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(txt["custom_btn"], callback_data="src_custom")])
    buttons.append([InlineKeyboardButton(txt["home_btn"], callback_data="go_home")])
    
    await callback.message.edit_text(txt["step1"], reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"^src_"))
async def handle_source_choice(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS[lang]
    src = callback.data.replace("src_", "")
    
    if src == "custom":
        update_user_state(user_id, "expecting", "source")
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton(txt["back_btn"], callback_data="step_1_source")],
            [InlineKeyboardButton(txt["home_btn"], callback_data="go_home")]
        ])
        await callback.message.edit_text("📝 Kanal username-ini yozib kiriting (Masalan: `@annuvr`):", reply_markup=btn)
    else:
        update_user_state(user_id, "source_channel", src)
        await show_step_2_topics(callback.message, lang)

async def show_step_2_topics(message, lang="uz_lot"):
    txt = TEXTS[lang]
    buttons = []
    for i in range(0, len(PREDEFINED_TOPICS), 3):
        row = []
        for top in PREDEFINED_TOPICS[i:i+3]:
            row.append(InlineKeyboardButton(f"📌 {top}", callback_data=f"top_{top}"))
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(txt["back_btn"], callback_data="step_1_source"), InlineKeyboardButton(txt["home_btn"], callback_data="go_home")])
    
    await message.edit_text(txt["step2"], reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"^top_"))
async def handle_topic_choice(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    top = callback.data.replace("top_", "")
    
    if top == "Hammasi":
        update_user_state(user_id, "keywords", [])
    else:
        update_user_state(user_id, "keywords", [top.lower()])
        
    update_user_state(user_id, "expecting", "target_chat")
    txt = TEXTS[lang]
    
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton(txt["back_btn"], callback_data="step_2_back"), InlineKeyboardButton(txt["home_btn"], callback_data="go_home")]
    ])
    await callback.message.edit_text(txt["step3"], reply_markup=btn)

@app.on_callback_query(filters.regex("step_2_back"))
async def step_2_back(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    await show_step_2_topics(callback.message, lang)

@app.on_callback_query(filters.regex("go_home"))
async def go_home_callback(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS[lang]
    btn = InlineKeyboardMarkup([[InlineKeyboardButton(txt["main_menu_btn"], callback_data="step_1_source")]])
    await callback.message.edit_text(txt["about"], reply_markup=btn)

async def show_step_4_times(message, user_id, lang="uz_lot"):
    txt = TEXTS[lang]
    state = get_user_state(user_id)
    selected = state.get("selected_times", [])
    
    buttons = []
    for i in range(0, len(AVAILABLE_TIMES), 4):
        row = []
        for t in AVAILABLE_TIMES[i:i+4]:
            mark = "✅ " if t in selected else "▫️ "
            row.append(InlineKeyboardButton(f"{mark}{t}", callback_data=f"tm_{t}"))
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(txt["custom_time_btn"], callback_data="custom_time_input")])
    buttons.append([InlineKeyboardButton(txt["save_btn"], callback_data="save_all")])
    buttons.append([InlineKeyboardButton(txt["back_btn"], callback_data="step_2_back"), InlineKeyboardButton(txt["home_btn"], callback_data="go_home")])
    
    await message.reply(txt["step4"], reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex("custom_time_input"))
async def custom_time_input_cb(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS[lang]
    
    update_user_state(user_id, "expecting", "custom_time")
    await callback.message.edit_text(txt["enter_custom_time_prompt"])

@app.on_callback_query(filters.regex(r"^tm_"))
async def toggle_time(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    t = callback.data.replace("tm_", "")
    
    selected = state.get("selected_times", [])
    if t in selected:
        selected.remove(t)
    else:
        selected.append(t)
        
    update_user_state(user_id, "selected_times", selected)
    await callback.message.delete()
    await show_step_4_times(callback.message, user_id, lang)

@app.on_callback_query(filters.regex("save_all"))
async def save_all_settings(client, callback):
    user_id = str(callback.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS[lang]
    
    settings = load_json(SETTINGS_FILE)
    settings[user_id] = {
        "source_channel": state.get("source_channel"),
        "keywords": state.get("keywords", []),
        "target_chat": state.get("target_chat"),
        "times": state.get("selected_times", [])
    }
    save_json(SETTINGS_FILE, settings)
    
    await callback.message.edit_text(txt["success"])

@app.on_message(filters.private & ~filters.command(["start", "help", "savol", "taklif", "privacy"]))
async def handle_text_inputs(client, message):
    user_id = str(message.from_user.id)
    state = get_user_state(user_id)
    lang = state.get("lang", "uz_lot")
    txt = TEXTS[lang]
    
    text = message.text.strip()
    
    # Klaviatura menyu tugmalari bosilganda:
    if text == txt["menu_setup"]:
        await show_main_menu(message, lang)
        return
    elif text == txt["menu_question"]:
        update_user_state(user_id, "expecting", "user_question")
        await message.reply(txt["ask_question"])
        return
    elif text == txt["menu_suggestion"]:
        update_user_state(user_id, "expecting", "user_suggestion")
        await message.reply(txt["ask_suggestion"])
        return
    elif text == txt["menu_help"]:
        await message.reply(txt["help_text"])
        return
    elif text == txt["menu_about"]:
        await message.reply(txt["about_text"])
        return
    elif text == txt["menu_privacy"]:
        await message.reply(txt["privacy_text"])
        return
    elif text == txt["menu_lang"]:
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🇺🇿 O'zbekcha (Lotin)", callback_data="lang_uz_lot")],
            [InlineKeyboardButton("🇺🇿 Ўзбекча (Кирил)", callback_data="lang_uz_kir")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"), InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")]
        ])
        await message.reply("🌐 **Muloqot tilini tanlang:**", reply_markup=btn)
        return

    exp = state.get("expecting")
    
    if exp == "source":
        update_user_state(user_id, "source_channel", text)
        update_user_state(user_id, "expecting", None)
        msg = await message.reply("✅")
        await show_step_2_topics(msg, lang)
        
    elif exp == "target_chat":
        update_user_state(user_id, "target_chat", text)
        update_user_state(user_id, "expecting", None)
        update_user_state(user_id, "selected_times", [])
        await show_step_4_times(message, user_id, lang)
        
    elif exp == "custom_time":
        # HH:MM formatlarini ajratib olish
        times_found = re.findall(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b", text)
        if times_found:
            selected = state.get("selected_times", [])
            for t in times_found:
                if len(t) == 4 and t[1] == ':':
                    t = '0' + t # 7:15 -> 07:15
                if t not in selected:
                    selected.append(t)
            update_user_state(user_id, "selected_times", selected)
            update_user_state(user_id, "expecting", None)
            await message.reply("✅ Vaqtlar qo'shildi!")
            await show_step_4_times(message, user_id, lang)
        else:
            await message.reply(txt["invalid_time"])

    elif exp in ["user_question", "user_suggestion"]:
        feedbacks = load_json(FEEDBACK_FILE)
        if user_id not in feedbacks: feedbacks[user_id] = []
        feedbacks[user_id].append({"type": exp, "text": text, "time": time.strftime("%Y-%m-%d %H:%M:%S")})
        save_json(FEEDBACK_FILE, feedbacks)
        
        update_user_state(user_id, "expecting", None)
        await message.reply(txt["thanks_feedback"])

async def main():
    scheduler.add_job(cron_checker, "interval", minutes=1)
    scheduler.start()
    await app.start()
    print("🚀 Iqro Pro Ultra Max bot ishga tushdi!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    app.run(main())

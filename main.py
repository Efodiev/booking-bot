import asyncio, os, logging
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для красивой даты
def format_dt(iso_string):
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%d.%m в %H:%M")
    except:
        return iso_string

# 1. ТЕБЕ: Новая заявка на регистрацию МАСТЕРА
async def handle_new_master(request):
    data = await request.json()
    name = data.get("master_name") or data.get("name") or "Не указано"
    m_id = data.get("master_id") or data.get("id") or "ID не передан"
    
    text = (f"⭐️ <b>НОВАЯ ЗАЯВКА: МАСТЕР</b>\n\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"🆔 <b>ID:</b> <code>{m_id}</code>\n\n"
            f"📥 Пожалуйста, проверьте и одобрите в админ-панели.")
    await bot.send_message(ADMIN_ID, text, parse_mode="HTML")
    return web.Response(text="OK")

# 2. МАСТЕРУ: Кабинет одобрен
async def handle_approve_master(request):
    data = await request.json()
    tg_id = data.get("telegram_id") or data.get("master_telegram_id")
    if tg_id:
        text = ("🎉 <b>ДОБРО ПОЖАЛОВАТЬ!</b>\n\n"
                "Ваш профиль мастера успешно <b>одобрен</b>.\n"
                "Теперь вы можете настроить услуги, график и принимать записи.")
        await bot.send_message(tg_id, text, parse_mode="HTML")
    return web.Response(text="OK")

# 3. МАСТЕРУ: Новая запись от клиента
async def handle_new_booking(request):
    data = await request.json()
    tg_id = data.get("master_telegram_id")
    if tg_id:
        time = format_dt(data.get("time"))
        text = (f"📅 <b>НОВАЯ ЗАПИСЬ</b>\n\n"
                f"👤 <b>Клиент:</b> {data.get('client_name')}\n"
                f"✂️ <b>Услуга:</b> {data.get('service')}\n"
                f"⏰ <b>Время:</b> {time}\n\n"
                f"📥 Подтвердите запись в личном кабинете.")
        await bot.send_message(tg_id, text, parse_mode="HTML")
    return web.Response(text="OK")

# 4. КЛИЕНТУ: Запись подтверждена
async def handle_booking_confirmed(request):
    data = await request.json()
    tg_id = data.get("client_telegram_id")
    if tg_id:
        time = format_dt(data.get("time"))
        text = (f"✅ <b>ЗАПИСЬ ПОДТВЕРЖДЕНА</b>\n\n"
                f"📍 <b>Мастер:</b> {data.get('master_name')}\n"
                f"✂️ <b>Услуга:</b> {data.get('service')}\n"
                f"⏰ <b>Время:</b> {time}\n\n"
                f"До встречи!")
        await bot.send_message(tg_id, text, parse_mode="HTML")
    return web.Response(text="OK")

# 5. КЛИЕНТУ: Запись отклонена
async def handle_booking_rejected(request):
    data = await request.json()
    tg_id = data.get("client_telegram_id")
    if tg_id:
        text = (f"❌ <b>ЗАПИСЬ ОТМЕНЕНА</b>\n\n"
                f"Мастер <b>{data.get('master_name')}</b> отклонил вашу заявку.\n"
                f"💬 <b>Причина:</b> {data.get('reason', 'Не указана')}")
        await bot.send_message(tg_id, text, parse_mode="HTML")
    return web.Response(text="OK")

async def main():
    app = web.Application()
    app.router.add_post("/webhook/new_master", handle_new_master)
    app.router.add_post("/webhook/approve_master", handle_approve_master)
    app.router.add_post("/webhook/new_booking", handle_new_booking)
    app.router.add_post("/webhook/booking_confirmed", handle_booking_confirmed)
    app.router.add_post("/webhook/booking_rejected", handle_booking_rejected)
    
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 10000))).start()
    
    # Режим поллинга для команд бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    

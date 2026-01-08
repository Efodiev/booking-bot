import asyncio, os, logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")
ADMIN_ID = os.getenv("ADMIN_ID") # Твой ID из @userinfobot

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# 1. Новая заявка на регистрацию МАСТЕРА (Тебе)
async def handle_new_master(request):
    data = await request.json()
    await bot.send_message(ADMIN_ID, f"🆕 <b>Новый мастер!</b>\nИмя: {data.get('name')}\nID: {data.get('id')}\nОдобрите в админке.")
    return web.Response(text="OK")

# 2. Мастер одобрен (Мастеру)
async def handle_approve_master(request):
    data = await request.json()
    await bot.send_message(data.get("telegram_id"), "🎉 <b>Поздравляем!</b>\nВаш кабинет одобрен. Настройте услуги и расписание.")
    return web.Response(text="OK")

# 3. КЛИЕНТ записался (Мастеру)
async def handle_new_booking(request):
    data = await request.json()
    await bot.send_message(data.get("master_telegram_id"), 
        f"📅 <b>Новая заявка на запись!</b>\nКлиент: {data.get('client_name')}\nУслуга: {data.get('service')}\nВремя: {data.get('time')}\nЖдет вашего одобрения в кабинете.")
    return web.Response(text="OK")

# 4. Мастер ОДОБРИЛ (Клиенту)
async def handle_booking_confirmed(request):
    data = await request.json()
    await bot.send_message(data.get("client_telegram_id"), 
        f"✅ <b>Запись подтверждена!</b>\nМастер: {data.get('master_name')}\nУслуга: {data.get('service')}\nВремя: {data.get('time')}")
    return web.Response(text="OK")

# 5. Мастер ОТКЛОНИЛ (Клиенту)
async def handle_booking_rejected(request):
    data = await request.json()
    await bot.send_message(data.get("client_telegram_id"), 
        f"❌ <b>Запись отклонена</b>\nМастер: {data.get('master_name')}\nПричина: {data.get('reason')}")
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
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    

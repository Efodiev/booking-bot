import asyncio
import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")
ADMIN_ID = os.getenv("ADMIN_ID")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- ВЕБХУК: НОВАЯ ЗАЯВКА НА РЕГИСТРАЦИЮ МАСТЕРА ---
async def handle_new_master(request):
    data = await request.json()
    master_name = data.get("name", "Новый мастер")
    master_id = data.get("id")
    if ADMIN_ID:
        await bot.send_message(int(ADMIN_ID), f"🔔 <b>Новая заявка мастера!</b>\n\nИмя: {master_name}\nID: {master_id}\n\nПроверьте в админ-панели приложения.", parse_mode="HTML")
    return web.Response(text="OK")

# --- ВЕБХУК: ОДОБРЕНИЕ МАСТЕРА АДМИНОМ ---
async def handle_approve_master(request):
    data = await request.json()
    master_tg_id = data.get("telegram_id")
    if master_tg_id:
        try:
            await bot.send_message(
                int(master_tg_id), 
                "🎉 <b>Поздравляем!</b>\n\nВаша анкета мастера одобрена. Теперь вы можете настроить свой профиль, услуги и расписание в личном кабинете.",
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Error sending msg: {e}")
    return web.Response(text="OK")

# --- ВЕБХУК: ПОДТВЕРЖДЕНИЕ ЗАПИСИ КЛИЕНТУ ---
async def handle_booking_confirmed(request):
    data = await request.json()
    client_tg_id = data.get("client_telegram_id")
    master_name = data.get("master_name")
    service = data.get("service_name")
    date_time = f"{data.get('date')} в {data.get('time')}"
    
    if client_tg_id:
        await bot.send_message(
            int(client_tg_id), 
            f"✅ <b>Запись подтверждена!</b>\n\nМастер <b>{master_name}</b> ждет вас на услугу '{service}'\n📅 {date_time}",
            parse_mode="HTML"
        )
    return web.Response(text="OK")

# --- ВЕБХУК: ОТКЛОНЕНИЕ ЗАПИСИ КЛИЕНТУ ---
async def handle_booking_rejected(request):
    data = await request.json()
    client_tg_id = data.get("client_telegram_id")
    master_name = data.get("master_name")
    reason = data.get("reason", "Причина не указана")
    
    if client_tg_id:
        await bot.send_message(
            int(client_tg_id), 
            f"❌ <b>Запись отклонена</b>\n\nМастер <b>{master_name}</b> не сможет принять вас.\n💬 Причина: {reason}",
            parse_mode="HTML"
        )
    return web.Response(text="OK")

@dp.message(CommandStart())
async def start(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть приложение", web_app=WebAppInfo(url=APP_URL))]
    ])
    await message.answer(f"Привет, {message.from_user.first_name}! Это сервис записи к мастерам ПМР.", reply_markup=markup)

async def main():
    app = web.Application()
    # Регистрация всех путей для уведомлений
    app.router.add_post("/webhook/new_master", handle_new_master)
    app.router.add_post("/webhook/approve_master", handle_approve_master)
    app.router.add_post("/webhook/booking_confirmed", handle_booking_confirmed)
    app.router.add_post("/webhook/booking_rejected", handle_booking_rejected)
    
    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    

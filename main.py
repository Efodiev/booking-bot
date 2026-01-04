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

# --- ВЕБХУК: НОВАЯ ЗАЯВКА ---
async def handle_new_master(request):
    data = await request.json()
    master_name = data.get("name", "Новый мастер")
    master_id = data.get("id")
    if ADMIN_ID:
        await bot.send_message(int(ADMIN_ID), f"🔔 Новая заявка!\nИмя: {master_name}\nID: {master_id}\nПроверьте в админ-панели приложения.")
    return web.Response(text="OK")

# --- ВЕБХУК: ОДОБРЕНИЕ (НОВОЕ!) ---
async def handle_approve_master(request):
    data = await request.json()
    master_tg_id = data.get("telegram_id")
    if master_tg_id:
        try:
            await bot.send_message(
                int(master_tg_id), 
                "🎉 <b>Поздравляем!</b>\n\nВаша анкета мастера одобрена. Теперь вы можете настроить свой профиль и принимать заказы в личном кабинете.",
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Error sending msg: {e}")
    return web.Response(text="OK")

@dp.message(CommandStart())
async def start(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть приложение", web_app=WebAppInfo(url=APP_URL))]
    ])
    await message.answer(f"Привет, {message.from_user.first_name}! Это сервис записи к мастерам ПМР.", reply_markup=markup)

async def main():
    app = web.Application()
    app.router.add_post("/webhook/new_master", handle_new_master)
    app.router.add_post("/webhook/approve_master", handle_approve_master) # Регистрация нового пути
    
    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

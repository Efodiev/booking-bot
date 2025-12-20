import asyncio
import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# Настройки берутся из Secrets
API_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Веб-сервер для Hugging Face ---
async def handle(request):
    return web.Response(text="Бот активен и работает!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # HF требует порт 7860
    site = web.TCPSite(runner, "0.0.0.0", 7860)
    await site.start()

# --- Логика бота ---
@dp.message(CommandStart())
async def start(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💅 Записаться на услугу", 
            web_app=WebAppInfo(url=APP_URL)
        )]
    ])
    
    await message.answer(
        f"Здравствуйте, {message.from_user.first_name}! 👋\n\n"
        "Это официальный бот для записи. Нажмите кнопку ниже, "
        "чтобы выбрать мастера и удобное время.",
        reply_markup=markup
    )

async def main():
    # Запускаем сервер "заглушку"
    asyncio.create_task(start_web_server())
    # Запускаем бота
    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

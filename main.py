import asyncio
import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ИЗ СЕКРЕТОВ ---
API_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")
# Получаем ADMIN_ID из секретов Render
ADMIN_ID = os.getenv("ADMIN_ID")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- ЛОГИКА ПРИЕМА ЗАЯВОК ОТ LOVABLE (WEBHOOK) ---
async def handle_new_master(request):
    try:
        data = await request.json()
        master_name = data.get("name", "Новый мастер")
        master_id = data.get("id", "неизвестно")
        
        if ADMIN_ID:
            # Кнопки для админа (тебя)
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"appr_{master_id}")],
                [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"rejc_{master_id}")]
            ])
            
            await bot.send_message(
                int(ADMIN_ID), 
                f"🔔 <b>Новая заявка на регистрацию!</b>\n\n"
                f"👤 <b>Имя:</b> {master_name}\n"
                f"🆔 <b>ID в базе:</b> <code>{master_id}</code>\n\n"
                f"Проверьте анкету в базе и выберите действие:",
                parse_mode="HTML",
                reply_markup=markup
            )
        return web.Response(text="OK", status=200)
    except Exception as e:
        logging.error(f"Error in webhook: {e}")
        return web.Response(text="Error", status=500)

# --- ОБРАБОТКА КОМАНДЫ /START ---
@dp.message(CommandStart())
async def start(message: types.Message):
    welcome_text = (
        f"<b>Приветствуем, {message.from_user.first_name}!</b> ✨\n\n"
        "Вы попали в сервис онлайн-записи к мастерам Приднестровья.\n\n"
        "🔹 <b>Выбирайте</b> своего мастера\n"
        "🔹 <b>Смотрите</b> реальное расписание\n"
        "🔹 <b>Записывайтесь</b> в один клик\n\n"
        "<i>Нажмите кнопку ниже, чтобы открыть приложение:</i>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🚀 Открыть запись", 
        web_app=WebAppInfo(url=APP_URL))
    )

    # Используем стильное фото для приветствия
    photo_url = "https://images.unsplash.com/photo-1560066984-138dadb4c035?q=80&w=1000&auto=format&fit=crop"
    
    try:
        await message.answer_photo(
            photo=photo_url,
            caption=welcome_text,
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
    except:
        # Если фото не загрузится, отправим просто текст
        await message.answer(welcome_text, parse_mode="HTML", reply_markup=builder.as_markup())

# --- ОБРАБОТКА КНОПОК ОДОБРЕНИЯ (ДЛЯ АДМИНА) ---
@dp.callback_query(F.data.startswith("appr_"))
async def approve_callback(callback: types.CallbackQuery):
    master_id = callback.data.split("_")[1]
    await callback.answer("В разработке...")
    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n⏳ <b>Мастер {master_id} будет активирован через админ-панель Lovable.</b>",
        parse_mode="HTML"
    )

# --- ЗАПУСК ВСЕЙ СИСТЕМЫ ---
async def main():
    # Настраиваем веб-сервер для Lovable
    app = web.Application()
    app.router.add_post("/webhook/new_master", handle_new_master)
    
    # Render использует порт 10000 по умолчанию
    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    
    # Запускаем сервер и бота одновременно
    await site.start()
    logging.info(f"Web server started on port {port}")
    
    print("Бот запущен и ожидает сообщений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")

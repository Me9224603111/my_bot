import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === Настройки ===
TOKEN = "8151771562:AAEL7USxHEfnjcT6CSBtapqFL2Z4eZPqTUw"
GROUP_ID = -1001304012145
ADMIN_ID = 199804963

# === Google Таблицы ===
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
gc = gspread.authorize(credentials)

TABLE_1_ID = "1rzqSH5B7FAGzihe5UgWjydgzQoQfL-dO"
TABLE_2_ID = "YOUR_TABLE_ID_2"

# === Инициализация бота и диспетчера ===
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher()

# === Планировщик ===
scheduler = AsyncIOScheduler()

# === Напоминание ===
async def send_reminder():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Заполнил", callback_data="filled")],
        [InlineKeyboardButton(text="⏳ Отложить", callback_data="postpone")]
    ])
    
    message = (
        f"🔔 *Напоминание!* Сегодня 20-е число.\n"
        f"Заполните таблицы:\n"
        f"📄 [Результаты конкурсов](https://docs.google.com/spreadsheets/d/{TABLE_1_ID})\n"
        f"📄 [Мероприятия](https://docs.google.com/spreadsheets/d/{TABLE_2_ID})"
    )

    await bot.send_message(GROUP_ID, message, reply_markup=keyboard)

# === Обработчик команды /start ===
@dp.message(F.text == "/start")
async def start_command(message: Message):
    await message.answer("Привет, я бот ДШИ! Готов напоминать о важных делах 😊")

# === Callback-обработчики ===
@dp.callback_query(F.data == "filled")
async def handle_filled(callback: CallbackQuery):
    user = callback.from_user.full_name
    await bot.send_message(ADMIN_ID, f"✅ {user} заполнил таблицу!")
    await callback.answer("Спасибо! Отчёт отправлен.")

@dp.callback_query(F.data == "postpone")
async def handle_postpone(callback: CallbackQuery):
    await callback.answer("Окей, напомню позже!")

# === Главный цикл ===
async def main():
    scheduler.add_job(send_reminder, "cron", day=20, hour=10, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
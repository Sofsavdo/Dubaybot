import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
from dotenv import load_dotenv

# .env faylidan tokenni olish
load_dotenv()
API_TOKEN = os.getenv("7814722343:AAFTjh31Li3YcJamaexorwWUjJqR9nEr3mw")

# Bot va Dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Ma'lumotlar bazasini yaratish
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, coins INTEGER DEFAULT 0, referrals INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# Start komandasi
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, coins) VALUES (?, 0)", (user_id,))
    conn.commit()
    conn.close()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = types.WebAppInfo(url="https://sofsavdo.github.io/dubaygame/game.html")  # Bu URL ni keyin o‘zgartiramiz
    keyboard.add(types.KeyboardButton("🎮 O‘yinni boshlash", web_app=web_app))
    keyboard.add("📊 Hisobim", "👥 Do‘st taklif qilish")
    await message.reply("Dubay Biznes Botga Xush kelibsiz!\n"
                        "O‘yinni boshlash uchun tugmani bosing!", reply_markup=keyboard)

# Hisobni ko‘rish
@dp.message_handler(lambda message: message.text == "📊 Hisobim")
async def check_balance(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT coins, referrals FROM users WHERE user_id = ?", (user_id,))
    data = c.fetchone()
    coins, referrals = data[0], data[1]
    conn.close()
    await message.reply(f"💰 Sizning hisobingiz:\n"
                        f"Coins: {coins}\n"
                        f"Referallar: {referrals}")

# Referral link
@dp.message_handler(lambda message: message.text == "👥 Do‘st taklif qilish")
async def invite_friend(message: types.Message):
    user_id = message.from_user.id
    referral_link = f"https://t.me/DubayBiznesBot?start={user_id}"
    await message.reply(f"Do‘stingizni taklif qiling va bonus oling!\n"
                        f"Sizning referral linkingiz: {referral_link}")

# Botni ishga tushirish
if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)
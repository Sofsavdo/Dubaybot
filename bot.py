import os
import json
import sqlite3
import asyncio
from aiogram import Bot, Router, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

# Router va Bot
router = Router()
storage = MemoryStorage()
bot = Bot(token=os.getenv("7984746447:AAFRxkL7oBEe1Bzxe5gFi3Igxvvh-6bJ9YU"))

# Ma'lumotlar bazasini yaratish
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, coins INTEGER DEFAULT 0, referrals INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# Start komandasi
@router.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, coins) VALUES (?, 0)", (user_id,))
    conn.commit()
    conn.close()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = types.WebAppInfo(url="https://sofsavdo.github.io/dubaygame/game.html")
    keyboard.add(types.KeyboardButton("🎮 O‘yinni boshlash", web_app=web_app))
    keyboard.add("📊 Hisobim", "👥 Do‘st taklif qilish")
    await message.reply("Dubay Biznes Botga Xush kelibsiz!\n"
                        "O‘yinni boshlash uchun tugmani bosing!", reply_markup=keyboard)

# Hisobni ko‘rish
@router.message(lambda message: message.text == "📊 Hisobim")
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
@router.message(lambda message: message.text == "👥 Do‘st taklif qilish")
async def invite_friend(message: types.Message):
    user_id = message.from_user.id
    referral_link = f"https://t.me/DubayBiznesBot?start={user_id}"
    await message.reply(f"Do‘stingizni taklif qiling va bonus oling!\n"
                        f"Sizning referral linkingiz: {referral_link}")

# Web App’dan ma'lumot qabul qilish
@router.message(content_types=['web_app_data'])
async def web_app_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    user_id = data['userId']
    coins = data['coins']
    
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET coins = ? WHERE user_id = ?", (coins, user_id))
    conn.commit()
    conn.close()
    
    await message.reply(f"Hisobingiz yangilandi! Jami coinlar: {coins}")

# Botni ishga tushirish
async def main():
    init_db()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    print("Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

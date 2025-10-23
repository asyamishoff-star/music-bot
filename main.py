import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import LabeledPrice
from aiogram.types.message import ContentType
from flask import Flask
from threading import Thread

# === Flask для keep_alive ===
app = Flask('')

@app.route('/')
def home():
    return "Бот жив! 🎵"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === Telegram Bot ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # ставишь свой токен
PROVIDER_TOKEN = os.environ.get("PROVIDER_TOKEN")  # токен платежей

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Альбом
album = {
    "title": "Доступ к нашей музыке",
    "description": "Живая запись с концерта, без студийной обработки!",
    "price": 50000,  # в копейках
    "download_link": "https://disk.yandex.ru/d/ZGdxYMizv8M78g"
}

# === Обработчики ===
@dp.message(commands=["start"])
async def start(msg: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text="Доступ к нашей музыке",
        callback_data="buy_album"
    ))
    keyboard.add(InlineKeyboardButton(
        text="Поддержка",
        url="https://t.me/bill_yagyaev"
    ))
    keyboard.add(InlineKeyboardButton(
        text="Сайт группы",
        url="https://twoviolins.ru"
    ))
    await msg.answer("Привет! Здесь можно купить доступ к музыке.", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "buy_album")
async def buy_album(query: types.CallbackQuery):
    prices = [LabeledPrice(label=album["title"], amount=album["price"])]
    await bot.send_invoice(
        chat_id=query.from_user.id,
        title=album["title"],
        description=album["description"],
        provider_token=PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="buy-album",
        payload=album["title"],
    )

@dp.pre_checkout_query()
async def checkout(query: types.PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(content_types=[ContentType.SUCCESSFUL_PAYMENT])
async def payment_success(msg: types.Message):
    await msg.answer(f"Спасибо! Вот твоя ссылка: {album['download_link']}")

# === Запуск ===
if __name__ == "__main__":
    keep_alive()
    asyncio.run(dp.start_polling(bot))

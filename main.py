import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread

# === Flask для "бессмертия" на Render ===
app = Flask('')

@app.route('/')
def home():
    return "Бот жив! 🎵"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Токены через переменные окружения (в Render Environment)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PROVIDER_TOKEN = os.environ.get("PROVIDER_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Альбом
album = {
    "title": "Доступ к нашей музыке",
    "description": (
        "Внимание, дружище! Тебя ждёт лайв-запись с нашего концерта!\n"
        "Живая энергетика, реальные эмоции, без студийной обработки!\n"
        "Если вдруг звук не зайдёт, без проблем вернём деньги!\n"
    ),
    "price": 50000,  # в копейках
    "download_link": "https://disk.yandex.ru/d/ZGdxYMizv8M78g"
}

# Стартовое сообщение с картинкой и кнопками
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        text="Доступ к нашей музыке",
        callback_data="show_album"
    ))
    keyboard.add(types.InlineKeyboardButton(
        text="Поддержка",
        url="https://t.me/bill_yagyaev"
    ))
    keyboard.add(types.InlineKeyboardButton(
        text="Сайт группы",
        url="https://twoviolins.ru"
    ))
    await bot.send_photo(
        chat_id=msg.chat.id,
        photo="https://i.postimg.cc/y8WttMHX/photo-2025-09-09-13-29-45.jpg",  # стартовая картинка
        caption="Привет, меломан! Рады видеть тебя в нашем музыкальном уголке!\n"
                "Здесь можно достать эксклюзивчик от Two Violins – погрузиться в наш симфорок и кайфануть по полной!😎",
        reply_markup=keyboard
    )

# Кнопка "Доступ к нашей музыке"
@dp.callback_query_handler(lambda c: c.data == "show_album")
async def show_album(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        text="Купить",
        callback_data="buy_album"
    ))
    await bot.send_animation(
        chat_id=callback_query.from_user.id,
        animation="https://i.postimg.cc/3JxYqz2G/album.gif",  # гифка альбома
        caption=f"{album['title']}\n\n{album['description']}",
        reply_markup=keyboard
    )

# Кнопка "Купить"
@dp.callback_query_handler(lambda c: c.data == "buy_album")
async def process_buy_callback(callback_query: types.CallbackQuery):
    prices = [types.LabeledPrice(label=album["title"], amount=album["price"])]
    await bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title=album["title"],
        description=album["description"],
        provider_token=PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="buy-album",
        payload=album["title"],
        photo_url="https://i.postimg.cc/FHwdwCzK/KUPIT-DOSTUP.png",
        photo_width=600,
        photo_height=600,
        photo_size=600
    )

# Подтверждение оплаты
@dp.pre_checkout_query_handler(lambda q: True)
async def process_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# После успешной оплаты
@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(msg: types.Message):
    await msg.answer(
        f"Спасибо за поддержку! ❤️\n\n"
        f"Вот твоя ссылка для доступа к музыке: {album['download_link']}\n"
        f"Пароль: СИМФОРОК\n"
        f"Приятного прослушивания! 🎧"
    )

# === Запуск ===
if __name__ == "__main__":
    keep_alive()  # держим Flask сервер живым
    executor.start_polling(dp, skip_updates=True)

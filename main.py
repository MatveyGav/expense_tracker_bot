import logging
from io import BytesIO
import requests
from tokens import BOT_TOKEN, CHECK_TOKEN

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import text
from aiogram.enums import ParseMode

import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image

# Токен бота (замените на свой)
url = 'https://proverkacheka.com/api/v1/check/get'


# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для распознавания QR-кодов.\n"
        "Отправь мне изображение с QR-кодом или используй команду /qr."
    )

# Команда /qr
@dp.message(Command("qr"))
async def cmd_qr(message: types.Message):
    await message.answer("📷 Отправь мне изображение с QR-кодом, и я попробую его распознать!")

# Обработка изображений
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    # Скачиваем изображение
    photo = message.photo[-1]  # Берем самое большое изображение
    file = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(file.file_path)

    # Преобразуем в формат для OpenCV
    pil_image = Image.open(BytesIO(photo_bytes.read()))
    cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Пытаемся распознать QR-код
    decoded_objects = decode(cv_image)

    if decoded_objects:
        results = []
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            request_data = {'token': CHECK_TOKEN,
                            'qrraw': data}
            r = requests.post(url, data=request_data)
        await message.answer(r.text)
    else:
        await message.answer("❌ QR-код не найден. Попробуй отправить более четкое изображение.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
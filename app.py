import asyncio
import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import FileIsTooBig
from config import API_TOKEN, RAPIDAPI_TOKEN
from aiogram import executor

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    await message.answer("<i>Assalomu alaykum bu bot bilan siz pdf fayllaringizni jamini qisqartirishingiz mumkin!!!</i>\n<b>Maksimal yuboriladigan fayl hajmi 50MB dan oshmasin</b>")

@dp.message_handler(content_types=types.ContentTypes.DOCUMENT)
async def handle_pdf(message: types.Message):
    if message.document.mime_type == 'application/pdf':
        folder_name = 'Received'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        file_name = os.path.join(folder_name, message.document.file_name)
        await message.document.download(file_name)

        reply_text = f"<b>Hurmatli, </b><code>{message.from_user.first_name}</code> <b>biz sizning pdf faylingizni qabul qildik!</b>\n<b>Iltimos biroz vaqt kutib turing...</b>"
        reply_message = await bot.send_message(chat_id=message.chat.id, text=reply_text)

        await asyncio.sleep(5)
        await reply_message.delete()
        
        sticker_file = open('AnimatedSticker.tgs', 'rb')
        await bot.send_sticker(chat_id=message.chat.id, sticker=sticker_file)
        sticker_file.close()

        file_path = file_name

        try:
            url = "https://pdf4me.p.rapidapi.com/RapidApi/OptimizePdf"
            files = {"File": open(file_path, 'rb')}
            headers = {
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "*/*",
                "X-RapidAPI-Key": RAPIDAPI_TOKEN,
                "X-RapidAPI-Host": "pdf4me.p.rapidapi.com"
            }

            response = requests.post(url, files=files, headers=headers)

            if response.status_code == 200:
                optimized_file_path = os.path.join(folder_name, "optimized_" + message.document.file_name)
                with open(optimized_file_path, 'wb') as optimized_file:
                    optimized_file.write(response.content)
                await bot.send_message(chat_id=message.chat.id, text=f"<b>Sizning tayyor faylingiz:</b>👇👇👇")
                await bot.send_document(chat_id=message.chat.id, document=open(optimized_file_path, 'rb'))

                

                os.remove(optimized_file_path)
            else:
                await bot.send_message(chat_id=message.chat.id, text="<b>PDF faylni hajmini qisqartirishda muammo paydo bo'ldi.</b>\n<b>Iltimos qaytadan urunib ko'ring</b>")
        except FileIsTooBig:
            await bot.send_message(chat_id=message.chat.id, text="<b>The uploaded PDF file is too big. Please upload a smaller file.</b>")
        
        os.remove(file_path)

    else:
        error_message = "<u>Iltimos faqatgina PDF fayl yuboring!!!</u>"
        await bot.send_message(chat_id=message.chat.id, text=error_message)

if __name__ == '__main__':
    executor.start_polling(dp)

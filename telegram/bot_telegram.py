from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from db_access import EmployeeAccess
from settings import TOKEN_Telegram


bot = Bot(token=TOKEN_Telegram)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    print(message.get_args())
    slug = message.get_args()

    print(message.from_user.id)
    telegram_chat_id = message.from_user.id
    registration = EmployeeAccess(
        slug=slug, telegram_chat_id=telegram_chat_id).add_telegram_chat_id()
    if registration:
        await message.reply("Hello!\nSuccess")
    else:
        await message.reply("Hello!\nNow you can receive messages from me")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    print(message.get_args())
    await message.reply('Напиши мне что-нибудь, и я отпрпавлю этот текст тебе '
                        'в ответ!')


@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp)

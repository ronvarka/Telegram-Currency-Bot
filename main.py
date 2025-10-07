import logging
from config import Config
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
import asyncio

from handlers.base_commands import BaseCommands
from handlers.currency_command import CurrencyCommand
from services.currency_service import CurrencyService

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()

    currency_service = CurrencyService(api_url=Config.EXCHANGE_RATE_API, cache_ttl=Config.CACHE_TTL)
    currency_handler = CurrencyCommand(currency_service)
    base_commands = BaseCommands()

    dp.message.register(base_commands.cmd_start, Command("start"))
    dp.message.register(base_commands.cmd_help, Command("help"))

    dp.message.register(currency_handler.start_handler, Command("currency"))
    dp.message.register(currency_handler.convert, Command("convert"))

    dp.callback_query.register(currency_handler.cmd_more, F.data == "cmd_more")
    dp.callback_query.register(currency_handler.cmd_back, F.data == "cmd_back")
    dp.callback_query.register(currency_handler.cmd_go, F.data == "cmd_go")
    dp.callback_query.register(
        currency_handler.cmd_return, F.data == "cmd_return"
    )

    dp.callback_query.register(
        currency_handler.cmd_currency,
        F.data.startswith("cmd_") & ~F.data.in_({"cmd_more", "cmd_back"}),
    )

    dp.message.register(base_commands.unknown_command)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

from aiogram import types


class BaseCommands:
    @staticmethod
    async def cmd_start(message: types.Message):
        start_text = """
    🤖 <b>Добро пожаловать в бот курсов валют!</b>

    Я помогу тебе:
    💱 Узнать актуальные курсы валют
    🔄 Конвертировать любую сумму
    📊 Следить за изменениями курсов

    Для начала работы используй:
    /currency - посмотреть курсы валют
    /help - подробная инструкция

    <b>Данные предоставлены ЦБ РФ</b>
    """
        await message.answer(start_text, parse_mode="HTML")

    @staticmethod
    async def cmd_help(message: types.Message):
        """Обработчик команды /help"""
        help_text = """
    🤖 <b>Бот курсов валют ЦБ РФ</b>

    <b>Доступные команды:</b>

    /start - Начать работу с ботом
    /help - Показать это сообщение

    💱 <b>Основные команды:</b>
    /currency - Показать курсы валют
    /convert [валюта] [сумма] - Конвертировать валюту

    📊 <b>Примеры использования:</b>
    /convert USD 100 - Конвертировать 100 долларов
    /convert EUR 50.5 - Конвертировать 50.5 евро

    <b>Как пользоваться:</b>
    1. Нажми /currency чтобы увидеть список валют
    2. Выбери валюту из списка
    3. Используй кнопки для навигации
    4. Для конвертации используй /convert

    📈 <b>Особенности:</b>
    • Данные обновляются каждый час
    • Показывается изменение курса
    • Поддержка 30+ валют
    • Конвертация с учетом номинала
    """
        await message.answer(help_text, parse_mode="HTML")

    @staticmethod
    async def unknown_command(message: types.Message):
        await message.answer(
            "❌ Неизвестная команда.\n"
            "Используй /help для просмотра доступных команд."
            )

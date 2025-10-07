import math

from aiogram import types
from services.currency_service import CurrencyService
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from config import Config


class CurrencyCommand:
    def __init__(self, currency_service: CurrencyService):
        self.currency_service = currency_service
        self.popular = [
            "USD - Доллар США",
            "EUR - Евро",
            "CNY - Юань",
            "GBP - Фунт стерлингов",
            "JPY - Иен",
            "CHF - Швейцарский франк",
        ]
        self.currencies = []
        self.current_page = 1
        self.ITEMS_PER_PAGE = Config.ITEMS_PER_PAGE
        self.max_page = 0

    def get_popular_keyboard(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=currency, callback_data=f"cmd_{currency[:3]}"
                    )
                ]
                for currency in self.popular
            ]
            + [
                [
                    InlineKeyboardButton(
                        text="Показать еще", callback_data="cmd_more"
                    )
                ]
            ]
        )

    def get_all_keyboard(self):
        if not self.currencies:
            self.currencies = self.currency_service.get_available_currencies()
            self.extra = [c for c in self.currencies if c not in self.popular]
        if not self.max_page:
            self.max_page = math.ceil(len(self.extra) / self.ITEMS_PER_PAGE)
        page_info = f"{self.current_page}/{self.max_page}"

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=currency, callback_data=f"cmd_{currency[:3]}"
                    )
                ]
                for currency in self.extra[
                    (self.current_page - 1) * self.ITEMS_PER_PAGE:
                    self.current_page * self.ITEMS_PER_PAGE
                ]
            ]
            + [
                [InlineKeyboardButton(text="<-", callback_data="cmd_return")]
                + [
                    InlineKeyboardButton(
                        text=f"Назад {page_info}", callback_data="cmd_back"
                    )
                ]
                + [InlineKeyboardButton(text="->", callback_data="cmd_go")]
            ]
        )

    async def start_handler(self, message: types.Message):
        await message.answer(
            "Выберите валюту:", reply_markup=self.get_popular_keyboard()
        )

    async def cmd_go(self, callback: types.CallbackQuery):
        if self.current_page < self.max_page:
            self.current_page += 1
            await self._update_message(callback)

    async def cmd_return(self, callback: types.CallbackQuery):
        if self.current_page > 1:
            self.current_page -= 1
            await self._update_message(callback)

    async def cmd_more(self, callback: types.CallbackQuery):
        await self._update_message(callback)

    async def cmd_back(self, callback: types.CallbackQuery):
        await callback.message.edit_text(
            "Популярные валюты:", reply_markup=self.get_popular_keyboard()
        )
        await callback.answer()

    async def _update_message(self, callback: types.CallbackQuery):
        await callback.message.edit_text(
            "Все доступные валюты:", reply_markup=self.get_all_keyboard()
        )
        await callback.answer()

    async def cmd_currency(self, callback: types.CallbackQuery):
        code = callback.data.split("_")[1]
        rate = self.currency_service.get_rate(code)

        await callback.message.edit_text(
            text=rate, reply_markup=callback.message.reply_markup
        )
        await callback.answer()

    async def convert(self, message: types.Message):
        data = message.text.split()
        if len(data) != 3:
            info = "Неверно введена команда. Пример: /convert usd 100."
        else:
            convert_currency = data[1].upper()
            convert_nominal = data[2]
            info = self.currency_service.convert(
                convert_currency, convert_nominal
            )

        await message.answer(text=info)

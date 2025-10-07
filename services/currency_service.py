from datetime import timedelta, datetime

import requests
from lxml import etree


class CurrencyService:
    def __init__(self, api_url: str, cache_ttl: int):
        self.api_url = api_url
        self.cache_ttl = timedelta(seconds=cache_ttl)
        self._cache = {
            'data': None,
            'last_updated': None,
            'previous_rates': None
        }

    def _is_cache_valid(self) -> bool:
        return (self._cache['data'] is not None and
                (datetime.now() - self._cache["last_updated"]) < self.cache_ttl
                )

    def _ensure_data_available(self) -> bool:
        if not self._is_cache_valid():
            try:
                self._fetch_rate()
                return True
            except Exception as e:
                print(f'❌ Ошибка при обновлении данных: {e}')
                if self._cache['data'] is None:
                    return False
        return True

    def _parse_currency(self, currency_code):
        try:
            currency = self._cache['data'].xpath(
                f"//Valute[CharCode='{currency_code}']")[0]
        except IndexError:
            raise ValueError(f"❌ Валюта '{currency_code}' не найдена\n\n"
                             f"Попробуйте выбрать из списка доступных валют")

        name = currency.xpath("Name/text()")[0]
        value = float(currency.xpath("Value/text()")[0].replace(',', '.'))
        nominal = currency.xpath('Nominal/text()')[0]
        return name, value, nominal

    def _fetch_rate(self):
        try:
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()

            if not response.content.strip():
                raise ValueError("📭 API вернул пустой ответ")

            try:
                root = etree.fromstring(response.content)
            except etree.XMLSyntaxError as e:
                raise ValueError("📄 Некорректный XML от сервера") from e

            if not root.xpath('//Valute/CharCode'):
                raise ValueError('📊 Ответ не содержит данных о валютах')

            self._cache = {
                'data': root,
                'last_updated': datetime.now(),
                'previous_rates': {}
            }

        except requests.RequestException as e:
            raise RuntimeError(f"🌐 Ошибка при запросе к API: {e}")

    def get_available_currencies(self) -> list:
        if not self._ensure_data_available():
            return []
        currencies = self._cache['data'].xpath('//Valute/CharCode/text()')
        currencies_name = self._cache['data'].xpath('//Valute/Name/text()')
        return [f"{currency} - {currency_name}" for currency,
                currency_name in zip(currencies, currencies_name)]

    def get_rate(self, currency_code) -> str:
        if not self._ensure_data_available():
            return "❌ Не удалось получить актуальный курс\n\n" \
                "Попробуйте позже или проверьте соединение"

        name, value, nominal = self._parse_currency(currency_code)

        if currency_code in self._cache['previous_rates']:
            difference = value - self._cache['previous_rates'][currency_code]
        else:
            difference = 0
        self._cache['previous_rates'][currency_code] = value

        cache_warning = (
            f'⚠️ Данные могут быть устаревшими\nОбновлено: '
            f'{self._cache['last_updated'].strftime('%d.%m.%Y в %H:%M')}\n\n'
            if (datetime.now() - self._cache['last_updated']) > self.cache_ttl
            else "")

        change_emoji = ("📈" if difference > 0 else "📉"
                        if difference < 0 else "➡️")
        change_info = (f'\n{change_emoji} Изменение: {difference:+.4f}'
                       if difference else '')

        return (
            f"{cache_warning}💱 {currency_code.upper()}\n"
            f"• {nominal} {name}\n"
            f"• 💰 Курс: {value:.2f} RUB"
            f"{change_info}"
        )

    def convert(self, currency_code, amount):
        try:
            amount = float(amount.replace(",", "."))
            if amount < 0:
                return "❌ Сумма должна быть положительным числом\n\n" \
                    "Пример: 100 или 50.5"
        except ValueError:
            return "❌ Неправильный формат суммы\n\n💡 " \
                "Пример правильной команды:\n/convert USD 100.5"

        if currency_code.isdigit():
            return "❌ Неправильный формат валюты\n\n💡" \
                "Пример правильной команды:\n/convert USD 100.5"

        if not self._ensure_data_available():
            return "❌ Не удалось произвести конвертацию\n\n" \
                "Попробуйте позже или проверьте соединение"

        try:
            name, value, nominal = self._parse_currency(currency_code)
        except ValueError as e:
            return str(e)

        converted_value = value / float(nominal) * amount
        return (
            f"💱 Конвертация {currency_code.upper()}\n\n"
            f"• 💰 {amount} {name}\n"
            f"• 🔄 = {converted_value:.2f} RUB\n"
        )

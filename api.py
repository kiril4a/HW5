import aiohttp
import asyncio

class PrivatBankAPIClient:
    def __init__(self):
        self.base_url = 'https://api.privatbank.ua/p24api/exchange_rates'
        self.session = aiohttp.ClientSession()

    async def get_exchange_rates(self, date):
        async with self.session.get(f'{self.base_url}?json&date={date}') as response:
            return await response.json()

    async def close_session(self):
        if not self.session.closed:
            await self.session.close()
class ExchangeRateProcessor:
    @staticmethod
    def filter_exchange_rates(exchange_rates, currencies, limit):
        filtered_rates = []
        for rate in exchange_rates:
            if rate['currency'] in currencies:
                filtered_rates.append(rate)
            if len(filtered_rates) >= limit:
                break
        return filtered_rates

    @staticmethod
    def format_exchange_rates(date, exchange_rates):
        formatted_rates = {date: {}}
        for rate in exchange_rates:
            formatted_rates[date][rate['currency']] = {
                'sale': rate.get('saleRate'),
                'purchase': rate.get('purchaseRate')
            }
        return formatted_rates
import argparse
import datetime
import asyncio
import json

async def main():
    parser = argparse.ArgumentParser(description='Get exchange rates from PrivatBank API')
    parser.add_argument('limit', type=int, help='Number of days to retrieve exchange rates for')
    args = parser.parse_args()

    today = datetime.date.today()
    api_client = PrivatBankAPIClient()

    exchange_rates = []
    for i in range(args.limit):
        date = today - datetime.timedelta(days=i)
        formatted_date = date.strftime('%d.%m.%Y')
        response = await api_client.get_exchange_rates(formatted_date)
        rates = ExchangeRateProcessor.filter_exchange_rates(response['exchangeRate'], ['USD', 'EUR'], 2)
        formatted_rates = ExchangeRateProcessor.format_exchange_rates(formatted_date, rates)
        exchange_rates.append(formatted_rates)

    await api_client.close_session()

    print(json.dumps(exchange_rates, indent=2))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

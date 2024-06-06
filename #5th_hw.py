#5th_hw.py
#Крок 1: Встановлення залежностей

pip install aiohttp asyncio

#Крок 2: Створення утиліти

import sys
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any

class CurrencyRateFetcher:
    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

    def __init__(self, days: int):
        self.days = days
        self.dates = [datetime.now() - timedelta(days=i) for i in range(1, days + 1)]
        self.dates_str = [date.strftime('%d.%m.%Y') for date in self.dates]

    async def fetch_rate(self, session: aiohttp.ClientSession, date: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{date}"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return self.parse_response(date, data)
            else:
                print(f"Failed to fetch data for {date}: HTTP {response.status}")
                return {}

    def parse_response(self, date: str, data: Dict[str, Any]) -> Dict[str, Any]:
        rates = {rate['currency']: rate for rate in data['exchangeRate']}
        return {
            date: {
                'EUR': {
                    'sale': rates['EUR']['saleRateNB'],
                    'purchase': rates['EUR']['purchaseRateNB']
                },
                'USD': {
                    'sale': rates['USD']['saleRateNB'],
                    'purchase': rates['USD']['purchaseRateNB']
                }
            }
        }

    async def fetch_all_rates(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_rate(session, date) for date in self.dates_str]
            return await asyncio.gather(*tasks)

def main(days: int):
    if not 1 <= days <= 10:
        print("Please enter a number of days between 1 and 10.")
        return

    fetcher = CurrencyRateFetcher(days)
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(fetcher.fetch_all_rates())
    print(results)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <number_of_days>")
        sys.exit(1)

    try:
        days = int(sys.argv[1])
    except ValueError:
        print("Please enter a valid number.")
        sys.exit(1)

    main(days)
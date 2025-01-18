import os
import json
import requests
import xml.etree.ElementTree as ET
import time
import aiohttp
import asyncio

async def get_binance_rate(session, currency):
    currency += 'USDT'
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={currency.upper()}'
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # Raises an exception for HTTP errors
            data = await response.json()
            print(data)
            print(f'get_binance_rate for {currency}')
            rate = float(data['price'])
            if rate == 118.7:
                return None
            return rate
    except aiohttp.ClientError as e:
        logging.error(f"Binance: Error: {e}")
        return None


async def get_bitfinex_rate(session, currency):
    # Определение правильного формата торговой пары
    if currency.lower() == 'matic':
        currency_pair = 'tMATIC:USD'
    elif currency.lower() == 'doge':
        currency_pair = 'tDOGE:USD'
    elif currency.lower() == 'avax':
        currency_pair = 'tAVAX:USD'
    elif currency.lower() == 'shib':
        currency_pair = 'tSHIB:USD'
    elif currency.lower() == 'bnb':
        return None
    elif currency.lower() == 'bch':
        return None
    elif currency.lower() == 'dash':
        return None
    else:
        currency_pair = f't{currency.upper()}USD'

    # Формирование URL на основе переданной валюты и USD
    url = f'https://api-pub.bitfinex.com/v2/ticker/{currency_pair}'
    
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # Raises an exception for HTTP errors
            data = await response.json()  # Преобразование ответа в JSON формат
            print(f'get_bitfinex_rate for {currency}')
            last_price = float(data[6])  # Последняя цена сделки, преобразованная в float
            return last_price
    except aiohttp.ClientError as e:
        logging.error(f"Bitfinex: Error: {e}")
        return None


async def get_cryptomus_rate(session, currency):
    url = "https://api.cryptomus.com/v1/exchange-rate/rates.xml"
    to_currency = 'USDTPOLYGON'
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # Проверяем наличие ошибок при запросе

            # Получаем текст XML из ответа
            xml_data = await response.text()

            try:
                # Парсим XML
                root = ET.fromstring(xml_data)

                # Итерируемся по элементам <item> и ищем соответствие from_currency и to_currency
                for item in root.findall('item'):
                    item_from = item.find('from').text
                    item_to = item.find('to').text
                    item_out = item.find('out').text
                    if item_from == currency.upper() and item_to == to_currency:
                        print(f'get_cryptomus_rate for {currency}')
                        return float(item_out)

                # Если не нашли соответствия
                return None

            except ET.ParseError as e:
                print(f"cryptomus: Error parsing XML: {e}")
                return None

    except aiohttp.ClientError as e:
        print(f"Cryptomus: Error: {e}")
        return None


async def get_coinbase_rate(session, currency):
    print(f'get_coinbase_rate for {currency}')
    # Прямое указание USD в URL
    if currency.upper() == 'TON':
        return None
    coin_name = currency.lower()
    url = f'https://api.coinbase.com/v2/prices/{coin_name}-usd/spot'

    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()

            if 'data' in data and 'amount' in data['data']:
                last_trade_price = float(data['data']['amount'])
                return last_trade_price
            else:
                print(f"coinbase: Не удалось найти цену для монеты {currency.upper()} на Coinbase")
                return None
    except aiohttp.ClientError as e:
        print(f"coinbase: Ошибка при выполнении запроса для монеты {currency.upper()}: {e}")
        return None
    


async def get_kraken_rate(session, currency):
    print(f'get_kraken_rate {currency}')
    # Формирование URL на основе переданной валюты и USD
    url = f'https://api.kraken.com/0/public/Ticker?pair={currency.upper()}USD'
    if currency.lower() == 'bnb':
        return None
    try:
        async with session.get(url) as response:
            data = await response.json()  # Преобразование ответа в JSON формат
            
            # Проверка наличия ключа 'result' в ответе
            if 'result' not in data:
                print(f"kraken: Ответ не содержит ключ 'result': {data}")
                return None
            # Поиск ключа, содержащего данные для указанной валютной пары
            found_key = None

            for key, value in data['result'].items():
                # Проверяем, содержит ли текущий ключ данные для указанной валютной пары
                if 'c' in value and isinstance(value['c'], list) and len(value['c']) > 0:
                    found_key = key
                    break

            # Проверяем, был ли найден ключ с указанной валютной парой
            if found_key:
                last_trade_price = float(
                    data['result'][found_key]['c'][0])  # Последняя цена сделки, преобразованная в float
                return last_trade_price
            else:
                print(f"kraken: Не удалось найти данные для {currency.upper()}/USD в ответе")
                return None
    except aiohttp.ClientError as e:
        print(f"kraken: Ошибка при выполнении запроса для монеты {currency.upper()}: {e}")
        return None


async def get_world_rate(session, base_currency):
    print(f'get_world_rate for {base_currency}')
    target_currency = 'usd'

    # Заменяем вызов на Kaiko API
    url = f'https://eu.market-api.kaiko.io/v2/data/trades.v1/spot_exchange_rate/{base_currency.lower()}-{target_currency}'

    try:
        async with session.get(url) as response:
            response.raise_for_status()  # Вызывает исключение, если статус ответа не 200

            data = await response.json()
            if 'data' in data and data['data']:
                # Получаем последнюю цену
                last_trade = data['data'][0]  # Предполагаем, что первый элемент — это последняя сделка
                return float(last_trade['price'])
            else:
                print(f"Error: Unable to find exchange rate for {base_currency} to {target_currency}")
                return None

    except aiohttp.ClientError as e:
        print(f"world: Ошибка при выполнении запроса для монеты {base_currency.upper()}: {e}")
        return None


async def exchange_rate():
    async with aiohttp.ClientSession() as session:
      # Функция для загрузки данных из JSON
      def load_data():
          filename = os.path.join('source', 'users.json')
          try:
              with open(filename, 'r') as file:
                  data = json.load(file)
          except FileNotFoundError:
              data = {}
          except json.JSONDecodeError:
              data = {}
          return data
  
      coin_array = ['XMR', 'SHIB', 'BTC', 'TRX', 'BCH', 'AVAX', 'ETH', 'DOGE', 'DASH', 'LTC', 'DAI', 'SOL', 'BNB',
                    'MATIC']
  
      binance_rate = {}
      bitfinex_rate = {}
      cryptomus_rate = {}
      coinbase_rate = {}
      kraken_rate = {}
      world_rate = {}
  
      def format_rate(rate):
          if rate is None:
              return 'None'
          try:
              return float(f'{float(rate):.8f}')
          except ValueError:
              return 'Invalid rate'
  
      #for coin in coin_array:
          #print(f'Запрос: {coin}')
          #binance_rate[coin] = format_rate(await get_binance_rate(session, coin))
          #bitfinex_rate[coin] = format_rate(await get_bitfinex_rate(session, coin))
          #cryptomus_rate[coin] = format_rate(await get_cryptomus_rate(session, coin))
          #coinbase_rate[coin] = format_rate(await get_coinbase_rate(session, coin))
          #kraken_rate[coin] = format_rate(await get_kraken_rate(session, coin))
          #world_rate[coin] = format_rate(await get_world_rate(session, coin))
      
      async def get_all_rates(session, coin):
          print(f'Запрос: {coin}')
          results = await asyncio.gather(
          get_binance_rate(session, coin),
          get_bitfinex_rate(session, coin),
          get_cryptomus_rate(session, coin),
          get_coinbase_rate(session, coin),
          get_kraken_rate(session, coin),
          get_world_rate(session, coin)
      )

          return {
              'binance': format_rate(results[0]),
              'bitfinex': format_rate(results[1]),
              'cryptomus': format_rate(results[2]),
              'coinbase': format_rate(results[3]),
              'kraken': format_rate(results[4]),
              'world': format_rate(results[5])
          }
      
      
      all_rates = await asyncio.gather(*(get_all_rates(session, coin) for coin in coin_array))

      # Распаковка результатов
      for i, coin in enumerate(coin_array):
          binance_rate[coin] = all_rates[i]['binance']
          bitfinex_rate[coin] = all_rates[i]['bitfinex']
          cryptomus_rate[coin] = all_rates[i]['cryptomus']
          coinbase_rate[coin] = all_rates[i]['coinbase']
          kraken_rate[coin] = all_rates[i]['kraken']
          world_rate[coin] = all_rates[i]['world']
      
          
  
      def calc_diff_and_percentage(base_rate, compare_rate):
          if isinstance(compare_rate, float):
              if type(base_rate) == str or type(compare_rate) == str:
                  return None, None
              else:
                  difference = compare_rate - base_rate
                  percentage_difference = (difference / base_rate) * 100
                  return round(compare_rate, 8), round(percentage_difference, 4)
          else:
              return None, None
  
      def calc_data_notification(coin, exchange, binance_rate, bitfinex_rate, cryptomus_rate, coinbase_rate, kraken_rate,
                                 world_rate):
          print(f'Начало подсчета: {coin}')
          if exchange == 'Binance' and binance_rate is not None:
              cryptomus_data = calc_diff_and_percentage(binance_rate[coin], cryptomus_rate[coin])
              bitfinex_data = calc_diff_and_percentage(binance_rate[coin], bitfinex_rate[coin])
              coinbase_data = calc_diff_and_percentage(binance_rate[coin], coinbase_rate[coin])
              kraken_data = calc_diff_and_percentage(binance_rate[coin], kraken_rate[coin])
              world_data = calc_diff_and_percentage(binance_rate[coin], world_rate[coin])
              print(binance_rate[coin],
                    cryptomus_data[0], cryptomus_data[1],
                    bitfinex_data[0], bitfinex_data[1],
                    coinbase_data[0], coinbase_data[1],
                    kraken_data[0], kraken_data[1],
                    world_data[0], world_data[1])
              return (binance_rate[coin],
                      cryptomus_data[0], cryptomus_data[1],
                      bitfinex_data[0], bitfinex_data[1],
                      coinbase_data[0], coinbase_data[1],
                      kraken_data[0], kraken_data[1],
                      world_data[0], world_data[1]
                      )
          elif exchange == 'Cryptomus' and cryptomus_rate is not None:
              binance_data = calc_diff_and_percentage(cryptomus_rate[coin], binance_rate[coin])
              bitfinex_data = calc_diff_and_percentage(cryptomus_rate[coin], bitfinex_rate[coin])
              coinbase_data = calc_diff_and_percentage(cryptomus_rate[coin], coinbase_rate[coin])
              kraken_data = calc_diff_and_percentage(cryptomus_rate[coin], kraken_rate[coin])
              world_data = calc_diff_and_percentage(cryptomus_rate[coin], world_rate[coin])
              return (cryptomus_rate[coin],
                      binance_data[0], binance_data[1],
                      bitfinex_data[0], bitfinex_data[1],
                      coinbase_data[0], coinbase_data[1],
                      kraken_data[0], kraken_data[1],
                      world_data[0], world_data[1]
                      )
          elif exchange == 'Bitfinex' and bitfinex_rate is not None:
              binance_data = calc_diff_and_percentage(bitfinex_rate[coin], binance_rate[coin])
              cryptomus_data = calc_diff_and_percentage(bitfinex_rate[coin], cryptomus_rate[coin])
              coinbase_data = calc_diff_and_percentage(bitfinex_rate[coin], coinbase_rate[coin])
              kraken_data = calc_diff_and_percentage(bitfinex_rate[coin], kraken_rate[coin])
              world_data = calc_diff_and_percentage(bitfinex_rate[coin], world_rate[coin])
              return (bitfinex_rate[coin],
                      binance_data[0], binance_data[1],
                      cryptomus_data[0], cryptomus_data[1],
                      coinbase_data[0], coinbase_data[1],
                      kraken_data[0], kraken_data[1],
                      world_data[0], world_data[1]
                      )
          elif exchange == 'Coinbase' and coinbase_rate is not None:
              binance_data = calc_diff_and_percentage(coinbase_rate[coin], binance_rate[coin])
              cryptomus_data = calc_diff_and_percentage(coinbase_rate[coin], cryptomus_rate[coin])
              bitfinex_data = calc_diff_and_percentage(coinbase_rate[coin], bitfinex_rate[coin])
              kraken_data = calc_diff_and_percentage(coinbase_rate[coin], kraken_rate[coin])
              world_data = calc_diff_and_percentage(coinbase_rate[coin], world_rate[coin])
              return (coinbase_rate[coin],
                      binance_data[0], binance_data[1],
                      cryptomus_data[0], cryptomus_data[1],
                      bitfinex_data[0], bitfinex_data[1],
                      kraken_data[0], kraken_data[1],
                      world_data[0], world_data[1]
                      )
          elif exchange == 'Kraken' and kraken_rate is not None:
              binance_data = calc_diff_and_percentage(kraken_rate[coin], binance_rate[coin])
              cryptomus_data = calc_diff_and_percentage(kraken_rate[coin], cryptomus_rate[coin])
              bitfinex_data = calc_diff_and_percentage(kraken_rate[coin], bitfinex_rate[coin])
              coinbase_data = calc_diff_and_percentage(kraken_rate[coin], coinbase_rate[coin])
              world_data = calc_diff_and_percentage(kraken_rate[coin], world_rate[coin])
              return (kraken_rate[coin],
                      binance_data[0], binance_data[1],
                      cryptomus_data[0], cryptomus_data[1],
                      bitfinex_data[0], bitfinex_data[1],
                      coinbase_data[0], coinbase_data[1],
                      world_data[0], world_data[1]
                      )

    def check_differences_and_notify():
        data = load_data()
        results = []

        for entry_id, entry_data in data.items():
            chat_id = entry_data.get('chat_id')
            exchange = entry_data.get('exchange')
            coin = entry_data.get('coin')
            diff_str = entry_data.get('diff')

            try:
                diff = float(diff_str)
            except (TypeError, ValueError):
                print(f"Invalid diff value for entry_id {entry_id}: {diff_str}")
                continue

            values = calc_data_notification(coin, exchange, binance_rate, bitfinex_rate, cryptomus_rate, coinbase_rate,
                                            kraken_rate, world_rate)

            (exchange_value, value1, percentage1, value2, percentage2, value3, percentage3, value4, percentage4, value5,
             percentage5) = values

            # Проверяем разницу по модулю для каждого percentage_difference
            if (
                    (percentage1 is not None and abs(percentage1) >= diff) or
                    (percentage2 is not None and abs(percentage2) >= diff) or
                    (percentage3 is not None and abs(percentage3) >= diff) or
                    (percentage4 is not None and abs(percentage4) >= diff) or
                    (percentage5 is not None and abs(percentage5) >= diff)
            ):
                print('Найдена нужная разница')
                results.append((
                    chat_id, exchange, coin, exchange_value, value1, percentage1,
                    value2, percentage2, value3, percentage3, value4, percentage4, value5, percentage5
                ))
            else:
                print(
                    f'Разница в {diff}% не достигла, текущее значение {percentage1, percentage2, percentage3, percentage4, percentage5}, монета {coin}')
            print(results)
        return results

    respons_rate = check_differences_and_notify()
    return respons_rate
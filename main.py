import os
import logging
import json
import asyncio
import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, RetryAfter
from exchang_rate import exchange_rate

API_TOKEN = ''

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# List of exchanges
exchanges = ['Binance', 'Bitfinex', 'Cryptomus', 'Coinbase', 'Kraken']

# List of coins
coins = ['XMR', 'SHIB', 'BTC', 'TRX', 'BCH', 'AVAX', 'ETH', 'DOGE', 'DASH', 'LTC', 'DAI', 'SOL', 'BNB', 'MATIC']
last_exchange_results = None
last_update_time = 0

# Keyboard for selecting rate difference
diff_kb = InlineKeyboardMarkup()
diff_kb.row(
    InlineKeyboardButton('0.1 %', callback_data='diff_0.1'),
    InlineKeyboardButton('0.5 %', callback_data='diff_0.5'),
    InlineKeyboardButton('1 %', callback_data='diff_1'),
    InlineKeyboardButton('2 %', callback_data='diff_2'),
    InlineKeyboardButton('5 %', callback_data='diff_5')
)

# Temporary dictionary to store user data
temp_user_data = {}


# Function to load data from JSON
def load_data():
    filename = os.path.join('source', 'users.json')
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data


# Function to save data to JSON
def save_data(data):
    filename = os.path.join('source', 'users.json')
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


# Function to delete user data by chat_id
def delete_user_data(chat_id):
    data = load_data()
    # Remove the entries with the specified chat_id
    data = {key: value for key, value in data.items() if value['chat_id'] != chat_id}

    # Rebuild the dictionary with sequential keys
    new_data = {str(index + 1): value for index, (key, value) in enumerate(data.items())}

    save_data(new_data)


async def update_exchange_rates():
    global last_exchange_results, last_update_time

    while True:
        current_time = time.time()

        if current_time - last_update_time >= 60:
            last_exchange_results = await exchange_rate()
            last_update_time = current_time
            logging.info("Exchange rates updated.")
        else:
            logging.info("Using cached exchange rates.")

        await asyncio.sleep(60)


# Asynchronous function to send messages every 60 seconds
# (chat_id, exchange, coin, exchange_value, value1, percentage1, value2, percentage2, value3, percentage3,
#                            value4, percentage4, value5, percentage5)

async def periodic_message_sender():
    while True:
        if last_exchange_results:
            for result in last_exchange_results:
                chat_id = result[0]
                user_data = load_data()
                if not any(user["chat_id"] == chat_id for user in user_data.values()):
                    logging.info(f"No data found for chat_id {chat_id}, skipping.")
                    continue
                exchange_select = result[1]
                coin_name = result[2]

                if exchange_select == 'Binance':
                    print('binance')
                    print('work')
                    binance_exchange_rate = result[3]
                    if result[4] is None:
                        cryptomus_information = 'Failed to retrieve data'
                    else:
                        cryptomus_information = f' {result[4]} / {result[5]}%'

                    if result[6] is None:
                        bitfinex_information = 'Failed to retrieve data'
                    else:
                        bitfinex_information = f' {result[6]} / {result[7]}%'

                    if result[8] is None:
                        coinbase_information = 'Failed to retrieve data'
                    else:
                        coinbase_information = f' {result[8]} / {result[9]}%'

                    if result[10] is None:
                        kraken_information = 'Failed to retrieve data'
                    else:
                        kraken_information = f' {result[10]} / {result[11]}%'

                    if result[12] is None:
                        world_information = 'Failed to retrieve data'
                    else:
                        world_information = f' {result[12]} / {result[13]}%'

                    message_text = (f'<b>\U0001F4C8Profitable rate:</b>\n\n'
                                    f'<b>\U0001F4CDCoin:</b> {coin_name}/USDT\n'
                                    f'<b>{exchange_select} rate</b>: {binance_exchange_rate}\n\n'
                                    f'<b><a href="https://app.cryptomus.com/signup?ref=wxL8Pw">Cryptomus</a> rate:</b> {cryptomus_information}\n'
                                    f'<b><a href="https://trading.bitfinex.com/t?type=exchange">Bitfinex</a> rate:</b> {bitfinex_information}\n'
                                    f'<b><a href="https://www.coinbase.com/ru/price/bitcoin">Coinbase</a> rate:</b> {coinbase_information}\n'
                                    f'<b><a href="https://www.kraken.com/">Kraken</a> rate:</b> {kraken_information}\n\n'
                                    # f'<b>рџЊЋWorld rate:</b> {world_information}\n\n'
                                    )

                elif exchange_select == 'Cryptomus':
                    cryptomus_exchange_rate = result[3]

                    if result[4] is None:
                        binance_information = 'Failed to retrieve data'
                    elif coin_name == 'XMR' and result[4] == 118.7:
                        binance_information = 'Failed to retrieve data'
                    else:
                        binance_information = f' {result[4]} / {result[5]}%'

                    if result[6] is None:
                        bitfinex_information = 'Failed to retrieve data'
                    else:
                        bitfinex_information = f' {result[6]} / {result[7]}%'

                    if result[8] is None:
                        coinbase_information = 'Failed to retrieve data'
                    else:
                        coinbase_information = f' {result[8]} / {result[9]}%'

                    if result[10] is None:
                        kraken_information = 'Failed to retrieve data'
                    else:
                        kraken_information = f' {result[10]} / {result[11]}%'

                    if result[12] is None:
                        world_information = 'Failed to retrieve data'
                    else:
                        world_information = f' {result[12]} / {result[13]}%'

                    message_text = (f'<b>\U0001F4C8Profitable rate:</b>\n\n'
                                    f'<b>\U0001F4CDCoin:</b> {coin_name}/USDT\n'
                                    f'<b>{exchange_select} rate</b>: {cryptomus_exchange_rate}\n\n'
                                    f'<b><a href="https://www.binance.com/">Binance</a> rate:</b> {binance_information}\n'
                                    f'<b><a href="https://trading.bitfinex.com/t?type=exchange">Bitfinex</a> rate:</b> {bitfinex_information}\n'
                                    f'<b><a href="https://www.coinbase.com/ru/price/bitcoin">Coinbase</a> rate:</b> {coinbase_information}\n'
                                    f'<b><a href="https://www.kraken.com/">Kraken</a> rate:</b> {kraken_information}\n\n'
                                    # f'<b>рџЊЋWorld rate:</b> {world_information}\n\n'
                                    )

                elif exchange_select == 'Bitfinex':
                    if coin_name == 'BNB' or coin_name == 'DASH':
                        pass
                    else:
                        bitfinex_exchange_rate = result[3]

                        if result[4] is None:
                            binance_information = 'Failed to retrieve data'
                        elif coin_name == 'XMR' and result[4] == 118.7:
                            binance_information = 'Failed to retrieve data'
                        else:
                            binance_information = f' {result[4]} / {result[5]}%'

                        if result[6] is None:
                            cryptomus_information = 'Failed to retrieve data'
                        else:
                            cryptomus_information = f' {result[6]} / {result[7]}%'

                        if result[8] is None:
                            coinbase_information = 'Failed to retrieve data'
                        else:
                            coinbase_information = f' {result[8]} / {result[9]}%'

                        if result[10] is None:
                            kraken_information = 'Failed to retrieve data'
                        else:
                            kraken_information = f' {result[10]} / {result[11]}%'

                        if result[12] is None:
                            world_information = 'Failed to retrieve data'
                        else:
                            world_information = f' {result[12]} / {result[13]}%'

                        message_text = (f'<b>\U0001F4C8Profitable rate:</b>\n\n'
                                        f'<b>\U0001F4CDCoin:</b> {coin_name}/USDT\n'
                                        f'<b>{exchange_select} rate</b>: {bitfinex_exchange_rate}\n\n'
                                        f'<b><a href="https://www.binance.com/">Binance</a> rate:</b> {binance_information}\n'
                                        f'<b><a href="https://app.cryptomus.com/signup?ref=wxL8Pw">Cryptomus</a> rate:</b> {cryptomus_information}\n'
                                        f'<b><a href="https://www.coinbase.com/ru/price/bitcoin">Coinbase</a> rate:</b> {coinbase_information}\n'
                                        f'<b><a href="https://www.kraken.com/">Kraken</a> rate:</b> {kraken_information}\n\n'
                                        # f'<b>рџЊЋWorld rate:</b> {world_information}\n\n'
                                        )

                elif exchange_select == 'Coinbase':
                    coinbase_exchange_rate = result[3]

                    if result[4] is None:
                        binance_information = 'Failed to retrieve data'
                    elif coin_name == 'XMR' and result[4] == 118.7:
                        binance_information = 'Failed to retrieve data'
                    else:
                        binance_information = f' {result[4]} / {result[5]}%'

                    if result[6] is None:
                        cryptomus_information = 'Failed to retrieve data'
                    else:
                        cryptomus_information = f' {result[6]} / {result[7]}%'

                    if result[8] is None:
                        bitfinex_information = 'Failed to retrieve data'
                    else:
                        bitfinex_information = f' {result[8]} / {result[9]}%'

                    if result[10] is None:
                        kraken_information = 'Failed to retrieve data'
                    else:
                        kraken_information = f' {result[10]} / {result[11]}%'

                    if result[12] is None:
                        world_information = 'Failed to retrieve data'
                    else:
                        world_information = f' {result[12]} / {result[13]}%'

                    message_text = (f'<b>\U0001F4C8Profitable rate:</b>\n\n'
                                    f'<b>\U0001F4CDCoin:</b> {coin_name}/USDT\n'
                                    f'<b>{exchange_select} rate</b>: {coinbase_exchange_rate}\n\n'
                                    f'<b><a href="https://www.binance.com/">Binance</a> rate:</b> {binance_information}\n'
                                    f'<b><a href="https://app.cryptomus.com/signup?ref=wxL8Pw">Cryptomus</a> rate:</b> {cryptomus_information}\n'
                                    f'<b><a href="https://trading.bitfinex.com/t?type=exchange">Bitfinex</a> rate:</b> {bitfinex_information}\n'
                                    f'<b><a href="https://www.kraken.com/">Kraken</a> rate:</b> {kraken_information}\n\n'
                                    # f'<b>рџЊЋWorld rate:</b> {world_information}\n\n'
                                    )

                elif exchange_select == 'Kraken':

                    if coin_name == 'BNB' or coin_name == 'TON':
                        pass
                    else:
                        kraken_exchange_rate = result[3]

                        if result[4] is None:
                            binance_information = 'Failed to retrieve data'
                        elif coin_name == 'XMR' and result[4] == 118.7:
                            binance_information = 'Failed to retrieve data'
                        else:
                            binance_information = f' {result[4]} / {result[5]}%'

                        if result[6] is None:
                            cryptomus_information = 'Failed to retrieve data'
                        else:
                            cryptomus_information = f' {result[6]} / {result[7]}%'

                        if result[8] is None:
                            bitfinex_information = 'Failed to retrieve data'
                        else:
                            bitfinex_information = f' {result[8]} / {result[9]}%'

                        if result[10] is None:
                            coinbase_information = 'Failed to retrieve data'
                        else:
                            coinbase_information = f' {result[10]} / {result[11]}%'

                        if result[12] is None:
                            world_information = 'Failed to retrieve data'

                        else:

                            world_information = f' {result[12]} / {result[13]}%'

                        message_text = (f'<b>\U0001F4C8Profitable rate:</b>\n\n'
                                        f'<b>\U0001F4CDCoin:</b> {coin_name}/USDT\n'
                                        f'<b>{exchange_select} rate</b>: {kraken_exchange_rate}\n\n'
                                        f'<b><a href="https://www.binance.com/">Binance</a> rate:</b> {binance_information}\n'
                                        f'<b><a href="https://app.cryptomus.com/signup?ref=wxL8Pw">Cryptomus</a> rate:</b> {cryptomus_information}\n'
                                        f'<b><a href="https://trading.bitfinex.com">Bitfinex</a> rate:</b> {bitfinex_information}\n'
                                        f'<b><a href="https://www.coinbase.com/price">Coinbase</a> rate:</b> {coinbase_information}\n\n'
                                        # f'<b>рџЊЋWorld rate:</b> {world_information}\n\n'
                                        )
                try:
                    await bot.send_message(chat_id=chat_id, text=message_text, parse_mode='HTML',
                                           disable_web_page_preview=True)
                except BotBlocked:
                    logging.error(f"Bot blocked by user with chat_id {chat_id}. Message is not send.")
                except ChatNotFound:
                    logging.error(f"Chat with chat_id {chat_id} not found. Message is not send.")
                except RetryAfter as e:
                    logging.error(f"Error: need to wait {e.timeout} seconds before next atemption.")
                except Exception as e:
                    logging.error(f"UnexpectedError: {e}")
                print(f'Sen push. Chat ID: {chat_id}')
        await asyncio.sleep(90)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    start_kb.row(KeyboardButton('Start tracking rate'), KeyboardButton('Stop tracking'))
    await message.reply("\U0001F977\U0001F3FB\U0001F4A5Hi! I will help you set up notifications to track cryptocurrency rates.",
                        reply_markup=start_kb)


@dp.message_handler(lambda message: message.text == 'Start tracking rate', state='*')
async def start_tracking(message: types.Message):
    exchange_kb = InlineKeyboardMarkup()
    for exchange in exchanges:
        exchange_kb.add(InlineKeyboardButton(exchange, callback_data=f'exchange_{exchange}'))

    await message.reply("\U00002757\U0000FE0FChoose the exchange:", reply_markup=exchange_kb)


@dp.message_handler(lambda message: message.text == 'Stop tracking', state='*')
async def delete_data(message: types.Message):
    chat_id = str(message.chat.id)
    delete_user_data(chat_id)
    await message.reply("\U00002757\U0000FE0FAll your data has been deleted.")


@dp.callback_query_handler(lambda query: query.data.startswith('exchange_'))
async def choose_exchange(query: types.CallbackQuery):
    exchange = query.data.split('_')[1]
    chat_id = str(query.message.chat.id)
    temp_user_data[chat_id] = {"exchange": exchange}

    coin_kb = InlineKeyboardMarkup()
    for i in range(0, len(coins), 3):
        row_buttons = [InlineKeyboardButton(coin, callback_data=f'coin_{coin}') for coin in coins[i:i + 3]]
        coin_kb.row(*row_buttons)
    try:
        await bot.send_message(query.from_user.id,
                               f"\U00002757\U0000FE0FYou have chosen the exchange {exchange}. Now choose the coin to track:",
                               reply_markup=coin_kb)
    except BotBlocked:
        logging.error(f"Bot blocked by user with chat_id {chat_id}. Message is not send.")
    except ChatNotFound:
        logging.error(f"Chat with chat_id {chat_id} not found. Message is not send.")
    except RetryAfter as e:
        logging.error(f"Error: need to wait {e.timeout} seconds before next atemption.")
    except Exception as e:
        logging.error(f"UnexpectedError: {e}")


@dp.callback_query_handler(lambda query: query.data.startswith('coin_'))
async def choose_coin(query: types.CallbackQuery):
    coin = query.data.split('_')[1]
    chat_id = str(query.message.chat.id)
    if chat_id in temp_user_data:
        temp_user_data[chat_id]["coin"] = coin
        try:
            await bot.send_message(query.from_user.id,
                                   f"\U00002757\U0000FE0FYou have chosen the {coin} coin. Now choose the rate difference for notifications:",
                                   reply_markup=diff_kb)
        except BotBlocked:
            logging.error(f"Bot blocked by user with chat_id {chat_id}. Message is not send.")
        except ChatNotFound:
            logging.error(f"Chat with chat_id {chat_id} not found. Message is not send.")
        except RetryAfter as e:
            logging.error(f"Error: need to wait {e.timeout} seconds before next atemption.")
        except Exception as e:
            logging.error(f"UnexpectedError: {e}")
    else:
        try:
            await bot.send_message(query.from_user.id, "Error: Temporary data not found.")
        except BotBlocked:
            logging.error(f"Bot blocked by user with chat_id {chat_id}. Message is not send.")
        except ChatNotFound:
            logging.error(f"Chat with chat_id {chat_id} not found. Message is not send.")
        except RetryAfter as e:
            logging.error(f"Error: need to wait {e.timeout} seconds before next atemption.")
        except Exception as e:
            logging.error(f"UnexpectedError: {e}")


@dp.callback_query_handler(lambda query: query.data.startswith('diff_'))
async def process_diff(query: types.CallbackQuery):
    diff_value = query.data.split('_')[1]
    chat_id = str(query.message.chat.id)

    if chat_id in temp_user_data:
        # Load data from JSON
        user_data = load_data()

        # Generate a unique identifier for the new record
        pair_id = str(len(user_data) + 1)

        # Add rate difference to temporary data
        temp_user_data[chat_id]["diff"] = diff_value

        # Save temporary data to main JSON
        user_data[pair_id] = {
            "chat_id": chat_id,
            "exchange": temp_user_data[chat_id]["exchange"],
            "coin": temp_user_data[chat_id]["coin"],
            "diff": diff_value
        }

        # Clear temporary data
        del temp_user_data[chat_id]

        save_data(user_data)
        try:
            await bot.send_message(query.from_user.id,
                                   f"\U00002757\U0000FE0FYou have chosen a rate difference of {diff_value} %. Notifications will be set up.")
        except BotBlocked:
            logging.error(f"Bot blocked by user with chat_id {chat_id}. Message is not send.")
        except ChatNotFound:
            logging.error(f"Chat with chat_id {chat_id} not found. Message is not send.")
        except RetryAfter as e:
            logging.error(f"Error: need to wait {e.timeout} seconds before next atemption.")
        except Exception as e:
            logging.error(f"UnexpectedError: {e}")
    else:
        try:
            await bot.send_message(query.from_user.id, "Error: Temporary data not found.")
        except BotBlocked:
            logging.error(f"Bot blocked by user with chat_id {chat_id}. Message is not send.")
        except ChatNotFound:
            logging.error(f"Chat with chat_id {chat_id} not found. Message is not send.")
        except RetryAfter as e:
            logging.error(f"Error: need to wait {e.timeout} seconds before next atemption.")
        except Exception as e:
            logging.error(f"UnexpectedError: {e}")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(update_exchange_rates())
    loop.create_task(periodic_message_sender())
    try:
        loop.run_until_complete(dp.start_polling())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

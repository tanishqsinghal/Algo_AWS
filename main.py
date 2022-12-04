import schedule, time, datetime, requests, json, os
from threading import Timer
import pandas as pd

from fyers_api import fyersModel, accessToken

session = accessToken.SessionModel(client_id='YUBD35U8OF-100', secret_key='TJFZARII4E',
                                   redirect_uri='http://h2r1m.pythonanywhere.com/user/', response_type='code',
                                   grant_type='authorization_code')

config = {
    "client_id": "YUBD35U8OF-100",
    "secret_key": "TJFZARII4E",
    "access_token": "",
    "request_url": "https://sm.affility.store"
}

def send_telegram_message(request):
    bot_token = '5969891290:AAE13zPtwdc2P3VqZy6o_7opvRHbAtH_vfE'
    bot_chatID = '998029180'
    message = request
    # message = datetime.datetime.now()
    apiURL = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': bot_chatID, 'text': message})
        # print(response.text)
    except Exception as e:
        print(e)
    return

def execute_trade():
    print("TRADES EXECUTED")

def schedule_trades(functionName, timeToExecute):
    print("SCHEDULED")
    currentTime = datetime.datetime.now()
    executionTime = datetime.datetime.now().strftime('%d-%m-%Y') + " " + timeToExecute
    executionTime = datetime.datetime.strptime(executionTime, '%d-%m-%Y %H-%M-%S')
    delay = (executionTime - currentTime).total_seconds()
    if delay >= 0:
        Timer(delay, functionName).start()


schedule.every().monday.at("09:00").do(schedule_trades, execute_trade, '09-20-00')
schedule.every().tuesday.at("09:00").do(schedule_trades, execute_trade, '09-20-00')
schedule.every().wednesday.at("09:00").do(schedule_trades, execute_trade, '09-20-00')
schedule.every().thursday.at("09:00").do(schedule_trades, execute_trade, '09-20-00')
schedule.every().friday.at("09:00").do(schedule_trades, execute_trade, '09-20-00')
# schedule.every().sunday.at("13:54").do(schedule_trades, execute_trade, '13-55-00')

while True:
    schedule.run_pending()
    time.sleep(60)
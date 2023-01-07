import schedule, time, datetime, requests, json, os, pytz
import threading, sys
from threading import Timer
import pandas as pd
# import datatable as dt
from fyers_api.Websocket import ws

from fyers_api import fyersModel, accessToken
from autologin import *

session = accessToken.SessionModel(client_id='ORDBWKXRS7-100', secret_key='5R3786TZ0W',
                                   redirect_uri='https://www.google.co.in', response_type='code',
                                   grant_type='authorization_code')

config = {
    "client_id": "ORDBWKXRS7-100",
    "secret_key": "5R3786TZ0W",
    "access_token": "",
    "request_url": "https://sm.affility.store",
    "strikes_traded": [],
    "strikes_entry_price_combined": 0,
    "strikes_ltp": [0, 0, 0, 0],
    "stop_loss": 0,
    "target": 0,
    "trades_exited": False
}

def schedule_trades(functionName, timeToExecute):
    # timeToExecute = str(convert_time_to_utc(timeToExecute))
    currentTime = datetime.datetime.now()
    executionTime = datetime.datetime.now().strftime('%d-%m-%Y') + " " + timeToExecute
    executionTime = datetime.datetime.strptime(executionTime, '%d-%m-%Y %H:%M:%S')
    delay = (executionTime - currentTime).total_seconds()
    # send_telegram_message(str(functionName) + "WITH DELAY " + str(delay) + " SCHEDULED")
    if delay >= 0:
        Timer(delay, functionName).start()
    return

def get_live_data():
    print('Started')
    data = {"symbol": "NSE:NIFTYBANK-INDEX", "resolution": "1", "date_format": "1", "range_from": "2022-12-30", "range_to": "2022-12-30", "cont_flag": "1"}
    while True:
        received_data = config["fyers"].history(data)
        if received_data['candles'] != None:
            last_candle = received_data['candles'][-1]
            second_last_candle = received_data['candles'][-2]
            if (last_candle[1] >= second_last_candle[4]) and (last_candle[2] <= second_last_candle[2]) and (last_candle[3] >= second_last_candle[3]) and (last_candle[4] <= second_last_candle[1]):
                if second_last_candle[1] > second_last_candle[4]:
                    print('BEARISH INSIDE')
                else:
                    print('INSIDE IN BEARISH')
                print(datetime.datetime.now().strftime("%H:%M:%S"))
            if (last_candle[1] <= second_last_candle[4]) and (last_candle[2] <= second_last_candle[2]) and (last_candle[3] >= second_last_candle[3]) and (last_candle[4] >= second_last_candle[1]):
                if second_last_candle[1] < second_last_candle[4]:
                    print('BULLISH INSIDE')
                else:
                    print('INSIDE IN BULLISH')
                print(datetime.datetime.now().strftime("%H:%M:%S"))
            # print(received_data['candles'][-1])
        time.sleep(60)

def test_data():
    print('Test Started')
    data = {"symbol": "NSE:NIFTYBANK-INDEX", "resolution": "15", "date_format": "1", "range_from": "2022-10-03", "range_to": "2022-12-30", "cont_flag": "1"}
    # print(data[-1])
    received_data = config["fyers"].history(data)
    print(received_data)
    candles = received_data['candles']

    entry = 0
    stop_loss = 0
    target = 0
    type = 0
    trade_taken = 0
    sl_hit = 0

    total_trades = 0
    total_targets = 0
    total_losses = 0
    total_points = 0

    for i in range(len(candles) - 1):
        if trade_taken == 0 and entry != 0 and sl_hit == 0:
            if type == 1:
                if candles[i - 1][2] >= entry:
                    trade_taken = 1
                    total_trades += 1
                    # print('BULLISH ENTRY' + str(datetime.datetime.fromtimestamp(candles[i][0])))
                if candles[i - 1][3] <= stop_loss:
                    sl_hit = 1
            elif type == 2:
                if candles[i - 1][3] <= entry:
                    trade_taken = 1
                    total_trades += 1
                    # print('BEARISH ENTRY' + str(datetime.datetime.fromtimestamp(candles[i][0])))
                if candles[i - 1][2] >= stop_loss:
                    sl_hit = 1

        if trade_taken == 1:
            if type == 1:
                if candles[i - 1][2] >= target:
                    trade_taken = 0
                    total_targets += 1
                    total_points += (target - entry)
                    print(total_points)
                    entry = 0
                    # print('Target:- ' + str(datetime.datetime.fromtimestamp(candles[i][0])) + str(target))
                elif candles[i - 1][3] <= stop_loss:
                    trade_taken = 0
                    total_losses += 1
                    total_points -= (entry - stop_loss)
                    print(total_points)
                    entry = 0
                    # print('SL:- ' + str(datetime.datetime.fromtimestamp(candles[i][0])) + str(stop_loss))
            elif type == 2:
                if candles[i - 1][3] <= target:
                    trade_taken = 0
                    total_targets += 1
                    total_points += (entry - target)
                    print(total_points)
                    entry = 0
                    # print('Target:- ' + str(datetime.datetime.fromtimestamp(candles[i][0])) + str(target))
                elif candles[i - 1][2] >= stop_loss:
                    trade_taken = 0
                    total_losses += 1
                    total_points -= (stop_loss - entry)
                    print(total_points)
                    entry = 0
                    # print('SL:- ' + str(datetime.datetime.fromtimestamp(candles[i][0])) + str(stop_loss))


        current_time = datetime.datetime.fromtimestamp(candles[i][0]).strftime("%H:%M:%S")
        current_time = datetime.datetime.strptime(str(current_time), "%H:%M:%S")

        start_time = datetime.datetime.strptime(str(datetime.time(9, 30, 0)), "%H:%M:%S")
        end_time = datetime.datetime.strptime(str(datetime.time(15, 0, 0)), "%H:%M:%S")
        if start_time <= current_time <= end_time:
            last_candle = candles[i-1]
            second_last_candle = candles[i-2]
            if (last_candle[1] <= second_last_candle[4]) and (last_candle[2] <= second_last_candle[2]) and (
                    last_candle[3] >= second_last_candle[3]) and (last_candle[4] >= second_last_candle[1]):
                # if second_last_candle[1] < second_last_candle[4]:
                #     print('BULLISH INSIDE')
                # else:
                #     print('INSIDE IN BULLISH')
                if second_last_candle[1] < second_last_candle[4]:
                    print(str(datetime.datetime.fromtimestamp(candles[i][0])) + "BULLISH")
                    if trade_taken == 0:
                        entry = last_candle[2] + 1
                        stop_loss = last_candle[3] - 1
                        target = last_candle[2] + (last_candle[2] - last_candle[3]) * 1.5
                        type = 1
                        sl_hit = 0
            if (last_candle[1] >= second_last_candle[4]) and (last_candle[2] <= second_last_candle[2]) and (
                    last_candle[3] >= second_last_candle[3]) and (last_candle[4] <= second_last_candle[1]):
                # if second_last_candle[1] > second_last_candle[4]:
                #     print('BEARISH INSIDE')
                # else:
                #     print('INSIDE IN BEARISH')
                if second_last_candle[1] > second_last_candle[4]:
                    print(str(datetime.datetime.fromtimestamp(candles[i][0])) + "BEARISH")
                    if trade_taken == 0:
                        entry = last_candle[3] - 1
                        stop_loss = last_candle[2] + 1
                        target = last_candle[3] - (last_candle[2] - last_candle[3]) * 1.5
                        type = 2
                        sl_hit = 0


    print('Total Trades:- ' + str(total_trades))
    print('Total Targets:- ' + str(total_targets))
    print('Total Losses:- ' + str(total_losses))
    print('Total Points:- ' + str(total_points))

def generate_token():
    print("_______________GENERATING TOKEN_________")
    file = json.load(open("token.json", 'r'))
    if file['date'] == str(datetime.date.today()):
        config["access_token"] = file['token']
        print("FOUND")
    else:
        config["access_token"] = login()
        data_to_write = {
            'date': str(datetime.date.today()),
            'token': config["access_token"]
        }
        file = open("token.json", 'w')
        json.dump(data_to_write, file)
        file.close()
        print("ADDED")

    instruments = pd.read_csv('https://public.fyers.in/sym_details/NSE_FO.csv', header=None)
    ism = instruments[instruments[13] == '{}'.format('BANKNIFTY')]
    config["expiry_date_banknifty"] = ism[9].tolist()[0][13:-7]

    # instruments = dt.fread('https://public.fyers.in/sym_details/NSE_FO.csv')
    # instruments = instruments.to_list()
    # config["expiry_date_banknifty"] = instruments[9][instruments[13].index('BANKNIFTY')][13:-7]

    config["fyers"] = fyersModel.FyersModel(client_id=config["client_id"], token=config["access_token"],
                                            log_path="")
    print("LOGGED IN")
    # schedule_trades(get_live_data, '12:38:01')
    # test_data()

# generate_token()

def test():
    print("WORKING")


test()

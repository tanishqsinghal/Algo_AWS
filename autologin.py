import configparser
from urllib.parse import urlparse, parse_qs

from fyers_api import fyersModel, accessToken

import schedule, time, datetime, requests, json, os, pytz
import threading, sys
from threading import Timer
# import pandas as pd
# import datatable as dt

from config_file import *

# session = accessToken.SessionModel(client_id='ORDBWKXRS7-100', secret_key='5R3786TZ0W',
#                                    redirect_uri='https://www.google.co.in', response_type='code',
#                                    grant_type='authorization_code')


config_data = configparser.ConfigParser()
config_data.read('config.ini')
client_id = config_data['fyers']['app_id']
app_id = client_id[:-4]
secret_key = config_data['fyers']['app_secret']
redirect_uri = config_data['fyers']['redirect_url']
username = config_data['fyers']['user_id']
password = config_data['fyers']['password']
pan = config_data['fyers']['pan']
pin = int(config_data['fyers']['two_fa'])


def login():
    session = accessToken.SessionModel(client_id=client_id, secret_key=secret_key, redirect_uri=redirect_uri,

                                   response_type='code', grant_type='authorization_code')



    s = requests.Session()



    data1 = f'{{"fy_id":"{username}","password":"{password}","app_id":"2","imei":"","recaptcha_token":""}}'

    r1 = s.post('https://api.fyers.in/vagator/v1/login', data=data1)

    request_key = r1.json()["request_key"]

    data2 = f'{{"request_key":"{request_key}","identity_type":"pin","identifier":"{pin}","recaptcha_token":""}}'

    r2 = s.post('https://api.fyers.in/vagator/v1/verify_pin', data=data2)

    headers = {

    'authorization': f"Bearer {r2.json()['data']['access_token']}",

    'content-type': 'application/json; charset=UTF-8'

    }



    data3 = f'{{"fyers_id":"{username}","app_id":"{app_id}","redirect_uri":"{redirect_uri}","appType":"100","code_challenge":"","state":"abcdefg","scope":"","nonce":"","response_type":"code","create_cookie":true}}'



    r3 = s.post('https://api.fyers.in/api/v2/token', headers=headers, data=data3)

    parsed = urlparse(r3.json()['Url'])

    auth_code = parse_qs(parsed.query)['auth_code'][0]

    session.set_token(auth_code)

    response = session.generate_token()

    token = response["access_token"]

    # print(token)
    # print('Got the access token!!!')

    return token


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

    # config["access_token"] = login()

    # instruments = pd.read_csv('https://public.fyers.in/sym_details/NSE_FO.csv', header=None)
    # ism = instruments[instruments[13] == '{}'.format('BANKNIFTY')]
    # config["expiry_date_banknifty"] = ism[9].tolist()[0][13:-7]

    # instruments = dt.fread('https://public.fyers.in/sym_details/NSE_FO.csv')
    # instruments = instruments.to_list()
    # config["expiry_date_banknifty"] = instruments[9][instruments[13].index('BANKNIFTY')][13:-7]

    config["fyers"] = fyersModel.FyersModel(client_id=config["client_id"], token=config["access_token"],
                                            log_path="")
    print("LOGGED IN")
    send_telegram_message("LOGGED IN")
    # import algo_simple_straddle
    # algo_simple_straddle.start_algo()
    # import algo_920_sl
    # algo_920_sl.start_algo()
    import algo_range_break
    algo_range_break.schedule_algo()



def schedule_trades(functionName, timeToExecute):
    timeToExecute = str(convert_time_to_utc(timeToExecute))
    currentTime = datetime.datetime.now()
    executionTime = datetime.datetime.now().strftime('%d-%m-%Y') + " " + timeToExecute
    executionTime = datetime.datetime.strptime(executionTime, '%d-%m-%Y %H:%M:%S')
    delay = (executionTime - currentTime).total_seconds()
    # send_telegram_message(str(functionName) + "WITH DELAY " + str(delay) + " SCHEDULED")
    if delay >= 0:
        Timer(delay, functionName).start()
    return


def check_range_nr7(candles, stock, timeframe):
    for x in range(len(candles) - 1):
        # Proceed ahead if current time is not in the defined range
        candle_time = datetime.datetime.fromtimestamp(candles[x][0])
        if datetime.time(9, 30, 0) > candle_time.time() > datetime.time(2, 45, 0):
            continue

        first_candle_high = candles[x][2]
        first_candle_low = candles[x][3]
        first_candle_range = first_candle_high - first_candle_low

        range_array = []
        is_nr7_found = False

        for y in range(x, len(candles) - 1):
            candle_time = datetime.datetime.fromtimestamp(candles[y][0])
            current_candle_close = candles[y][4]
            if current_candle_close > first_candle_high or current_candle_close < first_candle_low:
                if y - x < 7:
                    break
                else:
                    # candle_time = datetime.datetime.fromtimestamp(candles[y][0])
                    # print("BREAK FOUND:- ", candle_time)
                    # if is_nr7_found:
                    #     print("BREAK FOUND WITH NR7:- ", candle_time)
                    # else:
                    #     print("BREAK FOUND:- ", candle_time)
                    break
            else:
                current_candle_high = candles[y][2]
                current_candle_low = candles[y][3]
                current_candle_range = current_candle_high - current_candle_low

                if len(range_array) > 5:
                    if is_nr7_found == False:
                        if current_candle_range < min(range_array):
                            print(stock + " NR7 Found:- ", candle_time)
                            if y >= len(candles) - 2:
                                config["message_to_send"] += '\n\nNR7 <-' + str(timeframe) + '-> ' + stock + ' <--> ' + str(candle_time.time())
                            # send_telegram_message('NR7 <-' + str(timeframe) + '-> ' + stock + ' <--> ' + str(candle_time.time()))
                            is_nr7_found = True
                            break
                else:
                    range_array.append(current_candle_range)

def run_scanner(timeframe):
    print("TRADES EXECUTED-----------------------------------" + str(timeframe) + "-----------------------")
    stocks = ["HDFCBANK","PFC","RECLTD","RELIANCE","TATAPOWER","COALINDIA","SBIN","TATAMOTORS","IRCTC","ICICIBANK","LT","HAL","NTPC","KOTAKBANK","DLF","HAVELLS","AXISBANK","BANDHANBNK","BANKBARODA","IEX","INDUSINDBK","CHOLAFIN","ADANIPORTS","BAJFINANCE","CANBK","GAIL","FEDERALBNK","TATASTEEL","BAJAJFINSV","M&MFIN","INDUSTOWER","TCS","MARUTI","INFY","HINDALCO","POWERGRID","IOC","IDFCFIRSTB","IDEA","ZEEL","SHRIRAMFIN","ADANIENT","ITC","BHARTIARTL","BEL","HCLTECH","CONCOR","RBLBANK","BPCL","ASHOKLEY","HINDPETRO","JSWSTEEL","ICICIPRULI","TECHM","ONGC","PVRINOX","PETRONET","HEROMOTOCO","INDIGO","NMDC","TITAN","CUMMINSIND","HINDUNILVR","M&M","DIXON","IGL","UPL","PERSISTENT","POLYCAB","TATACOMM","BAJAJ-AUTO","GODREJPROP","LICHSGFIN","GLENMARK","BHARATFORG","WIPRO","HDFCAMC","JINDALSTEL","AMBUJACEM","ACC","HDFCLIFE","GMRINFRA","SBILIFE","SUNPHARMA","PEL","AUROPHARMA","GRASIM","VEDL","ULTRACEMCO","CHAMBLFERT","IDFC","AUBANK","OBEROIRLTY","VOLTAS","NATIONALUM","CROMPTON","TRENT","DEEPAKNTR","BRITANNIA","ASIANPAINT","EICHERMOT","SRF","BHEL","APOLLOHOSP","LTIM","CUB","COFORGE","LUPIN","DRREDDY","TATACONSUM","MFSL","DIVISLAB","ESCORTS","CIPLA","PIIND","PAGEIND","INDHOTEL","LAURUSLABS","L&TFH","MCDOWELL-N","DALBHARAT","ABB","SBICARD","TVSMOTOR","AARTIIND","ABCAPITAL","JUBLFOOD","UBL","BSOFT","ASTRAL","GNFC","ABFRL","PNB","SIEMENS","NAUKRI","ZYDUSLIFE","TATACHEM","MCX","EXIDEIND","MPHASIS","LALPATHLAB","TORNTPHARM","BIOCON","LTTS","OFSS","SHREECEM","GUJGASLTD","SUNTV","SYNGENE","GRANULES","RAMCOCEM","BATAINDIA","CANFINHOME","BERGEPAINT","PIDILITIND","MUTHOOTFIN","METROPOLIS","COLPAL","APOLLOTYRE","NESTLEIND","GODREJCP","MOTHERSON","INDIAMART","SAIL","JKCEMENT","MRF","COROMANDEL","NAVINFLUOR","ICICIGI","ATUL","DABUR","MGL","BALKRISIND","BALRAMCHIN","IPCALAB","BOSCHLTD","ALKEM","MARICO","ABBOTINDIA","MANAPPURAM","HINDCOPPER","IBULHSGFIN","INDIACEM","DELTACORP"]
    # stocks = ["HDFCBANK", "PFC", "RECLTD", "RELIANCE", "TATAPOWER", "COALINDIA", "SBIN", "TATAMOTORS"]
    config["message_to_send"] = ""

    for x in range(len(stocks)):
        data = {
            "symbol": "NSE:" + stocks[x] + "-EQ",
            "resolution": str(timeframe),
            "date_format": "1",
            "range_from": datetime.datetime.today().strftime('%Y-%m-%d'),
            "range_to": datetime.datetime.today().strftime('%Y-%m-%d'),
            "cont_flag": "1"
        }

        response = config["fyers"].history(data=data)
        if response['s'] == 'ok':
            check_range_nr7(response['candles'], stocks[x], timeframe)
    send_telegram_message(config["message_to_send"])

schedule.every().monday.at(convert_time_to_utc("09:00:00")).do(generate_token)
schedule.every().tuesday.at(convert_time_to_utc("09:00:00")).do(generate_token)
schedule.every().wednesday.at(convert_time_to_utc("09:00:00")).do(generate_token)
schedule.every().thursday.at(convert_time_to_utc("09:00:00")).do(generate_token)
schedule.every().friday.at(convert_time_to_utc("09:00:00")).do(generate_token)
# schedule.every().saturday.at("11:03:00").do(generate_token)
# schedule.every().sunday.at(convert_time_to_utc("09:00:00")).do(generate_token)
# schedule.every().sunday.at(convert_time_to_utc("09:00:00")).do(schedule_trades, execute_trade, '13-55-00')
generate_token()
run_scanner(15)

#Code to test if the script is working in the background or not
# def background_test():
#     print("WORKING IN BACKGROUND")
#     send_telegram_message("WORKING IN BACKGROUND")
#
# Timer(30, background_test).start()

while True:
    schedule.run_pending()
    time.sleep(60)
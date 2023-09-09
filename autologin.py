import configparser
from urllib.parse import urlparse, parse_qs

from fyers_api import fyersModel, accessToken

import schedule, time, datetime, requests, json, os, pytz
import threading, sys
from threading import Timer
import pandas as pd
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

    instruments = pd.read_csv('https://public.fyers.in/sym_details/NSE_FO.csv', header=None)
    ism = instruments[instruments[13] == '{}'.format('BANKNIFTY')]
    config["expiry_date_banknifty"] = ism[9].tolist()[0][13:-7]

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


schedule.every().monday.at(convert_time_to_utc("09:00:00")).do(generate_token)
schedule.every().tuesday.at(convert_time_to_utc("09:00:00")).do(generate_token)
schedule.every().wednesday.at(convert_time_to_utc("09:00:00")).do(generate_token)
schedule.every().thursday.at(convert_time_to_utc("09:00:00")).do(generate_token)
schedule.every().friday.at(convert_time_to_utc("09:00:00")).do(generate_token)
# schedule.every().saturday.at("11:03:00").do(generate_token)
# schedule.every().sunday.at(convert_time_to_utc("09:00:00")).do(generate_token)
# schedule.every().sunday.at(convert_time_to_utc("09:00:00")).do(schedule_trades, execute_trade, '13-55-00')
# generate_token()
while True:
    schedule.run_pending()
    time.sleep(60)
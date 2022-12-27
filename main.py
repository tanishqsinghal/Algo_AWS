import schedule, time, datetime, requests, json, os, pytz
import threading, sys
from threading import Timer
# import pandas as pd
import datatable as dt
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


def custom_message(msg):
    # print(f"Custom:{msg}")
    for x in range(4):
        if msg[0]['symbol'] == config['strikes_traded'][x]:
            config['strikes_ltp'][x] = msg[0]['ltp']

    combined_price_current = (config['strikes_ltp'][2] + config['strikes_ltp'][3]) - (config['strikes_ltp'][0] + config['strikes_ltp'][1])
    combined_price_current *= 25
    # print(combined_price_current)
    if (combined_price_current >= config['stop_loss'] or combined_price_current <= config['target']) and config['trades_exited'] == False:
        config['trades_exited'] = True
        pnl = config['strikes_entry_price_combined'] - combined_price_current
        print(pnl)
        send_telegram_message('P&L <--> ' + str(round(pnl, 2)))
        print('EXIT:- ' + str(combined_price_current))
        # config['fs'].unsubscribe(symbol=config['strikes_traded'])
        # exit_trade()
        sys.exit()
        exit_trade()


def run_websocket():
    Access_Token = config["client_id"] + ':' + config["access_token"]
    data_type = "symbolData"
    fs = ws.FyersSocket(access_token=Access_Token, run_background=False, log_path='')
    fs.websocket_data = custom_message
    config['fs'] = fs
    print("CONFIGURATION")
    # fs.subscribe(symbol=config["strikes_traded"], data_type=data_type)
    # fs.keep_running()
    config['websocket_process'] = threading.Thread(target=fs.subscribe, args=(config["strikes_traded"], data_type,))
    config['websocket_process'].daemon = True
    config['websocket_process'].start()



def generate_token():
    print("_______________GENERATING TOKEN_________")
    config["access_token"] = login()

    # instruments = pd.read_csv('https://public.fyers.in/sym_details/NSE_FO.csv', header=None)
    # ism = instruments[instruments[13] == '{}'.format('BANKNIFTY')]
    # config["expiry_date_banknifty"] = ism[9].tolist()[0][13:-7]

    instruments = dt.fread('https://public.fyers.in/sym_details/NSE_FO.csv')
    instruments = instruments.to_list()
    config["expiry_date_banknifty"] = instruments[9][instruments[13].index('BANKNIFTY')][13:-7]

    config["fyers"] = fyersModel.FyersModel(client_id=config["client_id"], token=config["access_token"],
                                            log_path="")
    print("LOGGED IN")
    send_telegram_message("LOGGED IN")
    schedule_trades(execute_trade, '09:20:00')

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
    spotPrice = config["fyers"].quotes({"symbols": "NSE:NIFTYBANK-INDEX"})['d'][0]['v']['lp']
    expiry_date = config["expiry_date_banknifty"]
    spotPrice_Round = round(spotPrice / 100)
    # expiry_date = '22D01'
    buyGap = 15
    sellGap = 0
    CE_Buy_StrikeSymbol = 'NSE:BANKNIFTY' + expiry_date + str(
        (spotPrice_Round + buyGap + sellGap + (5 - ((spotPrice_Round + buyGap + sellGap) % 5))) * 100) + 'CE'
    PE_Buy_StrikeSymbol = 'NSE:BANKNIFTY' + expiry_date + str(
        (spotPrice_Round - buyGap - sellGap - ((spotPrice_Round - buyGap - sellGap) % 5)) * 100) + 'PE'
    CE_Sell_StrikeSymbol = 'NSE:BANKNIFTY' + expiry_date + str((spotPrice_Round + sellGap) * 100) + 'CE'
    PE_Sell_StrikeSymbol = 'NSE:BANKNIFTY' + expiry_date + str((spotPrice_Round - sellGap) * 100) + 'PE'

    orderData_Buy = [{
        "symbol": CE_Buy_StrikeSymbol,
        "qty": 25,
        "type": 2,
        "side": 1,
        "productType": "INTRADAY",
        "limitPrice": 0,
        "stopPrice": 0,
        "disclosedQty": 0,
        "validity": "DAY",
        "offlineOrder": "False",
        "stopLoss": 0,
        "takeProfit": 0
    },
        {
            "symbol": PE_Buy_StrikeSymbol,
            "qty": 25,
            "type": 2,
            "side": 1,
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "disclosedQty": 0,
            "validity": "DAY",
            "offlineOrder": "False",
            "stopLoss": 0,
            "takeProfit": 0
        }]

    orderData_Sell = [{
        "symbol": CE_Sell_StrikeSymbol,
        "qty": 25,
        "type": 2,
        "side": -1,
        "productType": "INTRADAY",
        "limitPrice": 0,
        "stopPrice": 0,
        "disclosedQty": 0,
        "validity": "DAY",
        "offlineOrder": "False",
        "stopLoss": 0,
        "takeProfit": 0
    },
        {
            "symbol": PE_Sell_StrikeSymbol,
            "qty": 25,
            "type": 2,
            "side": -1,
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "disclosedQty": 0,
            "validity": "DAY",
            "offlineOrder": "False",
            "stopLoss": 0,
            "takeProfit": 0
        }]

    # config["fyers"].place_basket_orders(orderData_Buy)
    # time.sleep(1)
    # config["fyers"].place_basket_orders(orderData_Sell)

    dataToWrite = {
        'response': 0,
        'orderPlacementStatus': 1,
        'strikes': [],
        'strikesLTPEntry': [],
        'combinedEntryPrice': 0,
        'spotLTPEntry': spotPrice,
        'orderData': [],
        'orderEntryResponse': []
    }
    dataToWrite['strikes'].append(CE_Buy_StrikeSymbol)
    dataToWrite['strikes'].append(PE_Buy_StrikeSymbol)
    dataToWrite['strikes'].append(CE_Sell_StrikeSymbol)
    dataToWrite['strikes'].append(PE_Sell_StrikeSymbol)

    CE_Buy_StrikeSymbol_LTP = config["fyers"].quotes({"symbols": CE_Buy_StrikeSymbol})['d'][0]['v']['lp']
    PE_Buy_StrikeSymbol_LTP = config["fyers"].quotes({"symbols": PE_Buy_StrikeSymbol})['d'][0]['v']['lp']
    CE_Sell_StrikeSymbol_LTP = config["fyers"].quotes({"symbols": CE_Sell_StrikeSymbol})['d'][0]['v']['lp']
    PE_Sell_StrikeSymbol_LTP = config["fyers"].quotes({"symbols": PE_Sell_StrikeSymbol})['d'][0]['v']['lp']

    combined_price_entry = (CE_Sell_StrikeSymbol_LTP + PE_Sell_StrikeSymbol_LTP) - (CE_Buy_StrikeSymbol_LTP + PE_Buy_StrikeSymbol_LTP)
    dataToWrite['combinedEntryPrice'] = combined_price_entry

    stop_loss = combined_price_entry * 25 * 1.3
    target = combined_price_entry * 25 * 0.65

    config['strikes_entry_price_combined'] = combined_price_entry * 25
    config["stop_loss"] = stop_loss
    config["target"] = target
    print("Entry:- " + str(combined_price_entry * 25))
    print("SL:-" + str(stop_loss))
    print("Target:- " + str(target))

    dataToWrite['strikesLTPEntry'].append(CE_Buy_StrikeSymbol_LTP)
    dataToWrite['strikesLTPEntry'].append(PE_Buy_StrikeSymbol_LTP)
    dataToWrite['strikesLTPEntry'].append(CE_Sell_StrikeSymbol_LTP)
    dataToWrite['strikesLTPEntry'].append(PE_Sell_StrikeSymbol_LTP)

    dataToWrite['orderData'].append(orderData_Buy)
    dataToWrite['orderData'].append(orderData_Sell)

    telegram_Message = "Entry\nBANKNIFTY <-> " + str(spotPrice) + "\n" + \
                       CE_Buy_StrikeSymbol[-7:] + " <- B -> " + str(CE_Buy_StrikeSymbol_LTP) + "\n" + \
                       PE_Buy_StrikeSymbol[-7:] + " <- B -> " + str(PE_Buy_StrikeSymbol_LTP) + "\n" + \
                       CE_Sell_StrikeSymbol[-7:] + " <- S -> " + str(CE_Sell_StrikeSymbol_LTP) + "\n" + \
                       PE_Sell_StrikeSymbol[-7:] + " <- S -> " + str(PE_Sell_StrikeSymbol_LTP)

    # file = open(file_path, 'w')
    # json.dump(dataToWrite, file)
    # file.close()
    # print('FILE CREATED')
    # file_json = json.load(open(file_path, 'r'))
    # print(file_json)

    # requests.post(config['request_url'], data=dataToWrite)
    config["trades_data"] = dataToWrite

    schedule_trades(exit_trade, '15:05:00')
    send_telegram_message(telegram_Message)

    config["strikes_traded"] = [CE_Buy_StrikeSymbol, PE_Buy_StrikeSymbol, CE_Sell_StrikeSymbol, PE_Sell_StrikeSymbol]
    config["strikes_ltp"] = [CE_Buy_StrikeSymbol_LTP, PE_Buy_StrikeSymbol_LTP, CE_Sell_StrikeSymbol_LTP, PE_Sell_StrikeSymbol_LTP]
    run_websocket()
    return


def exit_trade():
    send_telegram_message(config["trades_data"])
    spotPrice = config["fyers"].quotes({"symbols": "NSE:NIFTYBANK-INDEX"})['d'][0]['v']['lp']

    exitOrderData_Sell = [{
        "id": "CE SELL ORDER ID"
    },
        {
            "id": "PE SELL ORDER ID"
        }]
    exitOrderData_Buy = [{
        "id": "CE BUY ORDER ID"
    },
        {
            "id": "PE BUY ORDER ID"
        }]

    # config["fyers"].exit_positions(exitOrderData_Sell)
    # time.sleep(1)
    # config["fyers"].exit_positions(exitOrderData_Buy)

    dataToWrite = {
        'strikesLTPExit': [],
        'spotLTPExit': spotPrice,
        'pnl': 0,
        'orderExitResponse': []
    }

    # file = open(file_path, 'w')
    # json.dump(dataToWrite, file)
    # file.close()
    # print('FILE CREATED')
    # file = json.load(open(file_path, 'r'))

    # response_data = requests.post(config['request_url'])
    # file = json.loads(response_data.text)

    file = config["trades_data"]

    CE_Buy_StrikeSymbol = file['strikes'][0]
    PE_Buy_StrikeSymbol = file['strikes'][1]
    CE_Sell_StrikeSymbol = file['strikes'][2]
    PE_Sell_StrikeSymbol = file['strikes'][3]

    CE_Buy_StrikeSymbol_LTP = config["fyers"].quotes({"symbols": CE_Buy_StrikeSymbol})['d'][0]['v']['lp']
    PE_Buy_StrikeSymbol_LTP = config["fyers"].quotes({"symbols": PE_Buy_StrikeSymbol})['d'][0]['v']['lp']
    CE_Sell_StrikeSymbol_LTP = config["fyers"].quotes({"symbols": CE_Sell_StrikeSymbol})['d'][0]['v']['lp']
    PE_Sell_StrikeSymbol_LTP = config["fyers"].quotes({"symbols": PE_Sell_StrikeSymbol})['d'][0]['v']['lp']

    dataToWrite['pnl'] = (CE_Buy_StrikeSymbol_LTP - file['strikesLTPEntry'][0]) + \
                         (PE_Buy_StrikeSymbol_LTP - file['strikesLTPEntry'][1]) + \
                         (file['strikesLTPEntry'][2] - CE_Sell_StrikeSymbol_LTP) + \
                         (file['strikesLTPEntry'][3] - PE_Sell_StrikeSymbol_LTP)

    dataToWrite['strikesLTPExit'].append(CE_Buy_StrikeSymbol_LTP)
    dataToWrite['strikesLTPExit'].append(PE_Buy_StrikeSymbol_LTP)
    dataToWrite['strikesLTPExit'].append(CE_Sell_StrikeSymbol_LTP)
    dataToWrite['strikesLTPExit'].append(PE_Sell_StrikeSymbol_LTP)

    telegram_Message = "Exit\nBANKNIFTY <-> " + str(spotPrice) + "\n" + \
                       CE_Buy_StrikeSymbol[-7:] + " <- S -> " + str(CE_Buy_StrikeSymbol_LTP) + "\n" + \
                       PE_Buy_StrikeSymbol[-7:] + " <- S -> " + str(PE_Buy_StrikeSymbol_LTP) + "\n" + \
                       CE_Sell_StrikeSymbol[-7:] + " <- B -> " + str(CE_Sell_StrikeSymbol_LTP) + "\n" + \
                       PE_Sell_StrikeSymbol[-7:] + " <- B -> " + str(PE_Sell_StrikeSymbol_LTP) + "\n" + \
                       "P&L <--> " + str(dataToWrite['pnl'])

    combinedDataToWrite = dict(list(file.items()) + list(dataToWrite.items()))
    # file = open(file_path, 'w')
    # json.dump(combinedDataToWrite, file)
    # file.close()
    # print('FILE CREATED')
    # file = json.load(open(file_path, 'r'))
    # print(file)

    # requests.post(config['request_url'], data=combinedDataToWrite)

    config["trades_data"] = combinedDataToWrite

    send_telegram_message(telegram_Message)

    return


# def generate_token_test():
#     print("_______________GENERATING TOKEN_________")
#     config["access_token"] = login()
#
#     instruments = pd.read_csv('https://public.fyers.in/sym_details/NSE_FO.csv', header=None)
#     ism = instruments[instruments[13] == '{}'.format('BANKNIFTY')]
#     config["expiry_date_banknifty"] = ism[9].tolist()[0][13:-7]
#
#     config["fyers"] = fyersModel.FyersModel(client_id=config["client_id"], token=config["access_token"],
#                                             log_path="")
#     print(config["access_token"])
#     print("LOGGED IN")
#     execute_trade()

# generate_token_test()

def convert_time_to_utc(timerequest):
    local_timezone = pytz.timezone("Asia/Kolkata")
    # local_dt = datetime.datetime.utcnow().astimezone(local)
    local_time = str(datetime.datetime.now().strftime('%Y-%m-%d ')) + str(timerequest)
    naive = datetime.datetime.strptime(local_time, "%Y-%m-%d %H:%M:%S")
    local_dt = local_timezone.localize(naive)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt.strftime('%H:%M:%S')

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
schedule.every().tuesday.at(convert_time_to_utc("09:15:00")).do(generate_token)
schedule.every().wednesday.at(convert_time_to_utc("09:00:00")).do(generate_token)
schedule.every().thursday.at(convert_time_to_utc("09:00:00")).do(generate_token)
schedule.every().friday.at(convert_time_to_utc("09:00:00")).do(generate_token)
# schedule.every().sunday.at(convert_time_to_utc("09:00:00")).do(generate_token)
# schedule.every().sunday.at(convert_time_to_utc("09:00:00")).do(schedule_trades, execute_trade, '13-55-00')

while True:
    schedule.run_pending()
    time.sleep(60)

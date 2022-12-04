import schedule, time, datetime, requests, json, os
from threading import Timer
import pandas as pd

from fyers_api import fyersModel, accessToken
from autologin import *

session = accessToken.SessionModel(client_id='YUBD35U8OF-100', secret_key='TJFZARII4E',
                                   redirect_uri='https://www.google.co.in', response_type='code',
                                   grant_type='authorization_code')

config = {
    "client_id": "YUBD35U8OF-100",
    "secret_key": "TJFZARII4E",
    "access_token": "",
    "request_url": "https://sm.affility.store"
}


def generate_token():
    config["access_token"] = login()

    instruments = pd.read_csv('https://public.fyers.in/sym_details/NSE_FO.csv', header=None)
    ism = instruments[instruments[13] == '{}'.format('BANKNIFTY')]
    config["expiry_date_banknifty"] = ism[9].tolist()[0][13:-7]

    config["fyers"] = fyersModel.FyersModel(client_id=config["client_id"], token=config["access_token"],
                                            log_path="")
    print("LOGGED IN")
    send_telegram_message("LOGGED IN")
    schedule_trades(execute_trade, '09-20-00')

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
    sellGap = 3
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

    send_telegram_message(telegram_Message)
    schedule_trades(exit_trade, '15-05-00')
    return


def exit_trade(request):
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

def schedule_trades(functionName, timeToExecute):
    currentTime = datetime.datetime.now()
    executionTime = datetime.datetime.now().strftime('%d-%m-%Y') + " " + timeToExecute
    executionTime = datetime.datetime.strptime(executionTime, '%d-%m-%Y %H-%M-%S')
    delay = (executionTime - currentTime).total_seconds()
    if delay >= 0:
        Timer(delay, functionName).start()


schedule.every().monday.at("09:00").do(generate_token)
schedule.every().tuesday.at("09:00").do(generate_token)
schedule.every().wednesday.at("09:00").do(generate_token)
schedule.every().thursday.at("09:00").do(generate_token)
schedule.every().friday.at("09:00").do(generate_token)
# schedule.every().sunday.at("16:58").do(generate_token)
# schedule.every().sunday.at("13:54").do(schedule_trades, execute_trade, '13-55-00')

while True:
    schedule.run_pending()
    time.sleep(60)
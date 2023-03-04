import schedule, time, datetime, requests, json, os, pytz
import threading, sys
from threading import Timer
from fyers_api.Websocket import ws

from config_file import *

algo_config = {
    "strikes_traded": ['x', 'x', 'x'],
    "strikes_ltp": [0, 0, 0],
    "stop_loss": [0, 0, 0],
    "target": 0,
    "sl_side": 0,
    "stop_loss_hit": False,
    "trades_exited": False
}

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


def custom_message(msg):
    # print(f"Custom:{msg}")
    for x in range(2):
        if msg[0]['symbol'] == algo_config['strikes_traded'][x]:
            algo_config['strikes_ltp'][x] = msg[0]['ltp']


    if algo_config['stop_loss_hit'] == False:
        for x in range(2):
            if algo_config['strikes_ltp'][x] >= algo_config['stop_loss'][x]:
                algo_config['stop_loss_hit'] = True

                algo_config['sl_side'] = x
                send_telegram_message('SL:- ' + str(algo_config['strikes_ltp'][x]) + "\n" + algo_config['strikes_traded'][x][-7:])
                # threading.Thread(target=send_telegram_message, args=('SL:- ' + algo_config['strikes_traded'][x])).start()
                # threading.Thread(target=execute_trade(), args=(x)).start()
                threading.Thread(target=execute_trade).start()
                sys.exit()


def run_websocket():
    Access_Token = config["client_id"] + ':' + config["access_token"]
    data_type = "symbolData"
    fs = ws.FyersSocket(access_token=Access_Token, run_background=False, log_path='')
    fs.websocket_data = custom_message
    config['fs'] = fs
    print("CONFIGURATION")
    # fs.subscribe(symbol=config["strikes_traded"], data_type=data_type)
    # fs.keep_running()
    config['websocket_process'] = threading.Thread(target=fs.subscribe, args=(algo_config["strikes_traded"][:-1], data_type,))
    config['websocket_process'].daemon = True
    config['websocket_process'].start()


def custom_message_2(msg):
    algo_config['strikes_ltp'][2] = msg[0]['ltp']


    if algo_config['trades_exited'] == False:
        if algo_config['strikes_ltp'][2] >= algo_config['stop_loss'][2]:
            algo_config['trades_exited'] = True

            send_telegram_message('SL:- ' + str(algo_config['strikes_ltp'][2]))
            # threading.Thread(target=send_telegram_message, args=('SL:- ' + str(algo_config['strikes_ltp'][2]))).start()
            sys.exit()
        if algo_config['strikes_ltp'][2] <= algo_config['target']:
            algo_config['trades_exited'] = True

            send_telegram_message('Target:- ' + str(algo_config['strikes_ltp'][2]))
            # threading.Thread(target=send_telegram_message, args=('Target:- ' + str(algo_config['strikes_ltp'][2]))).start()
            sys.exit()


def run_websocket_2():
    Access_Token = config["client_id"] + ':' + config["access_token"]
    data_type = "symbolData"
    fs = ws.FyersSocket(access_token=Access_Token, run_background=False, log_path='')
    fs.websocket_data = custom_message_2
    config['fs'] = fs
    print("CONFIGURATION_2")
    # fs.subscribe(symbol=config["strikes_traded"], data_type=data_type)
    # fs.keep_running()
    send_telegram_message('WEBSOCKET STARTED')
    config['websocket_process'] = threading.Thread(target=fs.subscribe, args=(algo_config["strikes_traded"][2], data_type,))
    config['websocket_process'].daemon = True
    config['websocket_process'].start()

def execute_trade():
    print("TRADES EXECUTED")
    spotPrice = config["fyers"].quotes({"symbols": "NSE:NIFTYBANK-INDEX"})['d'][0]['v']['lp']
    expiry_date = config["expiry_date_banknifty"]
    spotPrice_Round = round(spotPrice / 100)
    # expiry_date = '22D01'
    buyGap = 15
    sellGap = 0
    CE_Sell_StrikeSymbol = 'NSE:BANKNIFTY' + expiry_date + str((spotPrice_Round + sellGap) * 100) + 'CE'
    PE_Sell_StrikeSymbol = 'NSE:BANKNIFTY' + expiry_date + str((spotPrice_Round - sellGap) * 100) + 'PE'

    # target_strike = ''
    target_strike = PE_Sell_StrikeSymbol if algo_config['sl_side'] == 0 else CE_Sell_StrikeSymbol

    strike_LTP = config["fyers"].quotes({"symbols": target_strike})['d'][0]['v']['lp']

    date = datetime.datetime.now()
    weekday = date.weekday()
    stop_loss_multipliers = [1.2, 1.2, 1.2, 1.2, 1.2, 1.2]
    target_multipliers = [0.75, 0.75, 0.75, 0.75, 0.75, 0.75]
    stop_loss = strike_LTP * stop_loss_multipliers[weekday]
    target = strike_LTP * target_multipliers[weekday]

    algo_config['trades_exited'] = False
    algo_config["stop_loss"][2] = stop_loss
    algo_config["target"] = target
    algo_config["strikes_traded"][2] = target_strike
    algo_config["strikes_ltp"][2] = strike_LTP


    telegram_Message = "Entry\nBANKNIFTY <-> " + str(spotPrice) + "\n" + \
                       target_strike[-7:] + " <- S -> " + str(strike_LTP) + "\n" + \
                       "SL <-> " + str(round(stop_loss, 2)) + "\n" + \
                       "Target <-> " + str(round(target, 2))

    send_telegram_message(telegram_Message)

    run_websocket_2()
    return

def pre_trade():
    print("TRADES EXECUTED")
    spotPrice = config["fyers"].quotes({"symbols": "NSE:NIFTYBANK-INDEX"})['d'][0]['v']['lp']
    expiry_date = config["expiry_date_banknifty"]
    spotPrice_Round = round(spotPrice / 100)
    # expiry_date = '22D01'
    buyGap = 15
    sellGap = 0
    CE_Sell_StrikeSymbol = 'NSE:BANKNIFTY' + expiry_date + str((spotPrice_Round + sellGap) * 100) + 'CE'
    PE_Sell_StrikeSymbol = 'NSE:BANKNIFTY' + expiry_date + str((spotPrice_Round - sellGap) * 100) + 'PE'

    CE_Sell_StrikeSymbol_LTP = config["fyers"].quotes({"symbols": CE_Sell_StrikeSymbol})['d'][0]['v']['lp']
    PE_Sell_StrikeSymbol_LTP = config["fyers"].quotes({"symbols": PE_Sell_StrikeSymbol})['d'][0]['v']['lp']

    date = datetime.datetime.now()
    weekday = date.weekday()
    stop_loss_multipliers = [1.2, 1.2, 1.2, 1.2, 1.2, 1.2]
    stop_loss_CE = CE_Sell_StrikeSymbol_LTP * stop_loss_multipliers[weekday]
    stop_loss_PE = PE_Sell_StrikeSymbol_LTP * stop_loss_multipliers[weekday]

    algo_config['stop_loss_hit'] = False
    algo_config["stop_loss"][0] = stop_loss_CE
    algo_config["stop_loss"][1] = stop_loss_PE
    algo_config["strikes_traded"][0] = CE_Sell_StrikeSymbol
    algo_config["strikes_traded"][1] = PE_Sell_StrikeSymbol
    algo_config["strikes_ltp"][0] = CE_Sell_StrikeSymbol_LTP
    algo_config["strikes_ltp"][1] = PE_Sell_StrikeSymbol_LTP


    telegram_Message = "<----- " + date.strftime("%A") + " ----->" + "\n\n" + \
                       "BANKNIFTY <-> " + str(spotPrice) + "\n" + \
                       CE_Sell_StrikeSymbol[-7:] + " <- S -> " + str(CE_Sell_StrikeSymbol_LTP) + "\n" + \
                       PE_Sell_StrikeSymbol[-7:] + " <- S -> " + str(PE_Sell_StrikeSymbol_LTP) + "\n" + \
                       "SL_CE <-> " + str(round(stop_loss_CE, 2)) + "\n" + \
                       "SL_PE <-> " + str(round(stop_loss_PE, 2))

    send_telegram_message(telegram_Message)

    run_websocket()
    return

def exit_trade():
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
    dataToWrite['pnl'] *= 25

    dataToWrite['strikesLTPExit'].append(CE_Buy_StrikeSymbol_LTP)
    dataToWrite['strikesLTPExit'].append(PE_Buy_StrikeSymbol_LTP)
    dataToWrite['strikesLTPExit'].append(CE_Sell_StrikeSymbol_LTP)
    dataToWrite['strikesLTPExit'].append(PE_Sell_StrikeSymbol_LTP)

    telegram_Message = "Exit\nBANKNIFTY <-> " + str(spotPrice) + "\n" + \
                       CE_Buy_StrikeSymbol[-7:] + " <- S -> " + str(CE_Buy_StrikeSymbol_LTP) + "\n" + \
                       PE_Buy_StrikeSymbol[-7:] + " <- S -> " + str(PE_Buy_StrikeSymbol_LTP) + "\n" + \
                       CE_Sell_StrikeSymbol[-7:] + " <- B -> " + str(CE_Sell_StrikeSymbol_LTP) + "\n" + \
                       PE_Sell_StrikeSymbol[-7:] + " <- B -> " + str(PE_Sell_StrikeSymbol_LTP) + "\n" + \
                       "P&L <--> " + str(round(dataToWrite['pnl'], 2))

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

def start_algo():
    # pre_trade()
    schedule_trades(pre_trade, '09:20:00')
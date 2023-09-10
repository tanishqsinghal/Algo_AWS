import schedule, time, datetime, requests, json, os, pytz
import threading, sys
from threading import Timer
from fyers_api.Websocket import ws

from fyers_api import fyersModel, accessToken
from config_file import *


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
    stocks = ["HDFCBANK","PFC","RECLTD","RELIANCE","TATAPOWER","COALINDIA","SBIN","TATAMOTORS","IRCTC","ICICIBANK","LT","HAL","NTPC","KOTAKBANK","DLF","HAVELLS","AXISBANK","BANDHANBNK","BANKBARODA","IEX","INDUSINDBK","CHOLAFIN","ADANIPORTS","BAJFINANCE","CANBK","GAIL","FEDERALBNK","TATASTEEL","BAJAJFINSV","M&MFIN","INDUSTOWER","TCS","MARUTI","INFY","HINDALCO","POWERGRID","IOC","IDFCFIRSTB","IDEA","ZEEL","SHRIRAMFIN","ADANIENT","ITC","BHARTIARTL","BEL","HCLTECH","CONCOR","RBLBANK","BPCL","ASHOKLEY","HINDPETRO","JSWSTEEL","ICICIPRULI","TECHM","ONGC","PVRINOX","PETRONET","HEROMOTOCO","INDIGO","NMDC","TITAN","CUMMINSIND","HINDUNILVR","M&M","DIXON","IGL","UPL","PERSISTENT","POLYCAB","TATACOMM","BAJAJ-AUTO","GODREJPROP","LICHSGFIN","GLENMARK","BHARATFORG","WIPRO","HDFCAMC","JINDALSTEL","AMBUJACEM","ACC","HDFCLIFE","GMRINFRA","SBILIFE","SUNPHARMA","PEL","AUROPHARMA","GRASIM","VEDL","ULTRACEMCO","CHAMBLFERT","IDFC","AUBANK","OBEROIRLTY","VOLTAS","NATIONALUM","CROMPTON","TRENT","DEEPAKNTR","BRITANNIA","ASIANPAINT","EICHERMOT","SRF","BHEL","APOLLOHOSP","LTIM","CUB","COFORGE","LUPIN","DRREDDY","TATACONSUM","MFSL","DIVISLAB","ESCORTS","CIPLA","PIIND","PAGEIND","INDHOTEL","LAURUSLABS","L&TFH","MCDOWELL-N","DALBHARAT","ABB","SBICARD","TVSMOTOR","AARTIIND","ABCAPITAL","JUBLFOOD","UBL","BSOFT","ASTRAL","GNFC","ABFRL","PNB","SIEMENS","NAUKRI","ZYDUSLIFE","TATACHEM","MCX","EXIDEIND","MPHASIS","LALPATHLAB","TORNTPHARM","BIOCON","LTTS","OFSS","SHREECEM","GUJGASLTD","SUNTV","SYNGENE","GRANULES","RAMCOCEM","BATAINDIA","CANFINHOME","BERGEPAINT","PIDILITIND","MUTHOOTFIN","METROPOLIS","COLPAL","APOLLOTYRE","NESTLEIND","GODREJCP","MOTHERSON","INDIAMART","SAIL","JKCEMENT","MRF","COROMANDEL","NAVINFLUOR","ICICIGI","ATUL","DABUR","MGL","BALKRISIND","BALRAMCHIN","IPCALAB","BOSCHLTD","ALKEM","MARICO","ABBOTINDIA","MANAPPURAM","HINDCOPPER","IBULHSGFIN","INDIACEM","DELTACORP","HDFC"]
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

    # data = {
    #     "symbol": "NSE:SBIN-EQ",
    #     "resolution": "15",
    #     "date_format": "1",
    #     "range_from": "2023-06-01",
    #     "range_to": "2023-09-08",
    #     "cont_flag": "1"
    # }
    #
    # response = config["fyers"].history(data=data)
    # print(response['s'])
    #
    # file = open("test_data.json", 'w')
    # json.dump(response, file)
    # file.close()




def start_algo():
    print("STARTING__________________________________")
    run_scanner(5)
    run_scanner(15)
    schedule.every(5).minutes.do(run_scanner, 5)
    schedule.every(15).minutes.do(run_scanner, 15)

def schedule_algo():
    schedule_trades(start_algo, '10:30:00')

    # timeToExecute = '16:14:00'
    # currentTime = datetime.datetime.now()
    # executionTime = datetime.datetime.now().strftime('%d-%m-%Y') + " " + timeToExecute
    # executionTime = datetime.datetime.strptime(executionTime, '%d-%m-%Y %H:%M:%S')
    # delay = (executionTime - currentTime).total_seconds()
    # # send_telegram_message(str(functionName) + "WITH DELAY " + str(delay) + " SCHEDULED")
    # if delay >= 0:
    #     print(delay)
    #     Timer(delay, start_algo).start()
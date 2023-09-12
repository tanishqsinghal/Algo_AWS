import schedule, time, datetime, requests, json, os, pytz
import threading, sys
from threading import Timer
import algo_simple_straddle
from config_file import *

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

def test_range():
    file = json.load(open("test_data.json", 'r'))
    candles = file["candles"]

    for x in range(len(candles)):
        first_candle_high = candles[x][2]
        first_candle_low = candles[x][3]
        first_candle_range = first_candle_high - first_candle_low
        for y in range(x, len(candles)):
            current_candle_close = candles[y][4]
            if current_candle_close > first_candle_high or current_candle_close < first_candle_low:
                if y-x < 7:
                    break
                else:
                    candle_time = datetime.datetime.fromtimestamp(candles[y][0])
                    print("BREAK FOUND:- ", candle_time)
                    break

def test_nr7():
    file = json.load(open("test_data.json", 'r'))
    candles = file["candles"]
    range_array = []

    for x in range(len(candles)):
        candle_time = datetime.datetime.fromtimestamp(candles[x][0])
        if datetime.time(9, 30, 0) > candle_time.time() > datetime.time(2, 45, 0):
            continue
        current_candle_high = candles[x][2]
        current_candle_low = candles[x][3]
        current_candle_range = current_candle_high - current_candle_low

        if len(range_array) > 6:
            if current_candle_range < min(range_array):
                print("NR7 FOUND:- ", candle_time)
                range_array.clear()
            else:
                range_array.pop(0)
                range_array.append(current_candle_range)
        else:
            range_array.append(current_candle_range)

def test_range_nr7():
    file = json.load(open("test_data.json", 'r'))
    candles = file["candles"]

    total_targets = 0
    total_stoplosses = 0

    for x in range(len(candles)):
        # Proceed ahead if current time is not in the defined range
        candle_time = datetime.datetime.fromtimestamp(candles[x][0])
        if datetime.time(9, 30, 0) > candle_time.time() > datetime.time(2, 45, 0):
            continue

        first_candle_high = candles[x][2]
        first_candle_low = candles[x][3]
        first_candle_range = first_candle_high - first_candle_low

        range_array = []
        is_nr7_found = False
        is_nr7_entry_taken = False
        nr7_candle_number = 0
        nr7_candle_high = 0
        nr7_candle_low = 0
        stop_loss = 0
        target = 0

        for y in range(x, len(candles)):
            candle_time = datetime.datetime.fromtimestamp(candles[y][0])
            current_candle_close = candles[y][4]
            if current_candle_close > first_candle_high or current_candle_close < first_candle_low:
                if y - x < 7:
                    break
                else:
                    # candle_time = datetime.datetime.fromtimestamp(candles[y][0])
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
                            print("NR7 Found:- ", candle_time)
                            is_nr7_found = True
                            nr7_candle_number = y
                            nr7_candle_high = current_candle_high
                            nr7_candle_low = current_candle_low
                            # break
                    else:
                        # if current_candle_close < nr7_candle_low:
                        #     print("NR7 Low Broken:- ", candle_time)
                        #     stop_loss = max(current_candle_high, candles[y - 1][2]) + 0.05
                        #     target = current_candle_close - (stop_loss - current_candle_close) * 1.2
                        #     stop_loss = round(stop_loss, 2)
                        #     target = round(target, 2)
                        #     is_nr7_entry_taken = True
                        #     print("SL:- ", stop_loss)
                        #     print("Target:-", target)
                        #     break
                        if current_candle_close > nr7_candle_high:
                            print("NR7 High Broken:- ", candle_time)
                            stop_loss = min(current_candle_low, candles[y - 1][3]) - 0.05
                            target = current_candle_close + (current_candle_close - stop_loss) * 1.2
                            stop_loss = round(stop_loss, 2)
                            target = round(target, 2)
                            is_nr7_entry_taken = True
                            print("SL:- ", stop_loss)
                            print("Target:-", target)
                            break
                else:
                    range_array.append(current_candle_range)

        if is_nr7_entry_taken:
            for z in range(nr7_candle_number, len(candles)):
                if candles[z][2] >= target:
                    print("Target Found")
                    total_targets += 1
                    break
                elif candles[z][3] <= stop_loss:
                    print("SL HIT")
                    total_stoplosses += 1
                    break
    print("TOTAL TARGETS:-> ", total_targets)
    print("TOTAL STOPS:-> ", total_stoplosses)

def check_range_nr7():
    file = json.load(open("test_data.json", 'r'))
    candles = file["candles"]

    for x in range(len(candles)):
        # Proceed ahead if current time is not in the defined range
        candle_time = datetime.datetime.fromtimestamp(candles[x][0])
        if datetime.time(9, 30, 0) > candle_time.time() > datetime.time(2, 45, 0):
            continue

        first_candle_high = candles[x][2]
        first_candle_low = candles[x][3]
        first_candle_range = first_candle_high - first_candle_low

        range_array = []
        is_nr7_found = False

        for y in range(x, len(candles)):
            candle_time = datetime.datetime.fromtimestamp(candles[y][0])
            current_candle_close = candles[y][4]
            if current_candle_close > first_candle_high or current_candle_close < first_candle_low:
                if y - x < 7:
                    break
                else:
                    candle_time = datetime.datetime.fromtimestamp(candles[y][0])
                    print("BREAK FOUND:- ", candle_time)
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
                            print("NR7 Found:- ", candle_time)
                            is_nr7_found = True
                            nr7_candle_number = y
                            nr7_candle_high = current_candle_high
                            nr7_candle_low = current_candle_low
                            # break
                else:
                    range_array.append(current_candle_range)

# check_range_nr7()

def test_fun():
    # print(datetime.datetime.fromtimestamp(candles[x][0]).time())
    print(datetime.datetime.now().time())

test_fun()

# schedule.every().monday.at(convert_time_to_utc("09:00:00")).do(test)
# schedule.every().tuesday.at(convert_time_to_utc("09:00:00")).do(test)
# schedule.every().wednesday.at(convert_time_to_utc("09:00:00")).do(test)
# schedule.every().thursday.at(convert_time_to_utc("09:00:00")).do(test)
# schedule.every().friday.at(convert_time_to_utc("09:00:00")).do(test)
# schedule.every().saturday.at("10:22:00").do(test)
#
# while True:
#     schedule.run_pending()
#     time.sleep(60)
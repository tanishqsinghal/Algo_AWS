import schedule, time, datetime, requests, json, os, pytz
import threading, sys
from threading import Timer
import algo_simple_straddle

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

def test():
    print("SCHEDULED")
    algo_simple_straddle.execute_trade()
    # schedule_trades(algo_simple_straddle.execute_trade, '10:23:00')


test()


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
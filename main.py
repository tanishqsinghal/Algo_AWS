import schedule, time, datetime, requests
from threading import Timer

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


# nextDay = datetime.datetime.now() + datetime.timedelta(days=1)
# dateString = datetime.datetime.now().strftime('%d-%m-%Y') + " 11-25-00"
# newDate = nextDay.strptime(dateString,'%d-%m-%Y %H-%M-%S')

currentTime = datetime.datetime.now()
executionTime = datetime.datetime.now().strftime('%d-%m-%Y') + " 12-50-00"
executionTime = datetime.datetime.strptime(executionTime, '%d-%m-%Y %H-%M-%S')
delay = (executionTime - currentTime).total_seconds()
print(delay)
Timer(10.0, send_telegram_message, [str(datetime.datetime.now())]).start()
Timer(30.0, send_telegram_message, [str(datetime.datetime.now())]).start()
Timer(delay, send_telegram_message, [str(datetime.datetime.now())]).start()

# def job():
#     print("I am doing this job!")
#
#
# schedule.every().monday.at("14:00").do(job)
# schedule.every().tuesday.at("14:00").do(job)
# schedule.every().wednesday.at("14:00").do(job)
# schedule.every().thursday.at("14:00").do(job)
# schedule.every().friday.at("14:00").do(job)
# schedule.every().sunday.at("11:18").do(job)
#
# while True:
#     schedule.run_pending()
#     print("RUNNING")
#     time.sleep(1)
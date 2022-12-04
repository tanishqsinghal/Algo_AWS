import schedule, time, datetime
from threading import Timer


def my_job():
    print ("hello world")
nextDay = datetime.datetime.now() + datetime.timedelta(days=1)
dateString = datetime.datetime.now().strftime('%d-%m-%Y') + " 11-25-00"
newDate = nextDay.strptime(dateString,'%d-%m-%Y %H-%M-%S')
delay = (newDate - datetime.datetime.now()).total_seconds()
print(delay)
# Timer(str(delay),my_job,()).start()
t = Timer(10.0, my_job)
t.start()

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
import requests, pytz, datetime

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
    "trades_exited": False,
    "message_to_send": ""
}

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


def convert_time_to_utc(timerequest):
    local_timezone = pytz.timezone("Asia/Kolkata")
    # local_dt = datetime.datetime.utcnow().astimezone(local)
    local_time = str(datetime.datetime.now().strftime('%Y-%m-%d ')) + str(timerequest)
    naive = datetime.datetime.strptime(local_time, "%Y-%m-%d %H:%M:%S")
    local_dt = local_timezone.localize(naive)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt.strftime('%H:%M:%S')
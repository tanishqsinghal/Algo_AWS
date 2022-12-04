import requests
import configparser
from urllib.parse import urlparse, parse_qs

from fyers_api import fyersModel, accessToken


config = configparser.ConfigParser()
config.read('config.ini')
client_id = config['fyers']['app_id']
app_id = client_id[:-4]
secret_key = config['fyers']['app_secret']
redirect_uri = config['fyers']['redirect_url']
username = config['fyers']['user_id']
password = config['fyers']['password']
pan = config['fyers']['pan']
pin = int(config['fyers']['two_fa'])


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

# try:
#
#     with open("access_token.csv", "a") as fyers_token:
#
#         fyers_token.write(str(client_id) + "," + str(token))
#
#         print("Wrote ---->", str(client_id) + "," + str(token))
#
#         fyers_token.write("\n")
#
#         fyers_token.close()
#
#     print("Access token generated successfully")
#
# except:
#
#     print("Some went wrong Credentials or Network Connetivity")









# import pyotp, datetime
# from fyers_api import accessToken
# import configparser
# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from time import sleep
# import urllib.parse as urlparse
#
#
# # get all required credentials from config.ini file
#
# config = configparser.ConfigParser()
# config.read('config.ini')
# app_id = config['fyers']['app_id']
# app_secret = config['fyers']['app_secret']
# redirect_url = config['fyers']['redirect_url']
# user_id = config['fyers']['user_id']
# password = config['fyers']['password']
# two_fa = config['fyers']['two_fa']
#
#
# # generate the session url
# session=accessToken.SessionModel(client_id=app_id,
#                                     secret_key= app_secret,
#                                     redirect_uri= redirect_url,
#                                     response_type='code',
#                                     grant_type='authorization_code')
# session_url =  session.generate_authcode()
#
# # to automate the login procedure, I have used selenium webdriver
# # launch firefox  driver
# options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
# driver = webdriver.Firefox(executable_path=r'geckodriver.exe', options=options)
# driver.get(session_url)
#
#
# # initiate longin
#
# xpath = ["//*[@id='fy_client_id']", "//*[@id='fy_client_pwd']"]
# keys = [user_id, password]
#
# for i in range(2):
#     driver.find_element(by= By.XPATH, value= xpath[i]).send_keys(keys[i])
#     sleep(1)
#     driver.find_element(by= By.XPATH, value= xpath[i]).submit()
#     sleep(1)
#
# for i in range(4):
#     digit = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/section[8]/div[3]/div[3]/form/div[2]/input[{}]".format(i+1))))
#     digit.send_keys(two_fa[i])
#     sleep(0.1)
#
# submit = WebDriverWait(driver, 20).until(lambda x: x.find_element(By.XPATH,"//*[@id='verifyPinSubmit']"))
# submit.click()
# sleep(2)
#
# # login successful
# # get the authorization code
#
# current_url = driver.current_url
# driver.close()
# parsed = urlparse.urlparse(current_url)
# auth_code = urlparse.parse_qs(parsed.query)['auth_code'][0]
#
# print(auth_code)







# form = WebDriverWait(driver, 10).until(
#
#             EC.visibility_of_element_located((By.ID, 'confirmOtpForm')))
#
# totp = pyotp.TOTP("HLROG5N5T4DQ32V232ICMWG5XQV5LTYQ")
#
# token = totp.now()
#
# digits = [d for d in token]
#
# time_remaining = totp.interval - datetime.datetime.now().timestamp() % totp.interval
#
# print(F"Time Remaining is {time_remaining}")
#
#
# if time_remaining <= 8:
#
#     print("Sleeping for some time as time remaining is less than 8")
#
#     sleep(time_remaining)
#
#     token = totp.now()
#
#     digits = [d for d in token]
#
#
# driver.find_element(By.XPATH, "//form[@id='confirmOtpForm']").find_element(By.ID, "first").send_keys(digits[0])
#
# driver.find_element(By.XPATH, "//form[@id='confirmOtpForm']").find_element(By.ID, "second").send_keys(
#
#     digits[1])
#
# driver.find_element(By.XPATH, "//form[@id='confirmOtpForm']").find_element(By.ID, "third").send_keys(digits[2])
#
# driver.find_element(By.XPATH, "//form[@id='confirmOtpForm']").find_element(By.ID, "fourth").send_keys(
#
#     digits[3])
#
# driver.find_element(By.XPATH, "//form[@id='confirmOtpForm']").find_element(By.ID, "fifth").send_keys(
#
#     digits[4])
#
# driver.find_element(By.XPATH, "//form[@id='confirmOtpForm']").find_element(By.ID, "sixth").send_keys(
#
#     digits[5])
#
# sleep(1)
#
# driver.find_element(By.ID, "confirmOtpSubmit").click()

# logging.info("Entered the TOTP Details")
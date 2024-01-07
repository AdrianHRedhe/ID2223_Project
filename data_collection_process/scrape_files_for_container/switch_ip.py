import mybrowser
import time
import requests
from datetime import datetime 

# Set the encoding for stdout to UTF-8
#sys.setdefaultencoding('utf-8')

start_time = datetime.now()
response = requests.get('http://icanhazip.com/', proxies={'http': '127.0.0.1:8118'})
print(response.text.strip(), datetime.now()-start_time)
print()

mybrowser.MyBrowserClass.set_new_ip()
time.sleep(2)

response = requests.get('http://icanhazip.com/', proxies={'http': '127.0.0.1:8118'})
print(response.text.strip(), datetime.now()-start_time)

from selenium import webdriver
#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
#from fake_useragent import UserAgent
#from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from stem import Signal
from stem.control import Controller

class MyBrowserClass:
    def start_browser():
        driver_path = "./geckodriver"

        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy.http_proxy = 'localhost:8118'
        proxy.ssl_proxy = 'localhost:8118'

        capabilities = webdriver.DesiredCapabilities.FIREFOX
        proxy.add_to_capabilities(capabilities)

        profile = FirefoxProfile()
        profile.set_preference("intl.accept_languages", "en_GB")
        
        options = Options()
        options.add_argument('--proxy_server=http://127.0.0.1:8118')
        options.add_argument('--headless')
        options.profile = profile
        print("Options:", options.arguments)

        browser = webdriver.Firefox(executable_path=driver_path, options=options, desired_capabilities=capabilities)

        return browser

    def set_new_ip():
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password="my password") 
            controller.signal(Signal.NEWNYM)

def restart_browser(MyBrowserClass,previous_driver):
    previous_driver.quit()
    return MyBrowserClass.start_browser()


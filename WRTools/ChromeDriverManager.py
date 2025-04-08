import undetected_chromedriver as uc
from undetected_chromedriver import ChromeOptions
from Manager import AccManage
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver import FirefoxOptions
import pickle


def getWebDriver(index):
    mac_arr = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:107.0) Gecko/20100101 Firefox/107.0',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0',
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
               ]

    windows_arr = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
                   ]
    if AccManage.Device_ID == 'Mac' or AccManage.Device_ID == 'AIR':
        user_agent = mac_arr[index]
    else:
        user_agent = windows_arr[index]
    options = ChromeOptions()
    options.add_argument(f"--user-agent={user_agent}")
    if AccManage.chromedriver_path.__len__() > 0:
        driver = uc.Chrome(use_subprocess=True, driver_executable_path=AccManage.chromedriver_path, options=options) #todo chromedriverPath
    else:
        driver = uc.Chrome(use_subprocess=True, options=options)
        driver.set_window_size(height=900, width=1400)
    cookies = driver.get_cookies()
    with open('cookies.pkl', 'wb') as file:
        pickle.dump(cookies, file)

        # 加载 cookies
    with open('cookies.pkl', 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    return driver


def get_firfox_driver():
    option = FirefoxOptions()
    # option.add_argument("--headless")  # 隐藏浏览器
    browser = Firefox(executable_path='/usr/local/bin/geckodriver', options=option)
    return browser
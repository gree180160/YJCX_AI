from selenium.webdriver import Firefox
from selenium.webdriver import FirefoxOptions
import time

option = FirefoxOptions()
# option.add_argument("--headless")  # 隐藏浏览器

browser=Firefox(executable_path='/usr/local/bin/geckodriver', options=option)
url = "https://octopart.com/"
browser.get(url)
time.sleep(5)
print(browser)

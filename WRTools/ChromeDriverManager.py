import undetected_chromedriver as uc
from undetected_chromedriver import ChromeOptions
from Manager import AccManage

def getWebDriver(index):

    mac_arr = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
           'Chrome 80.0 on macOS 10.15: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
           'Chrome 85.0 on macOS 10.15: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
           'Chrome 90.0 on macOS 11.0: Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
           'Chrome 95.0 on macOS 12.0: Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
           'Safari 12.0 on macOS 10.14: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
           'Firefox 75.0 on macOS 10.13: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:75.0) Gecko/20100101 Firefox/75.0'
               ]
    windows_arr = ['Chrome 88.0 on Windows 10: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
                   'Chrome 90.0 on Windows 10: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
                   'Chrome 91.0 on Windows 8.1: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Chrome 94.0 on Windows 8: Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
                   'Firefox 85.0 on Windows 7: Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
                   'Edge 89.0 on Windows 8.1: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 Edg/89.0.774.54',
                   ]
    if AccManage.Device_ID == 'Mac':
        user_agent = mac_arr[index]
    else:
        user_agent = windows_arr[index]
    options = ChromeOptions()
    options.add_argument(f"--user-agent={user_agent}")
    if AccManage.chromedriver_path.__len__() > 0:
        driver = uc.Chrome(use_subprocess=True, driver_executable_path=AccManage.chromedriver_path, options=options) #todo chromedriverPath
    else:
        driver = uc.Chrome(use_subprocess=True, options=options)
        driver.set_window_size(height=800, width=1200)
    return driver
import random
import re

import requests
from WRTools import ExcelHelp, UserAgentHelper
import undetected_chromedriver as uc
from selenium import webdriver
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

ip_file = '/Users/liuhe/PycharmProjects/SeleniumDemo/WRTools/IP&UA.xlsx'
ip_sheet = 'IP'

ip_arr_city = ExcelHelp.read_col_content(file_name=ip_file, sheet_name=ip_sheet, col_index=1)[622:634]

ip_arr_country = ExcelHelp.read_col_content(file_name=ip_file, sheet_name=ip_sheet, col_index=1)[0:684]
ip_arr_country1 = ExcelHelp.read_col_content(file_name=ip_file, sheet_name=ip_sheet, col_index=1)[0:171]
ip_arr_country2 = ExcelHelp.read_col_content(file_name=ip_file, sheet_name=ip_sheet, col_index=1)[171:171*2]
ip_arr_country3 = ExcelHelp.read_col_content(file_name=ip_file, sheet_name=ip_sheet, col_index=1)[171*2:171*3]
ip_arr_country4 = ExcelHelp.read_col_content(file_name=ip_file, sheet_name=ip_sheet, col_index=1)[171*3:]


# same city
def getRandowCityIP():
    return random.choice(ip_arr_city)


# same city
def getRandowCityProxy():
    {'http:': f"http://{getRandowCityIP()}"}


# country
def getRandowIP_country():
    return random.choice(ip_arr_country)


def getRandowIP_country1():
    return random.choice(ip_arr_country1)


def getRandowIP_country2():
    return random.choice(ip_arr_country2)


def getRandowIP_country3():
    return random.choice(ip_arr_country3)


def getRandowIP_country4():
    return random.choice(ip_arr_country4)


def getRandowProxy_contry():
    {'http:': f"http://{getRandowIP_country()}"}


def getRandowProxy_contry1():
    {'http:': f"http://{getRandowIP_country1()}"}


def getRandowProxy_contry2():
    {'http:': f"http://{getRandowIP_country2()}"}


def getRandowProxy_contry3():
    {'http:': f"http://{getRandowIP_country3()}"}


def getRandowProxy_contry4():
    {'http:': f"http://{getRandowIP_country4()}"}


def check_proxy():
    url = "http://httpbin.org/ip"
    randow_ip = getRandowCityProxy()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}
    try:
        resp = requests.get(url, headers=headers, proxies=randow_ip, timeout=10)
        print(resp.text)
    except Exception as e:
        print(f"{randow_ip} 请求失败，代理IP无效！{e}")


def check_all(ip_arr):
    url = "http://httpbin.org/ip"
    ip_list = ['154.236.179.233:1976', '103.146.197.91:8181', '102.68.128.218:8080']
    for ip in ip_list:
        ip_string = ip.replace(' ', '')
        proxies = {
            'http': 'http://' + ip_string,
            'https': 'http://' + ip_string
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko)Version / 5.1 Safari / 534.50'
        }
        try:
            req = requests.get(url=url, headers=headers, proxies=proxies, timeout=25)
            print(f"{ip} OK")
        except Exception as e:
            print(f"{ip} Fail {e}")


def check_ip():
    ip_arr = ExcelHelp.read_col_content(file_name='/Users/liuhe/PycharmProjects/SeleniumDemo/WRTools/IP&UA.xlsx', sheet_name="IP", col_index=1)
    ip_arr = ['103.145.151.130:8080', '35.188.141.76:3128', '112.14.40.137:9091'] # ip_arr
    for ip in ip_arr:
        randow_ip = {'http:': f"http://{ip}"}
        driver_option = webdriver.ChromeOptions()
        # driver_option.add_argument('--headless')
        driver_option.add_argument(f'--proxy-server=http://112.132.123.176:8080')
        driver_option.add_argument("–incognito")
        #  等待初始HTML文档完全加载和解析，
        driver_option.page_load_strategy = 'eager'
        driver_option.add_argument(f'user-agent="{UserAgentHelper.getRandowUA()}"')
        # 优化图片显示
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # driver_option.add_experimental_option('prefs', prefs)
        driver = uc.Chrome(use_subprocess=True, options=driver_option)
        driver.set_page_load_timeout(10)
        url = "http://httpbin.org/ip"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}
        try:
            driver.get("https://www.ip138.com/")
            print(f'{ip} , ok')
        except Exception as e:
            print(f"{ip} , fail")


def pinyi_test():
    # 提取ip
    resp = requests.get("http://tiqu.pyhttp.taolop.com/getflowip?count=1&neek=42357&type=1&sep=0&sb=0&ip_si=1&mr=0")
    ip = resp.text
    print(f'ip is : {ip}')
    if re.match(r'(?:(?:25[0-5]|2[0-4]\d|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)', ip) is None:
        exit("IP 不正确")

    ip_arr = ip.split(":")
    # 请求地址
    targetUrl = "https://www.ip138.com/"
    # 代理服务器
    proxyHost = ip_arr[0]
    proxyPort = ip_arr[1]
    proxyMeta = "http://%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
    }

    proxies = {

        "http": proxyMeta,
        "https": proxyMeta
    }
    resp = requests.get(targetUrl, proxies=proxies)
    resp.encoding = 'utf-8'
    print(resp.status_code)
    print(resp.text)


if __name__ == '__main__':
    ip_arr = ExcelHelp.read_col_content(file_name='/Users/liuhe/PycharmProjects/SeleniumDemo/WRTools/IP&UA.xlsx',
                                        sheet_name="IP", col_index=1)
    # check_all(ip_arr)
    # check_ip()
    pinyi_test()
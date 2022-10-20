# 青果网络
import base64
import time
import requests
from requests.adapters import HTTPAdapter
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from WRTools import UserAgentHelper
import json
from sys import platform

auth_key = "7E689398"  # 隧道代理的AuthKey
password = "1B5ECE52E079"  # 隧道代理的AuthPwd
tunnel_server = "http://tunnel5.qg.net:18716"  # 隧道代理的地址
target_url = "https://d.qg.net/ip"  # 要访问的目标地址
proxy_headers = {}
proxy = {
    "http": tunnel_server,
    "https": tunnel_server
}
last_IP = '116.7.96.149'


def encode_authorization(key, passwd):
    # python 使用 bytes 类型进行 base64 编码
    basic_str = bytes("%s:%s" % (key, passwd), "ascii")
    # 得到的返回值也是 bytes 类型，所以需要再 decode 为字符串
    return "Basic %s" % base64.b64encode(basic_str).decode("utf-8")


def reset_tunnel_proxy_headers():
    global proxy_headers
    proxy_headers = {
        tunnel_server: {
            "Proxy-Authorization": encode_authorization(auth_key, password)
        }
    }


def update_tunnel_proxy_headers(key, val):
    global proxy_headers
    proxy_headers[tunnel_server][key] = val


def new_session():
    adapter = TunnelProxyAdapter()
    se = requests.Session()
    se.mount('https://', adapter)
    se.mount('http://', adapter)
    return se


class TunnelProxyAdapter(requests.adapters.HTTPAdapter):
    def proxy_headers(self, p):
        if p in proxy_headers:
            # print("session with headers:", proxy_headers[p])
            return proxy_headers[p]
        else:
            return None


def normal_tunnel():
    """
    结果类似:
    request on normal mode
    session with headers: {'Proxy-Authorization': 'Basic xxxx'}
    request id: 1, code: 200, result: 140.250.149.229
    """
    # reset_tunnel_proxy_headers()
    print("request on normal mode")
    resp = new_session().get("https://octopart.com/search?q=PIC18F&currency=USD&specs=0", proxies=proxy, headers = {'User-Agent': UserAgentHelper.getRandowUA()})
    resp.encoding = 'utf-8'
    print("request id: 1, code: %s, result: %s" % (resp.status_code, resp.text))


def mark_tunnel():
    reset_tunnel_proxy_headers()
    update_tunnel_proxy_headers("Proxy-TunnelID", "channel-1")
    update_tunnel_proxy_headers("Proxy-TTL", 10)
    se = new_session()
    print("request with mark")
    for i in range(1, 3):
        resp = se.get(target_url, proxies=proxy, headers={"Connection": "close"}, verify=False)
        print("request id: %-2s, code: %s, result: %s" % (i, resp.status_code, resp.text))
        time.sleep(1)


def multi_channel_tunnel():
    print("request on multi channel")
    # reset_tunnel_proxy_headers()
    for i in range(1, 12):
        se = new_session()
        chan_id = "channel-%s" % i
        # update_tunnel_proxy_headers("Proxy-TunnelID", chan_id)
        try:
            resp = se.get("https://octopart.com/search?q=PIC18F&currency=USD&specs=0", proxies=proxy,
                          headers={'User-Agent': UserAgentHelper.getRandowUA(), "Connection": "close"})
        # resp = se.get("http://httpbin.org/ip", proxies=proxy, headers={"Connection": "close"})
        except:
            print('proxy error')
        resp.encoding = 'utf-8'
        print("request id: %-2s, channel id: %s, code: %s" % (i, chan_id, resp.status_code))
        # print("request id: %-2s, channel id: %s, code: %s, result: %s" % (i, chan_id, resp.status_code, resp.text))
        time.sleep(5)
    # time.sleep(10)
    # 因为固定时长为1分钟，所以在1分钟内继续使用已有通道，仍是之前的IP
    # for i in range(1, 11):
    #     se = new_session()
    #     chan_id = "channel-%s" % i
    #     update_tunnel_proxy_headers("Proxy-TunnelID", chan_id)
    #     resp = se.get(target_url, proxies=proxy, headers={"Connection": "close"})
    #     print("request id: %-2s, channel id: %s, code: %s, result: %s" % (i, chan_id, resp.status_code, resp.text))


def testXX():
    target_url = "http://httpbin.org/ip"
    proxy_host = 'http-dynamic.xiaoxiangdaili.com'
    proxy_port = 10030
    proxy_username = '890185094781095936'
    proxy_pwd = 'QREpQEcL'
    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxy_host,
        "port": proxy_port,
        "user": proxy_username,
        "pass": proxy_pwd,
    }
    proxies = {
        'http': proxyMeta,
        'https': proxyMeta,
    }
    headers = {'User-Agent': UserAgentHelper.getRandowUA()}
    try:
        headers = {'User-Agent': UserAgentHelper.getRandowUA()}
        resp = requests.get(url="https://www.baidu.com/index.php?tn=monline_3_dg", proxies=proxies, headers=headers)
        resp.encoding = 'utf-8'
        print(resp.text)
    except Exception as e:
        print(f'exception: {e}')


def getMyIP() -> str:
    url = 'http://httpbin.org/ip'
    response = requests.get(url=url)
    result = json.loads(response.text)['origin']
    return result


def getAddIPList() -> list:
    url = 'https://proxy.qg.net/whitelist/query?Key=A89F5917'
    response = requests.get(url=url)
    dic = json.loads(response.text)
    result = dic['Data']
    return result


def addIP(newIP) -> bool:
    url = f'https://proxy.qg.net/whitelist/add?Key=A89F5917&IP={newIP}'
    response = requests.post(url=url)
    dic = json.loads(response.text)
    result = (dic['Code'] == 0)
    return result


def maintainWhiteList() -> bool:
    global last_IP
    result = False
    newIP = getMyIP()
    if newIP != last_IP:
        addedIP_list = getAddIPList()
        if newIP not in addedIP_list:
            result = addIP(newIP)
    if result:
        last_IP = newIP
    return result


#  自动化测试Selenium+chrome连接代理ip（账密模式）
'''
import requests
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import string
import zipfile
import time

targetURL = "http://d.qg.net/ip"  # "https://www.ip138.com/" #访问的目标站点
proxyHost = "http://tunnel3.qg.net" #代理IP地址
proxyPort = "11144" #代理IP端口号
authKey = "011A80DC" #代理IP的AuthKey
password = "60D66B7F0ACC" #代理IP的AuthPwd

def create_proxy_auth_extension(proxy_host, proxy_port, proxy_username, proxy_password, scheme='http', plugin_path=None):
    """代理认证插件

    args:
        proxy_host (str): 你的代理地址或者域名（str类型）
        proxy_port (int): 代理端口号（int类型）
        # 用户名密码认证(私密代理/独享代理)
        proxy_username (str):用户名（字符串）
        proxy_password (str): 密码 （字符串）
    kwargs:
        scheme (str): 代理方式 默认http
        plugin_path (str): 扩展的绝对路径

    return str -> plugin_path
    """

    if plugin_path is None:
        plugin_path = 'vimm_chrome_proxyauth_plugin.zip'

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
        """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                },
                bypassList: ["foobar.com"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_path


def test_selenium():
    # browser_location = r".\Chrome\chrome.exe" #指定浏览器路径位置
    # driver_location = r".\Chrome\chromedriver.exe" #指定Driver路径位置
    proxy_auth_plugin_path = create_proxy_auth_extension(
        proxy_host=proxyHost,
        proxy_port=proxyPort,
        proxy_username=authKey,
        proxy_password=password)
    option = webdriver.ChromeOptions()
    # option.binary_location = browser_location #设置浏览器位置
    option.add_argument("--start-maximized") #窗口最大化运行
    option.add_extension(proxy_auth_plugin_path) #添加proxy插件

    driver = uc.Chrome(options=option)  #
    driver.get(targetURL)
    time.sleep(10)
    print(driver.page_source)


'''

if __name__ == "__main__":
    # normal_tunnel()
    # mark_tunnel()
    # multi_channel_tunnel()
    # for i in range(1,5):
    #     time.sleep(2)
    #     testXX()
    # getMyIP()
    maintainWhiteList()
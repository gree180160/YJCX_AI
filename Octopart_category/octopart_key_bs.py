# beautifusoup 根据关键字查找P/N, manu
import ssl
import string
import time
import threading
from bs4 import BeautifulSoup
import requests
from WRTools import IPHelper, UserAgentHelper, LogHelper, WaitHelp, QGHelp, EmailHelper, ExcelHelp
from IC_stock import IC_stock_excel_read, IC_Stock_excel_write

import json

ssl._create_default_https_context = ssl._create_unverified_context
default_url = 'https://octopart.com/'
keyword_source_file = '//TKeywords.xlsx'
log_file = '//Octopart_category/octopart_key_cate_log.txt'
cookies = {'__insp_norec_sesstrue':'true',
           '__insp_nvtrue':'true',
           '_pxhd':'i06js1ixb-jfqH0l1dRNSfXXJjjqmmB4m2-9q8e33PQ4JCNy5Jb4oVFGim3/rhAjpiQMGLgLuvN3J0qVTcJQnQ==:7ezmrvu/9WaQ4RP661-hFMhaW99W2Tt-YP4yp22ruHsC5uZE/sUbMMcjjw5gn5qre98SbyNxizO8yon/0GsSTPTMJ7KRt7X5cVwnp-TW0Ao=',
           'ajs_anonymous_id':'%2205799ecd-b973-454d-9553-156b8fb51b8b%22'
            }
# headers = {'User-Agent': UserAgentHelper.getRandowUA(),
#            'cache-control':'no-cache',
#             'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
#             'Content-Type': 'text/html; charset=utf-8',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#             'upgrade-insecure-requests': '1',
#             'Connection': 'keep-alive'}
headers = {}

totol_page = 1
current_page = 1
# 出现安全验证的次数，连续三次则关闭webdriver
security_times = 0


# 验证是否处于验证IP 页面
def is_security_check(soup) -> bool:
    global security_times
    result = False
    try:
        alert = soup.select('div.inner.narrow')
        if alert and len(alert) > 0:
            result = True
            security_times += 1
            EmailHelper.mail_ip_error("mac")
            # QGHelp.maintainWhiteList()
            time.sleep(60)
    except:
        result = False
        security_times = 0
    return result


# 获取总页数
def set_totalpage(soup):
    global totol_page
    try:
        ul = soup.select('ul.jsx-4126298714.jumps')[0]
        li_last = ul.select('li.jsx-4126298714')[-1]
        a = li_last.select('a')[0]
        totol_page = a.text
    except:
        totol_page = 1


# 确定根据key 是否有匹配的结果，避开建议性的结果
def has_content(soup) -> bool:
    result = True
    try:
        no_result = soup.select('div.jsx-1140710980.no-results-found')
        if no_result and len(no_result) > 0:
            result = False
    except:
        result = True
    return result


def get_category(key_index, key_name,manu_ids):
    global headers
    global current_page
    headers['User-Agent'] = UserAgentHelper.getRandowUA()
    headers['Connection'] = "close"
    QGHelp.reset_tunnel_proxy_headers()
    while current_page <= totol_page:
        print(f'key_index is: {key_index} key_name is: {key_name} page is: {current_page}, toalpage is:{totol_page}')
        url = get_url(key_name=key_name, page=current_page, manu_ids=manu_ids)
        try:
            se = QGHelp.new_session()
            QGHelp.update_tunnel_proxy_headers("Proxy-TunnelID", key_name)
            respond = se.get(url, proxies=QGHelp.proxy, headers=headers)
            WaitHelp.waitfor(True, isDebug=False)  # todo test
            respond.encoding = 'utf-8'
            current_page = 1
        except Exception as e:
            LogHelper.write_log(log_file, f'{key_name} request get exception: {e}')
            current_page += 1
            return
        # print(f'respond is :{req.text}')
        soup = BeautifulSoup(respond.text, 'lxml')
        if is_security_check(soup):
            LogHelper.write_log(log_file_name=log_file, content=f'{key_name} ip security check')
            current_page += 1
            print("is_security_check")
            break
        if not has_content(soup=soup):
            current_page += 1
            break
        set_totalpage(soup)
        analyth_html(key_name=key_name, soup=soup)
        current_page += 1


# 解析html，获取cate，manu
def analyth_html(key_name, soup):
    try:
        table = soup.select('div.jsx-2172888034.prices-view')[0]
        cate_first = table.select('div.jsx-2172888034')
        cate_left = table.select('div.jsx-2400378105.part')
        cates_all = cate_first + cate_left
        info_list = []
        for temp_cate in cates_all:
            header = temp_cate.select('div.jsx-3355510592.header')[0]
            try:
                manu = header.select('div.jsx-312275976.jsx-2649123136.manufacturer-name-and-possible-tooltip')[0].text
            except:
                manu = None
            try:
                cate_name = header.select('div.jsx-312275976.jsx-2649123136.mpn')[0].text
            except:
                cate_name = None
            if cate_name and manu:
                if cate_name.startswith(key_name):
                    info_list.append([cate_name, manu, key_name, current_page])
        if len(info_list) > 0:
            IC_Stock_excel_write.add_arr_to_sheet(file_name=f'{key_name}.xlsx', sheet_name='all', dim_arr=info_list)
    except Exception as e:
        LogHelper.write_log(log_file, f'{key_name} analyth_html exception: {e}')


def main():
    key_list = IC_stock_excel_read.get_cate_name_arr(file_name=keyword_source_file, sheet_name='all', col_index=2)
    manuid_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='all', col_index=3)
    for (key_index, key_name) in enumerate(key_list):
        if security_times > 3:
            return
        if key_index % 6 == 0 or key_index % 6 == 1:
            if security_times > 3:
                return
            get_category(key_index=key_index, key_name=key_name, manu_ids=str(manuid_list[key_index]))


if __name__ == "__main__":
    main()


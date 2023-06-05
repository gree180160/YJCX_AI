# beautifusoup 根据关键字查找P/N, manu
import ssl
import string
import time
import threading
from bs4 import BeautifulSoup
import requests
from WRTools import IPHelper, UserAgentHelper, LogHelper, WaitHelp, EmailHelper, ExcelHelp, PathHelp
from Manager import URLManager

import json

ssl._create_default_https_context = ssl._create_unverified_context
default_url = 'https://octopart.com/'

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TNXP.xlsx'),
                  'sourceSheet': 'opn',
                  'colIndex': 1,
                  'startIndex': 1720,
                  'endIndex': 2500}
result_save_file = PathHelp.get_file_path(None, 'TNXP.xlsx')

log_file = PathHelp.get_file_path('Octopart_category', 'octopart_key_cate_log.txt')

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
        a = li_lawww.select('a')[0]
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
    # headers['User-Agent'] = UserAgentHelper.getRandowUA()
    # headers['Connection'] = "close"
    while current_page <= totol_page:
        print(f'key_index is: {key_index} key_name is: {key_name} page is: {current_page}, toalpage is:{totol_page}')
        url = URLManager.octopart_get_page_url(key_name=key_name, page=1, manu=URLManager.Octopart_manu.NXP)
        try:
            respond = requests.get(url)
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
        print('')
    except Exception as e:
        LogHelper.write_log(log_file, f'{key_name} analyth_html exception: {e}')


def main():
    all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    all_manus = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'] + 1)
    for (key_index, key_name) in enumerate(all_cates):
        if security_times > 3:
            return
        if key_index % 6 == 0 or key_index % 6 == 1:
            if security_times > 3:
                return
            get_category(key_index=key_index, key_name=key_name, manu_ids=str(all_manus[key_index]))


if __name__ == "__main__":
    main()


# 根据关键字查找P/N, manu
from bs4 import BeautifulSoup
import time
from WRTools import IPHelper, UserAgentHelper, LogHelper, WaitHelp, QGHelp, EmailHelper, ExcelHelp
from IC_stock import IC_stock_excel_read, IC_Stock_excel_write
from urllib.parse import urlparse, parse_qs, parse_qsl
import os
import re
import html5lib
import json


default_url = 'https://octopart.com/'
keyword_source_file = '/Users/liuhe/PycharmProjects/SeleniumDemo/TKeywords.xlsx'
log_file = '/Users/liuhe/PycharmProjects/SeleniumDemo/Octopart_category/octopart_key_cate_log.txt'

total_page = 1
current_page = 1
# 出现安全验证的次数，连续三次则关闭webdriver
security_times = 0


def get_url(key_name, page, alpha, manu_ids) -> str:
    manu_param = '&manufacturer_id=' + manu_ids.replace(';', '&manufacturer_id=')
    page_param = '' if page == 1 else '&start=' + str(page * 10 - 10)
    url = f'https://octopart.com/search?q={key_name}{alpha}&currency=USD&specs=0{manu_param}{page_param}'
    return url


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
    global total_page
    try:
        ul = soup.select('ul.jsx-4126298714.jumps')[0]
        li_last = ul.select('li.jsx-4126298714')[-1]
        a = li_last.select('a')[0]
        total_page = a.text
    except:
        total_page = 1


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


def get_category(file_name_index, file_name, key_name, alpha):
    path = f'/Users/liuhe/Desktop/htmlFils_all/files1/{file_name}'
    htmlfile = open(path, 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    soup = BeautifulSoup(htmlhandle, 'html5lib')
    set_totalpage(soup)
    analyth_html(key_name=key_name, soup=soup, alpha=alpha, htmlhandle=htmlhandle)


# 解析html，获取cate，manu
def analyth_html(key_name, soup, alpha, htmlhandle):
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
                    info_list.append([cate_name, manu, key_name, total_page])
        if len(info_list) > 0:
            IC_Stock_excel_write.add_arr_to_sheet(file_name=f'{key_name}.xlsx', sheet_name='all', dim_arr=info_list)
    except Exception as e:
        info_arr = getSKUByRE(html_txt=htmlhandle, key_name=key_name)
        if len(info_arr) > 0:
            IC_Stock_excel_write.add_arr_to_sheet(file_name=f'{key_name}.xlsx', sheet_name='all', dim_arr=info_arr)
        else:
            LogHelper.write_log(log_file, f'{key_name} analyth_html exception: {e}')


# 正则"sku":"SAK-TC1367A-264F150EBAA","updated" ，直接强行获取
def getSKUByRE(html_txt, key_name) -> list:
    result = []
    rag = 'sku":"([A-Za-z0-9-]*?)","updated'
    cate_arr = re.findall(rag, html_txt)
    for temp_cate in cate_arr:
        cate = temp_cate[3:-3]
        result.append([cate, '', key_name, total_page])
    return result


# 获取url 查询参数dic
def getInfoByFileName(fileName):
    eg = 'view-source_https___octopart.com_search_q=TPS13&currency=USD&specs=0&manufacturer_id=370'
    url = fileName.replace('view-source_', '')
    url = url.replace('___', '://')
    url = url.replace('octopart.com_search_q', 'octopart.com/search?q')
    url = url.replace('octopart.com_search q', 'octopart.com/search?q')
    result = parse_qs(urlparse(url).query)
    return result


def get_files():
    path = '/Users/liuhe/Desktop/htmlFils_all/files1'
    file_name_list = os.listdir(path)
    result = []
    for temp in file_name_list:
        if temp.endswith('.htm') or temp.endswith('.html')  or temp.endswith('.mhtml'):
            result.append(temp)
    return result


def main():
    file_name_list = get_files()
    for (file_name_index, file_name) in enumerate(file_name_list):
        print(f'file name is: {file_name}')
        dic = getInfoByFileName(file_name)
        try:
            keyAndalpha = dic['q'][0]
            key = keyAndalpha[0:-1]
            alpha = keyAndalpha[-1]
        except:
            LogHelper.write_log(log_file_name=log_file, content='parameter q is none')
            continue
        try:
            page_str = dic['start'][0]
            if page_str:
                page = page_str.split('.')[0]
            else:
                page = '0'
        except:
            page = '0'
        get_category(file_name_index, file_name, key_name=key, alpha=alpha)


if __name__ == "__main__":
    main()

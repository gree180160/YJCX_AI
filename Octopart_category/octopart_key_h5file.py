# 根据关键字查找P/N, manu
from bs4 import BeautifulSoup
from WRTools import LogHelper, PathHelp, ExcelHelp
from Manager import URLManager
from urllib.parse import parse_qs
import os
import re
from urllib.parse import urlparse


default_url = 'https://octopart.com/'
keyword_source_file = PathHelp.get_file_path(None, 'TRenesa.xlsx')
log_file = '/Users/liuhe/PycharmProjects/SeleniumDemo/Octopart_category/octopart_key_cate_log.txt'
fold_path = '/Users/liuhe/Desktop/progress/TReneseas_all/Reneseas_html_files'

total_page = 1
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
            # EmailHelper.mail_ip_error("mac")
            # QGHelp.maintainWhiteList()
            # time.sleep(60)
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


def get_category(fold_path, file_name, key_name):
    path = fold_path + f'/{file_name}'
    htmlfile = open(path, 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    soup = BeautifulSoup(htmlhandle, 'html5lib')
    set_totalpage(soup)
    analyth_html(key_name=key_name, soup=soup, htmlhandle=htmlhandle)


# 解析html，获取cate，manu
def analyth_html(key_name, soup, htmlhandle):
    if is_security_check(soup=soup):
        LogHelper.write_log(log_file_name=log_file, content=f'alert happens in :{key_name} \n')
        return
    try:
        table = soup.select('div.jsx-2172888034.prices-view')[0]
        cate_first = table.select('div.jsx-2172888034')
        cate_left = table.select('div.jsx-2400378105.part')
        cates_all = cate_first + cate_left
        info_list = []
        for temp_cate in cates_all:
            header = temp_cate.select('div.jsx-3355510592.header')[0]
            try:
                manu = header.select('div.jsx-312275976.jsx-2018853745.manufacturer-name-and-possible-tooltip')[0].text
            except:
                manu = None
            try:
                cate_name = header.select('div.jsx-312275976.jsx-2018853745.mpn')[0].text
            except:
                cate_name = None
            if cate_name and manu:
                if cate_name.startswith(key_name):
                    info_list.append([cate_name, manu, key_name, total_page])
        if len(info_list) > 0:
            ExcelHelp.add_arr_to_sheet(file_name=keyword_source_file, sheet_name='page0_pn',
                                                  dim_arr=info_list)
    except Exception as e:
        info_arr = getSKUByRE(html_txt=htmlhandle, key_name=key_name)
        if len(info_arr) > 0:
            ExcelHelp.add_arr_to_sheet(file_name=keyword_source_file, sheet_name='page0_pn',
                                                  dim_arr=info_arr)
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
    # eg = 'view-source_https___octopart.com_search_q=TPS13&currency=USD&specs=0&manufacturer_id=370'
    url = fileName.replace('https __octopart.com_search currency=',
                           'view-source:https://octopart.com/search?currency=')
    url = url.replace('view-source_', '')
    url = url.replace('___', '://')
    url = url.replace('octopart.com_search_q', 'octopart.com/search?q')
    url = url.replace('octopart.com_search q', 'octopart.com/search?q')
    result = parse_qs(urlparse(url).query)
    return result


def get_files(fold_path: str):
    file_name_list = os.listdir(fold_path)
    result = []
    for temp in file_name_list:
        if temp.endswith('.htm') or temp.endswith('.html') or temp.endswith('.mhtml'):
            result.append(temp)
    return result


# 获取指定文件下的html files，并将结果转化为url输出
def get_finished_ppn(fold_path: str):
    file_name_list = os.listdir(fold_path)
    result = []
    for temp in file_name_list:
        result.append(get_ppn_from_filename(temp))
    return result


def get_ppn_from_filename(filename: str):
    result = ""
    if ' q=' in filename and '&currency=' in filename:
        index1: int = filename.index(' q=')
        index2: int = filename.index('&currency=')
        s = ''
        for (index, char) in enumerate(filename):
            if index in range(index1 + 3, index2):
                result += char
    return result


def main():
    # fold_path = fold_path
    file_name_list = get_files(fold_path=fold_path)
    for (file_name_index, file_name) in enumerate(file_name_list):
        print(f'file name is: {file_name}')
        dic = getInfoByFileName(file_name)
        try:
            key = dic['q'][0]
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
        get_category(fold_path=fold_path, file_name=file_name, key_name=key)


# 比较两个url 是否相同
def queryToUrl(url1, url2, para1, para2) -> bool:
    # url1 paramiter
    qs1 = urlparse(url1)
    dic1 = parse_qs(qs1.query)
    para1_value1 = dic1[para1]
    para2_value1 = dic1[para2]
    # url2 paramiter
    qs2 = urlparse(url2)
    dic2 = parse_qs(qs2.query)
    para1_value2 = dic2[para1]
    para2_value2 = dic2[para2]
    return para1_value1 == para1_value2 and para2_value1 == para2_value2


# 查找遗漏的html——文件,并保存
def get_unfinished_urls(keyword_source_file: str, finished_html_files_fold: str):
    unfinished_url = []
    unfinished_pn = []
    all_ppn = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='Sheet1', col_index=1)
    finished_ppn = get_finished_ppn(fold_path=finished_html_files_fold)
    for (ppn_index, temp_ppn) in enumerate(all_ppn):
        if not temp_ppn in finished_ppn:
            manu = URLManager.Octopart_manu.Renesas
            url = URLManager.octopart_get_page_url(key_name=temp_ppn, page=1, manu=manu)
            unfinished_url.append([url])
            unfinished_pn.append([temp_ppn])
    ExcelHelp.add_arr_to_sheet(file_name=keyword_source_file, sheet_name='unfinished_url', dim_arr=unfinished_url)
    ExcelHelp.add_arr_to_sheet(file_name=keyword_source_file, sheet_name='unfinished_pn', dim_arr=unfinished_pn)


if __name__ == "__main__":
     main()
    # get_unfinished_urls(keyword_source_file=PathHelp.get_file_path(None, 'TRenesa.xlsx') , finished_html_files_fold ='/Users/liuhe/Desktop/Reneseas_html_files')

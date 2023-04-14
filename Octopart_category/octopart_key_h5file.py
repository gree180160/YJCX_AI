# 根据关键字查找P/N, manu
from bs4 import BeautifulSoup
from WRTools import LogHelper, PathHelp, ExcelHelp
from Manager import URLManager
from urllib.parse import parse_qs
import os
import re
from urllib.parse import urlparse


default_url = 'https://octopart.com/'
keyword_source_file = PathHelp.get_file_path(None, 'TSTM.xlsx')
sheet_name = "page0_pn2"
fold_path = '/Users/liuhe/Desktop/progress/TSTM/html2'
log_file = '/Octopart_category/octopart_key_cate_log.txt'

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
    analyth_html(key_name=key_name, soup=soup)


# 解析html，获取cate，manu
def analyth_html(key_name, soup):
    if is_security_check(soup=soup):
        LogHelper.write_log(log_file_name=log_file, content=f'alert happens in :{key_name} \n')
        return
    info_list = []
    try:
        if soup.select('div.jsx-2172888034.prices-view').__len__() > 0:
            # style plain
            table = soup.select('div.jsx-2172888034.prices-view')[0]
            cate_first = table.select('div.jsx-2172888034')
            cate_left = table.select('div.jsx-2400378105.part')
            cates_all = cate_first + cate_left
            for temp_cate in cates_all:
                header = temp_cate.select('div.jsx-3355510592.header')[0]
                try:
                    manu = header.select('div.jsx-312275976.jsx-2018853745.manufacturer-name-and-possible-tooltip')[
                        0].text
                except:
                    manu = None
                try:
                    cate_name = header.select('div.jsx-312275976.jsx-2018853745.mpn')[0].text
                except:
                    cate_name = None
                if cate_name and manu:
                    if check_htmlPPN_valid(html_ppn=cate_name, opn=key_name):
                        info_list.append([cate_name, manu, key_name, total_page])
        else:
            # style container
            table = soup.select('div.jsx-2906236790.prices-view')[0]
            cate_first = table.select('div.jsx-2906236790')
            cate_left = table.select('div.jsx-1681079743.part')
            cates_all = cate_first + cate_left
            for temp_cate in cates_all:
                header = temp_cate.select('div.jsx-2471764431.header')[0]
                try:
                    manu = header.select('div.jsx-312275976.jsx-1485186546.manufacturer-name-and-possible-tooltip')[0].text
                except:
                    manu = None
                try:
                    cate_name = header.select('div.jsx-312275976.jsx-1485186546')[2].text
                except:
                    cate_name = None
                if cate_name and manu:
                    if check_htmlPPN_valid(html_ppn=cate_name, opn=key_name):
                        info_list.append([cate_name, manu, key_name, total_page])
    except Exception as e:
        LogHelper.write_log(log_file, f'{key_name} analyth_html exception: {e}')
    if len(info_list) > 0:
        ExcelHelp.add_arr_to_sheet(file_name=keyword_source_file, sheet_name=sheet_name,
                                       dim_arr=info_list)


# 获取url 查询参数dic
def getInfoByFileName(fileName):
    # eg = 'view-source_https___octopart.com_search_q=TPS13&currency=USD&specs=0&manufacturer_id=370'
    url = fileName.replace('https __octopart.com_search currency=',
                           'view-source:https://octopart.com/search?currency=')
    url = url.replace('view-source-https- octopart.com search q=', 'https://octopart.com/search?q=')
    url = url.replace('https __octopart.com_search q=', 'https://octopart.com/search?q=')
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


# 获取指定文件下的html files，并将结果转化为ppn输出
def get_finished_ppn(fold_paths: list):
    result = []
    for fold_path in fold_paths:
        file_name_list = os.listdir(fold_path)
        for temp in file_name_list:
            result.append(get_ppn_from_filename(temp))
    return result


def get_ppn_from_filename(filename: str):
    dic = getInfoByFileName(filename)
    try:
        key = dic['q'][0]
        key = key.replace('.html', '')
        key = key.replace('.htm', '')
    except:
        LogHelper.write_log(log_file_name=log_file, content='parameter q is none')
        key = ''
    return key


def get_url_from_filename(filename: str):
    url = filename.replace('https __octopart.com_search q=', 'view-source:https://octopart.com/search?q=')
    result = url.replace('.htm', '')
    result = result.replace('.html', '')
    return result


# 获取指定文件下的html files，并将结果转化为url输出
def get_finished_urls(fold_path: str):
    file_name_list = os.listdir(fold_path)
    result = []
    for temp in file_name_list:
        result.append(get_url_from_filename(temp))
    return result


# 验证获取的ppn 是否与opn 相关
def check_htmlPPN_valid(html_ppn, opn):
    opn = opn.replace(" ", "")
    html_ppn = html_ppn.replace(" ", "")
    # 去掉结尾的+，因为pn ,结尾有无+都是一个型号
    if opn.endswith('+'):
        pn = opn[0:-1]
    if html_ppn.endswith('+'):
        html_pn = html_ppn[0:-1]
    result = bool(re.search(opn, html_ppn, re.IGNORECASE))
    return result


def main():
    # fold_path = fold_path
    file_name_list = get_files(fold_path=fold_path)
    file_name_list.sort()
    for (file_name_index, file_name) in enumerate(file_name_list):
        if file_name_index in range(0, 10000):
            print(f'file_index is: {file_name_index}, file name is: {file_name}')
            dic = getInfoByFileName(file_name)
            try:
                key = dic['q'][0]
                key = key.replace('.html', '')
                key = key.replace('.htm', '')
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
def get_unfinished_pn(keyword_source_file: str, finished_html_files_folds: list):
    unfinished_url = []
    all_ppn = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='opn', col_index=1)
    finished_ppn = get_finished_ppn(fold_paths=finished_html_files_folds)
    for (ppn_index, temp_ppn) in enumerate(all_ppn):
        if not temp_ppn in finished_ppn:
            manu = URLManager.Octopart_manu.Onsemi
            url = URLManager.octopart_get_page_url(key_name=temp_ppn, page=1, manu=manu)
            unfinished_url.append([temp_ppn, url])
    ExcelHelp.add_arr_to_sheet(file_name=keyword_source_file, sheet_name='unfinished_url2', dim_arr=unfinished_url)


# 查找遗漏的html——文件,并保存
def get_unfinished_pageMore(keyword_source_file: str, finished_html_files_fold: str):
    unfinished_url = []
    url_pageMore = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='url_pagemore', col_index=1)
    finished_url = get_finished_urls(finished_html_files_fold)
    for (ppn_index, tempURL) in enumerate(url_pageMore):
        if not tempURL in finished_url:
            url = tempURL
            unfinished_url.append([url])
    ExcelHelp.add_arr_to_sheet(file_name=keyword_source_file, sheet_name='unfinished_url_pagemore', dim_arr=unfinished_url)


def get_Onsemi_ppn():
    finished_ppn1 = ExcelHelp.read_col_content(file_name=PathHelp.get_file_path(None, 'TOnsemi.xlsx'), sheet_name='ppn1', col_index=1)
    finished_ppn2 = ExcelHelp.read_col_content(file_name=PathHelp.get_file_path(None, 'TOnsemi.xlsx'),
                                               sheet_name='ppn2', col_index=1)
    finished_ppn3 = ExcelHelp.read_col_content(file_name=PathHelp.get_file_path(None, 'TOnsemi.xlsx'),
                                               sheet_name='ppn3', col_index=1)
    unfinished_ppn4 = ExcelHelp.read_col_content(file_name=PathHelp.get_file_path(None, 'TOnsemi_ppn.xlsx'),
                                               sheet_name='page0_pn4', col_index=1)
    all_finish = set(finished_ppn1).union(set(finished_ppn2)).union(set(finished_ppn3))
    ppn4 = list(set(unfinished_ppn4).difference(all_finish))
    ExcelHelp.add_arr_to_col(file_name=PathHelp.get_file_path(None, 'TOnsemi_ppn.xlsx'), sheet_name='ppn4', dim_arr=ppn4)


if __name__ == "__main__":
    # get_Onsemi_ppn()
    # get_category(fold_path="/Users/liuhe/Desktop", file_name="https __octopart.com_search q=LM293DR2&currency=USD&specs=0.html", key_name="LM293DR2")
    main()
    # get_unfinished_pn(keyword_source_file=PathHelp.get_file_path(None, 'TOnsemi.xlsx'),
    #                   finished_html_files_folds = ["/Users/liuhe/Desktop/progress/TOnsemi/Octopart_html1",
    #                                                "/Users/liuhe/Desktop/progress/TOnsemi/Octopart_html2",
    #                                                "/Users/liuhe/Desktop/progress/TOnsemi/Octopart_html3",
    #                                                "/Users/liuhe/Desktop/progress/TOnsemi/Octopart_html4"])

# 根据url查找P/N
from bs4 import BeautifulSoup
from WRTools import LogHelper, PathHelp, WaitHelp, ExcelHelp
from urllib.parse import urlparse, parse_qs, parse_qsl
import os
import re
import requests
import ssl


ssl._create_default_https_context = ssl._create_unverified_context

result_save_file = PathHelp.get_file_path('ADI', 'ADI_URLS&PNS.xlsx')
log_file = '//ADI/ADI_pn_log.txt'
html_file_path = '/Users/liuhe/Desktop/ADI_html_files'
headers = {'Accept-Language': 'en,zh;q=0.9,en-US;q=0.8,zh-CN;q=0.7',
               'Accept-Encoding': 'gzip,deflate, br',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}
waitting_urls = []

# *********************************从html files 分析价格数据*****************************************************
# 根据html 文件，获取页面所有cate的price信息，并保存,每1k 的cate，保存在一个excel 中
def get_soup(file_name_index, file_name):
    path = f'{html_file_path}/{file_name}'
    htmlfile = open(path, 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    soup = BeautifulSoup(htmlhandle, 'html5lib')
    analy_soup_new_products(soup=soup, htmlhandle=htmlhandle, fileName=file_name)


# 从首页获取adi 的一级分类的导航页
def analy_soup_first_level(soup, htmlhandle, fileName):
    table = soup.select('ul.adi-mm__products__categories-menu__list')[0]
    rows = table.select('li.adi-mm__products__categories-menu__list__category')
    urls = []
    for temp_row in rows:
        a = temp_row.select('a')[0]
        url = a['href']
        urls.append([url])
    ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name='first_level', dim_arr=urls)


#  获取adi 新产品的opn
def analy_soup_new_products(soup, htmlhandle, fileName):
    divs = soup.select('div.product-id')
    opns = []
    for temp_div in divs:
        a = temp_div.select('a')[0]
        opn = a.text
        opns.append([opn])
    ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name='new_opns', dim_arr=opns)


def analy_soup_second_level(soup, url):
    try:
        tables = soup.select('ul.list-sort-unstyled')
        for table in tables:
            rows = table.select('li')
            urls = []
            for temp_row in rows:
                a = temp_row.select('a')[0]
                url = a['href']
                urls.append([url])
        ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name='second_level', dim_arr=urls)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{url} more 解析异常：{e} ')



# 获取所有octopart 的html文件
def get_files():
    path = html_file_path
    file_name_list = os.listdir(path)
    result = []
    for temp in file_name_list:
        if temp.endswith('.htm') or temp.endswith('.html')  or temp.endswith('.mhtml'):
            result.append(temp)
    return result


# 分析本地的html文件
def local_html_file():
    file_name_list = get_files()
    print(f'file count is :{file_name_list.__len__()}')
    sublist = file_name_list[1:2]  # total 81695
    for (file_name_index, file_name) in enumerate(sublist):
        print(f'file name is: {file_name}')
        get_soup(file_name_index, file_name)

# 分析 online——url info
def links():
    links = ExcelHelp.read_col_content(result_save_file, sheet_name='first_level', col_index=1)
    for (index, url) in enumerate(links):
        print(f'index is :{index} url is : {url}')
        try:
            req = requests.get(url=url, headers=headers, proxies=IPHelper.getRandowProxy_contry3(),
                               timeout=(60, 120))
            if index > 0 and index % 15 == 0:
                WaitHelp.waitfor(True, isDebug=False)
                WaitHelp.waitfor(True, isDebug=False)
            else:
                WaitHelp.waitfor(True, isDebug=False)
        except Exception as e:
            LogHelper.write_log(log_file, f'{url} request get exception: {e}')
            return
        # print(f'respond is :{req.text}')
        soup = BeautifulSoup(req.text, 'lxml')
        analy_soup_second_level(soup, url=url)


def deal_sub():
    global waitting_urls
    links = ExcelHelp.read_col_content(result_save_file, sheet_name='second_level', col_index=1)
    waitting_urls = links
    while waitting_urls.__len__() > 0:
        current_url = waitting_urls[0]
        print(f'total count is :{waitting_urls.__len__()} first url is : {current_url}')
        if current_url.__contains__('parametricsearch'):
            waitting_urls.remove(current_url)
            print('excel_page add')
            ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name='excel_page', dim_arr=[[current_url]])
        else:
            try:
                req = requests.get(url=current_url, headers=headers, proxies=IPHelper.getRandowProxy_contry3(),
                                   timeout=(300, 600))
                WaitHelp.waitfor(True, isDebug=False)
                # print(f'respond is :{req.text}')
                soup = BeautifulSoup(req.text, 'lxml')
                analy_soup_sub_level(soup, url=current_url)
            except Exception as e:
                LogHelper.write_log(log_file, f'url is: {current_url} request get exception: {e}')
                return



def analy_soup_sub_level(soup, url):
    global waitting_urls
    # 先根据是否有excel 链接，判断是否为最终节点，excel_page， 是则记录最终节点url，否则把页面中的url 加入到middle_page，和waitting
    tools = soup.select('menu.tools')
    waitting_urls.remove(url)
    try:
        tables = soup.select('ul.list-sort-unstyled')
        urls = []
        for table in tables:
            rows = table.select('li')
            for temp_row in rows:
                a = temp_row.select('a')[0]
                url = a['href']
                if not url.startswith('http'):
                    url = 'https://www.analog.com' + url
                if url.__contains__('parametricsearch'):
                    # add to excel_page
                    print('excel_page add')
                    ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name='excel_page',
                                               dim_arr=[[url]])
                else:
                    if not waitting_urls.__contains__(url):
                        waitting_urls.append(url)
                        urls.append([url])
        if urls.__len__() > 0:
            print('middle_page add')
            ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name='middle_page', dim_arr=urls)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{url} more 解析异常：{e} ')


# 给excel_page url 增加搜索条件
def add_filterToURL():
    original_urls = ExcelHelp.read_col_content(file_name=result_save_file, sheet_name='excel_page', col_index=1)
    result = []
    for temp_url in original_urls:
        newURL = temp_url + '#/d=s7|s25|s3|s5'
        result.append([newURL])
    ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name='url_all', dim_arr=result)


def main():
    # deal_sub()
    add_filterToURL()

if __name__ == "__main__":
    main()


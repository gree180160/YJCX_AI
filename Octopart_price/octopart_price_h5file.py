# 根据关键字查找P/N, manu
from bs4 import BeautifulSoup
import time
from WRTools import IPHelper, UserAgentHelper, LogHelper, PathHelp, QGHelp, EmailHelper, ExcelHelp
from IC_stock import IC_stock_excel_read, IC_Stock_excel_write
from urllib.parse import urlparse, parse_qs, parse_qsl
import os
import re
import base64
import octopart_price_info


result_save_file = PathHelp.get_file_path('Octopart_price', 'octopart_price_cate_1012war.xlsx')
log_file = '/Users/liuhe/PycharmProjects/SeleniumDemo/Octopart_category/octopart_key_cate_log.txt'


def get_price(file_name_index, file_name, cate_name):
    path = f'/Users/liuhe/Desktop/htmlFils_all/K1012war/{file_name}'
    htmlfile = open(path, 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    soup = BeautifulSoup(htmlhandle, 'html5lib')
    analy_html(cate_name=cate_name, soup=soup, htmlhandle=htmlhandle)


# 解析某个型号的页面信息，如果有更多，直接点击，然后只选择start ， 遇到第一个不是star 的就返回
def analy_html(cate_name, soup, htmlhandle):
    # 是否需要继续展开。 出现第一条非start数据后不再展开
    try:
        all_cates = soup.select('div.jsx-922694994.results')[0]
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} all_cates exception:{e}')
        return
    try:
        first_cate = all_cates.select('div.jsx-2172888034')[0]
    except:
        first_cate = all_cates.select('div.jsx-2172888034.part')[0]
    if not cate_valid(cate_name, first_cate):
        return
    need_more = True
    # 默认直接显示的row
    valid_supplier_arr = []
    tr_arr = []
    try:
        cate_table = first_cate.select('tbody')[0]
        tr_arr = cate_table.select('tr')
        for tr in tr_arr:
            if not need_more:
                break
            cate_price_ele = get_supplier_info(tr=tr, cate_name=cate_name)
            # 只有实心(1)数据才是有效的，只有空心(-1)才需要停止loop
            if cate_price_ele.is_valid_supplier():
                valid_supplier_arr.append(cate_price_ele.descritpion_arr())
            else:
                print(f'supplier invalid: {cate_price_ele.description_str()}')
                if cate_price_ele.stop_loop():
                    need_more = False
    except Exception as e:
        need_more = False
        LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} 默认打开的内容解析异常：{e} ')
    sheet_name_base64str = str(base64.b64encode(cate_name.encode('utf-8')), 'utf-8')
    IC_Stock_excel_write.add_arr_to_sheet(
        file_name=result_save_file,
        sheet_name=sheet_name_base64str,
        dim_arr=valid_supplier_arr)
    valid_supplier_arr.clear()


# 判断当前内容是否和cate_name 一致
def cate_valid(cate_name, first_row) -> bool:
    result = False
    try:
        cate_div = first_row.select('div.jsx-312275976.jsx-2649123136.mpn')[0]
        html_cate_name = cate_div.text
        # 去掉中间的空格防止，导入的cate 格式误差
        cate_name = cate_name.replace(" ", "")
        html_cate_name = html_cate_name.replace(" ", "")
        # 去掉结尾的+，因为cate_name ,结尾有无+都是一个型号
        if cate_name.endswith('+'):
            cate_name = cate_name[0:-1]
        if html_cate_name.endswith('+'):
            html_cate_name = html_cate_name[0:-1]
        result = bool(re.search(cate_name, html_cate_name, re.IGNORECASE))
        if not result:
            LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} cannot match')
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} cannot check name: {e}')
        result = False
    return result


# 将页面tr的内容 转化成octopart_price_info
# tr: contain row info
def get_supplier_info(tr, cate_name) -> octopart_price_info:
    td_arr = tr.select('td')
    star_td = td_arr[0]
    is_star = 0
    try:
        a = star_td.select('a')[0]
        title = a['title']
        if title == 'Non-Authorized Stocking Distributor':
            is_star = -1
        elif title == 'Authorized Distributor':
            is_star = 1
        else:
            is_star = 0
    except:
        is_star = -1
    distribute_tr = td_arr[1]
    try:
        distribute_name = distribute_tr.select('a')[0].text
    except:
        distribute_name = '--'
    SKU_tr = td_arr[2]
    try:
        sku = SKU_tr.text
    except:
        sku = "--"
    stock_tr = td_arr[3]
    try:
        stock = stock_tr.text
    except:
        stock = '--'
    MOQ_tr = td_arr[4]
    try:
        moq = MOQ_tr.text
    except:
        moq = '--'
    currency_type_tr = td_arr[6]
    try:
        currency_type = currency_type_tr.text
    except:
        currency_type = '--'
    k_price_tr = td_arr[10]
    try:
        k_price = k_price_tr.text
    except:
        k_price = '--'
    updated_tr = td_arr[12]
    try:
        updated_span = updated_tr.select('span')[0]
        updated = updated_span.text
    except:
        updated = '--'
    manu_name = "--"
    octopart_price_ele = octopart_price_info.Octopart_price_info(cate=cate_name, manu=manu_name, is_star=is_star,
                                                                 distribute=distribute_name, SKU=sku, stock=stock,
                                                                 MOQ=moq, currency_type=currency_type, k_price=k_price,
                                                                 updated=updated)
    return octopart_price_ele


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
    path = '/Users/liuhe/Desktop/htmlFils_all/K1012war'
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
            cate_name = dic['q'][0]
        except:
            LogHelper.write_log(log_file_name=log_file, content='parameter q is none')
            continue
        get_price(file_name_index, file_name, cate_name=cate_name)


if __name__ == "__main__":
    main()


# 根据关键字查找P/N, manu
from bs4 import BeautifulSoup
from WRTools import IPHelper, UserAgentHelper, LogHelper, PathHelp, QGHelp, EmailHelper, ExcelHelp
import requests
import re
import base64
import octopart_price_info
from Manager import URLManager


sourceFile_dic = {'fileName': PathHelp.get_file_path('TInfenion_40H', 'Task.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 2}
result_save_file = PathHelp.get_file_path('TInfenion_40H', 'dijikey_status.xlsx')
log_file = '//Octopart_category/octopart_key_cate_log.txt'

cookies = {'fc_locale':'zh-CN', 'fc_timezone':'Asia%2FShanghai'}
headers = {'User-Agent': UserAgentHelper.getRandowUA(),
               'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
               'Accept-Encoding': 'gzip,deflate, br',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Connection': 'keep-alive'}


def get_price(cate_name: str, manu: URLManager.Octopart_manu):
    url = URLManager.octopart_get_page_url(key_name=cate_name, page=1, manu=manu)
    req = requests.get(url=url, headers=headers, cookies=cookies, timeout=(600, 360))
    soup = BeautifulSoup(req.text, 'lxml')
    analy_html(cate_name=cate_name, soup=soup)


# 解析某个型号的页面信息，如果有更多，直接点击，然后只选择start ， 遇到第一个不是star 的就返回
def analy_html(cate_name, soup):
    # 是否需要继续展开。 出现第一条非start数据后不再展开
    if '?' in cate_name:
        return
    try:
        # all_cates = soup.select('div.jsx-922694994.results')[0]
        all_cates = soup.select('div.jsx-2172888034.prices-view')[0]
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
    ExcelHelp.add_arr_to_sheet(
        file_name=result_save_file,
        sheet_name=sheet_name_base64str,
        dim_arr=valid_supplier_arr)
    valid_supplier_arr.clear()


# 判断当前内容是否和cate_name 一致
def cate_valid(cate_name, first_row) -> bool:
    result = False
    try:
        cate_div = first_row.select('div.jsx-312275976.jsx-2018853745.mpn')[0]
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


def main():
    all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    for (cate_index, cate_name) in enumerate(all_cates):
        if cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
            get_price(cate_name=cate_name, manu=URLManager.Octopart_manu.NoManu)


if __name__ == "__main__":
    main()


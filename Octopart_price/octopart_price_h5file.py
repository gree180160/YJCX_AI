# 根据关键字查找P/N, manu
from bs4 import BeautifulSoup
from WRTools import LogHelper, PathHelp, ExcelHelp
import os
import re
import base64
import octopart_price_info

# result_save_file_arr = ['/Users/liuhe/Desktop/progress/TOnsemi/octopart/4-1.xlsx',
#                         '/Users/liuhe/Desktop/progress/TOnsemi/octopart/4-2.xlsx',
#                         '/Users/liuhe/Desktop/progress/TOnsemi/octopart/4-3.xlsx',
#                         '/Users/liuhe/Desktop/progress/TOnsemi/octopart/4-4.xlsx']
# log_file = '//Octopart_category/octopart_key_cate_log.txt'
# html_file_path = '/Users/liuhe/Desktop/progress/TOnsemi/Octopart_html4'

result_save_file_arr = ['/Users/liuhe/Desktop/progress/TSTM/octopart_price1.xlsx']
log_file = '//Octopart_category/octopart_key_cate_log.txt'
html_file_path = '/Users/liuhe/Desktop/progress/TSTM/html1'


# 获取所有octopart 的html文件
def get_files():
    path = html_file_path
    file_name_list = os.listdir(path)
    result = []
    for temp in file_name_list:
        if temp.endswith('.htm') or temp.endswith('.html')  or temp.endswith('.mhtml'):
            result.append(temp)
    return result


# *********************************从html files 分析价格数据*****************************************************
# 根据html 文件，获取页面所有cate的price信息，并保存,每1k 的cate，保存在一个excel 中
def manu_get_price(file_name_index, file_name):
    path = f'{html_file_path}/{file_name}'
    htmlfile = open(path, 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    soup = BeautifulSoup(htmlhandle, 'html5lib')
    manu_analy_html(soup=soup, htmlhandle=htmlhandle, fileName=file_name, file_name_index=file_name_index)


# 解析某个型号的页面信息，如果有更多，直接点击，然后只选择start ， 遇到第一个不是star 的就返回
def manu_analy_html(soup, htmlhandle, fileName, file_name_index):
    # 是否需要继续展开。 出现第一条非start数据后不再展开
    try:
        table = soup.select('div.jsx-2906236790.prices-view')[0]
        cate_first = table.select('div.jsx-2906236790')
        cate_left = table.select('div.jsx-1681079743.part')
        cates_all = cate_first + cate_left
        valid_supplier_arr = []
        for temp_cate in cates_all:
            try:
                supplier_table = temp_cate.select('table.jsx-4253165187')[0]
                cate_name = get_cate_name(cate_area=temp_cate, file_name=fileName)
                if '?' in cate_name:
                    continue
                manu_name = get_manufacture_name(cate_area=temp_cate, file_name=fileName)
                tbody = supplier_table.select('tbody.jsx-4253165187')[0]
                tr_list = tbody.select('tr')
                for tr_row in tr_list:
                    cate_price_ele = manu_get_supplier_info(tr=tr_row, cate_name=cate_name, manu_name=manu_name)
                    # 只有实心(1)数据才是有效的，只有空心(-1)才需要停止loop
                    if cate_price_ele.is_valid_supplier() or True:
                        valid_supplier_arr.append(cate_price_ele.descritpion_arr())
                    else:
                        print(f'supplier invalid: {cate_price_ele.description_str()}')
                        if cate_price_ele.stop_loop():
                            need_more = False
            except Exception as e:
                need_more = False
                LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} 默认打开的内容解析异常：{e} ')
        ExcelHelp.add_arr_to_sheet(
            file_name=result_save_file_arr[file_name_index % result_save_file_arr.__len__()],
            sheet_name='octopart_price',
            dim_arr=valid_supplier_arr)
        valid_supplier_arr.clear()
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{fileName} all_cates exception:{e}')
        return


# 获取cate
def get_cate_name(cate_area, file_name) -> str:
    cate_name = ''
    try:
        if cate_area.select('div.jsx-312275976.jsx-2018853745.mpn').__len__() > 0:
            cate_div = cate_area.select('div.jsx-312275976.jsx-2018853745.mpn')[0]
            cate_name = cate_div.text
        else:
            header = cate_area.select('div.jsx-2471764431.header')[0]
            cate_name = header.select('div.jsx-312275976.jsx-1485186546')[2].text
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{file_name} cannot check keyname: {e}')
    return cate_name


# 获取manu
def get_manufacture_name(cate_area, file_name) -> str:
    manu_name = ''
    try:
        if cate_area.select('div.jsx-312275976.jsx-2018853745.manufacturer-name-and-possible-tooltip').__len__() > 0:
            manu_name_value = cate_area.select('div.jsx-312275976.jsx-2018853745.manufacturer-name-and-possible-tooltip')[0].text
            manu_name = manu_name_value
        else:
            header = cate_area.select('div.jsx-2471764431.header')[0]

            manu_name = header.select('div.jsx-312275976.jsx-1485186546.manufacturer-name-and-possible-tooltip')[0].text
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{file_name} cannot check manufacture: {e}')
    return manu_name


# 手动解析html files 将页面tr的内容 转化成octopart_price_info
# tr: contain row info
def manu_get_supplier_info(tr, cate_name, manu_name) -> octopart_price_info:
    td_arr = tr.select('td')
    star_td = td_arr[0]
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
    manu_name = manu_name
    octopart_price_ele = octopart_price_info.Octopart_price_info(cate=cate_name, manu=manu_name, is_star=is_star,
                                                                 distribute=distribute_name, SKU=sku, stock=stock,
                                                                 MOQ=moq, currency_type=currency_type, k_price=k_price,
                                                                 updated=updated)
    return octopart_price_ele



def main():
    file_name_list = get_files()
    print(f'file count is :{file_name_list.__len__()}')
    sublist = file_name_list
    for (file_name_index, file_name) in enumerate(sublist):
        if file_name_index in range(0, 10000):
            print(f'file_index is: {file_name_index}, file name is: {file_name}')
            manu_get_price(file_name_index, file_name)


if __name__ == "__main__":
    main()
    # manu_get_price(0, "https __octopart.com_search q=LM293DR2&currency=USD&specs=0.html")
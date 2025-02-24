# 对于贸易商数量超过5家的，跑一下正能量里面的价格，取3个月内的最高值，没有价格则忽略
#一个月内，实名supplier，至少有5条报价,云汉，圣禾堂一家算三家，取价格第二低的报价
import time

from WRTools import PathHelp, ExcelHelp, WaitHelp, MySqlHelp_recommanded
import re
import json
from urllib.request import urlopen
import os

good_suppliers = ['云汉芯城', '圣禾堂', '誉光国际']
# 取3个月内的最高值，没有价格则忽略


def bom_price_result(cate_source_file, sheet_name):
    rate = get_rate()
    pps = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name=sheet_name, col_index=1)
    manufactures = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name=sheet_name, col_index=2)
    bom_price_list = ExcelHelp.read_sheet_content_by_name(file_name=cate_source_file, sheet_name='bom_price')
    result = []
    for (index, temp_ppn) in enumerate(pps):
        ppn_str = str(temp_ppn)
        price_info_arr = []
        #MySqlHelp_recommanded.DBRecommandChip().bom_price_read("update_time > '2023/10/28'")
        started_record = False
        #(`ppn`, `manu`, `supplier`, `package`, `lot`, `quoted_price`, `release_time`, `stock_num`, `valid_supplier`, `update_time`)
        supplier_count = 0
        for (row_index, row_content) in enumerate(bom_price_list):
            ppn_bom = str(row_content[0])
            if ppn_bom == ppn_str:
                started_record = True
                valid_date = is_valid_supplier(row_content[6], row_content[2])
                if valid_date:
                    bom_price = row_content[5]
                    bom_price_num = change_price_get(bom_price, rate)
                    price_info_arr.append([bom_price_num, row_index])
                    if row_content[2].__contains__('云汉芯城') or row_content[2].__contains__('圣禾堂'):
                        supplier_count += 3
                    elif row_content[2].__contains__('誉光国际') or row_content[2].__contains__('科伟奇电子'):
                        supplier_count += 2
                    else:
                        supplier_count += 1
            else:
                if started_record:
                    break #结束这个ppn 的查找

        # 至少有5条报价, 云汉，圣禾堂一家算三家，取价格第二低的报价
        if price_info_arr.__len__() > 0 and supplier_count >= 3:
            second_smallest_arr = second_smallest(price_info_arr)
            ppn_result = [ppn_str, manufactures[index], second_smallest_arr[0], bom_price_list[second_smallest_arr[1]][2]]
        else:
            ppn_result = [ppn_str, manufactures[index], "", ""]
        print(ppn_result)
        result.append(ppn_result)
    ExcelHelp.add_arr_to_sheet(file_name=cate_source_file, sheet_name='bom_price_sum', dim_arr=result)


# 获取倒数第二小的价格，及其对应的index，为获取supplier等信息做准备
def second_smallest(arr):
    # 排序数组，根据price的值进行排序
    sorted_arr = sorted(arr, key=lambda x: x[0])
            # 找到倒数第二小的price
    if len(sorted_arr) < 2:
        return arr[0]  # 如果没有倒数第二小的元素，则返回None
    second_smallest_price = sorted_arr[1]
    # 找到对应的row_index
    for item in sorted_arr:
        if abs(float(item[0]) - float(second_smallest_price[0])) < 0.0001:
            return item  # 返回[price, row_index]


def change_price_get(price_str, rate):
    price_float = 0.00
    if price_str is not None:
        if len(price_str) > 0:
            price_str = extract_currency(price_str)
            if '￥' in price_str:
                price_str = price_str.replace('￥', '')
                price_str = price_str.replace(',', '')
                price_float = float(price_str)
            elif '＄' in price_str:
                price_str = price_str.replace('＄', '')
                price_str = price_str.replace(',', '')
                price_float = float(price_str) * rate
            else:
                price_str = price_str.replace(',', '')
                price_float = float(price_str)
            if price_float <= 0:
                price_float = 0.00
    return price_float


# 计算汇率
def get_rate():
    result = 7.3 # default cate
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        resp = urlopen(url)
        resp = resp.read().decode(resp.headers.get_content_charset() or 'ascii')
        json_dic = json.loads(resp)
        result = json_dic['rates']['CNY']
        print(f'net rate is:{result}')
    except Exception as e:
        print('get_rate exception: {e}')
    return result


def extract_currency(string):
    pattern = r'[￥＄0-9.]+'  # 匹配货币符号¥、$，数字和小数点
    matches = re.findall(pattern, string)
    if matches.__len__() > 0:
        return matches[0]
    else:
        return '0.00'


def is_valid_supplier(date_string, supplier_name) -> bool:
    if supplier_name.__contains__("此供应商选择了隐藏公司名") or supplier_name.__contains__('订货'):
        return False
    if date_string.__contains__('1月内') or date_string.__contains__("周内") or date_string.__contains__(
            'API实时'):
        return True
    elif date_string.__contains__('天') or date_string.__contains__('小时'):
        return True
    else:
        numberDays = WaitHelp.daysPassed(date_string)
        if 0 < numberDays <= 30:  # 8
            return True
        else:
            print(f'thatDay invalid: {date_string}')
        return False


def read_record(save_file, task_name):
    record = MySqlHelp_recommanded.DBRecommandChip().bom_price_read(f'task_name = "{task_name}"')
    ExcelHelp.add_arr_to_sheet(save_file, 'bom_price', record)


if __name__ == "__main__":
    aim_file = PathHelp.get_file_path(None, 'TInfineonPowerManger.xlsx')
    task_name = 'TInfineonPowerManger'
    read_record(aim_file, task_name)
    bom_price_result(aim_file, 'ppn2')
    print('over')








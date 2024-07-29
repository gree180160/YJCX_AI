# 对于贸易商数量超过5家的，跑一下正能量里面的价格，取3个月内的最高值，没有价格则忽略
#一个月内，实名supplier，至少有三条报价
from WRTools import PathHelp, ExcelHelp, MySqlHelp_recommanded, WaitHelp
import re
import json
from urllib.request import urlopen
from Manager import TaskManager
import ssl


# 取3个月内的最高值，没有价格则忽略
def bom_price_result(cate_source_file):
    rate = get_rate()
    pps = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn4', col_index=1)
    manufactures = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn4', col_index=2)
    bom_price_list = ExcelHelp.read_sheet_content_by_name(file_name=cate_source_file, sheet_name='bom_price')
    result = []
    for (index, temp_ppn) in enumerate(pps):
        ppn_str = str(temp_ppn)
        price_arr = []
        #MySqlHelp_recommanded.DBRecommandChip().bom_price_read("update_time > '2023/10/28'")
        started_record = False
        #(`ppn`, `manu`, `supplier`, `package`, `lot`, `quoted_price`, `release_time`, `stock_num`, `valid_supplier`, `update_time`)
        for row_content in bom_price_list:
            ppn_bom = str(row_content[0])
            if ppn_bom == ppn_str:
                started_record = True
                valid_date = is_valid_supplier(row_content[6], row_content[2])
                if valid_date:
                    bom_price = row_content[5]
                    bom_price_num = change_price_get(bom_price, rate)
                    price_arr.append(bom_price_num)
            else:
                if started_record:
                    break #结束这个ppn 的查找
        price_arr = sorted(price_arr, reverse=True)
        if price_arr.__len__() > 0:
            if int(price_arr[-1]) > 0:
                min = price_arr[-1]
            else:
                if price_arr.__len__() >= 2:
                    min = price_arr[-1]
                else:
                    min = ' '
        else:
            min = ''
        ppn_result = [ppn_str, manufactures[index]] + [min]
        print(ppn_result)
        result.append(ppn_result)
    ExcelHelp.add_arr_to_sheet(file_name=cate_source_file, sheet_name='bom_price_sum', dim_arr=result)


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
    result = 7.27  # default cate
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        json_str = ''
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
    if supplier_name.__contains__("此供应商选择了隐藏公司名"):
        return False
    valid_time_arr = ['3天内', '1周内', '今天', '昨天', '1月内', '2022/09']
    if valid_time_arr.__contains__(date_string):
        return True


if __name__ == "__main__":
    bom_price_result(PathHelp.get_file_path(None, 'TManuAndSeri_willTC.xlsx'))
    print('over')




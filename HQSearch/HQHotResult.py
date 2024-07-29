# 计算cate 热度
# 输入型号， 查询热度
# 月：1. count(month_value < 5) < 3
# 月：2. count(month_value > 10) >= 3 and count(month_value > 20) >= 2 and count(month_value > 50) >=1
# 月：3. max(new1, new2, new3) > 10
# 月：4. max(all_list) > 50 and min(new1, new2, new3) > 10 -> True
# 月：5. max(new1, new2, new3) < 5 -> False
# 周: 1. count((new1, new2, new3, new4) > 10) > 2, count((new1, new2, new3, new4) <5 ) < 2,
# 周: 2. min(new1, new2, new3, new4) >= 10 -> True

from openpyxl import workbook, load_workbook, Workbook
import base64
from statistics import mean
import math
from WRTools import PathHelp, ExcelHelp, MySqlHelp_recommanded
from Manager import TaskManager
# cate_source_file = PathHelp.get_file_path(None, 'TLK240322.xlsx') #PathHelp.get_file_path(None, '/Users/liuhe/Downloads/TTIMilitary.xlsx')
# 根据规则匹配判断型号是否符合热度标准。


def HQ_hot_result(cate_source_file):
    pps = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn', col_index=1)
    manufactures = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn', col_index=2)
    hq_hot_info = ExcelHelp.read_sheet_content_by_name(cate_source_file, sheet_name='HQ_hot')
    result = []
    for (index, temp_ppn) in enumerate(pps):
        ppn_str = str(temp_ppn)
        hot_result = 0
        hot_week = hot_month = ''

        for (row_index, row_content) in enumerate(hq_hot_info):
            if row_index > 0:
                ppn_ic = str(row_content[0])
                if ppn_ic.upper() == ppn_str.upper():
                    hot_week = row_content[2]
                    hot_month = row_content[3]
                    week_data = eval(hot_week)
                    try:
                        int_week_data = [int(x) for x in week_data]
                    except Exception as e:
                        int_week_data = [9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999]
                        print(f'{ppn_ic} int_week_data error: {e}')
                    month_data = eval(hot_month)
                    try:
                        int_month_data = [int(x) for x in month_data]
                    except Exception as e:
                        int_month_data = [9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999]
                        print(f'{ppn_ic} int_month_data error: {e}')
                    if valid_week(int_week_data) and valid_month(int_month_data):
                        hot_result = 1
        result.append([ppn_str, manufactures[index], hot_week, hot_month, hot_result])
    ExcelHelp.add_arr_to_sheet(file_name=cate_source_file, sheet_name="HQ_hot_result", dim_arr=result)


# check week search data
def valid_week(week_data: list):
    result = False
    last_four = sorted(week_data[-4:])
    if last_four[1] > 5 and last_four[2] > 8 and last_four[-1] > 30:
        result = True
    return result


# check month search data
def valid_month(month_data: list):
    result = False
    # 条件1
    condition1_count = sum(1 for month_value in month_data if month_value < 30) < 3
    # 条件2
    condition2_count = sum(1 for month_value in month_data if month_value > 30) >= 8 and sum(
        1 for month_value in month_data if month_value > 50) >= 7 and sum(
        1 for month_value in month_data if month_value > 100) >= 3

    # 条件3
    condition3 = max(month_data[-3:]) > 100
    # 条件4 -> True
    condition4 = max(month_data) > 300 and min(month_data[-2:]) > 20
    # 条件5 -> False
    condition5 = max(month_data[-3:]) < 60
    # 验证条件
    if condition4:
        return True
    if condition5:
        return False
    if condition1_count and condition2_count and condition3:
        result = True
    return result


# 加权平均数
def HQ_hot_result2(cate_source_file):
    pps = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn', col_index=1)
    manufactures = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn', col_index=2)
    hq_hot_info = ExcelHelp.read_sheet_content_by_name(cate_source_file, sheet_name='HQ_hot')
    result = []
    for (index, temp_ppn) in enumerate(pps):
        ppn_str = str(temp_ppn)
        avg = hot_result = 0
        hot_week = hot_month = ''

        for (row_index, row_content) in enumerate(hq_hot_info):
            if row_index > 0:
                ppn_ic = str(row_content[0])
                if ppn_ic.upper() == ppn_str.upper():
                    hot_week = row_content[2]
                    hot_month = row_content[3]
                    week_data = eval(hot_week)
                    try:
                        int_week_data = [int(x) for x in week_data]
                    except Exception as e:
                        int_week_data = [9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999]
                        print(f'{ppn_ic} int_week_data error: {e}')
                    month_data = eval(hot_month)
                    try:
                        int_month_data = [int(x) for x in month_data]
                    except Exception as e:
                        int_month_data = [9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999, 9999]
                        print(f'{ppn_ic} int_month_data error: {e}')
                    avg = getMonthAvg(int_month_data)
                    if valid_week(int_week_data) and valid_month(int_month_data):
                        hot_result = 1
                    else:
                        hot_result = 0
                    break;
        result.append([ppn_str, manufactures[index], hot_week, hot_month, avg, hot_result])
    ExcelHelp.add_arr_to_sheet(file_name=cate_source_file, sheet_name="HQ_hot_result", dim_arr=result)


# 去掉最小值，前四个月数据*0.8， 后四个月数据*1.2，再算平均数，再/10
def getMonthAvg(month_list):
    new_list = []
    for (index, value) in enumerate(month_list):
        try:
            if index <= 3:
                new_value = value * 0.8
            elif index >= 8:
                new_value = value * 1.2
            else:
                new_value = value * 1.0
        except:
            new_value = 9999
        new_list.append(new_value)
    result = round(mean(new_list), 2)
    return result


if __name__ == "__main__":
    # HQ_hot_result2(PathHelp.get_file_path("LiChuang", 'TLCClearance.xlsx'))
    HQ_hot_result2(PathHelp.get_file_path(None, 'TRU2407_72H.xlsx'))
    print('over')

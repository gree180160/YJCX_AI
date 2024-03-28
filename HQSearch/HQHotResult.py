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
from WRTools import PathHelp, ExcelHelp, MySqlHelp_recommanded
from Manager import TaskManager

cate_source_file = PathHelp.get_file_path(None, 'TLK240322.xlsx') #PathHelp.get_file_path(None, '/Users/liuhe/Downloads/TTIMilitary.xlsx')
result_save_file = cate_source_file


# 根据规则匹配判断型号是否符合热度标准。
def HQ_hot_result():
    pps = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn', col_index=1)
    manufactures = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn', col_index=2)
    result = []
    for (index, temp_ppn) in enumerate(pps):
        ppn_str = str(temp_ppn)
        hot_result = 0
        hq_hot_info = ExcelHelp.read_sheet_content_by_name(cate_source_file, sheet_name='HQ_hot')
        for (row_index, row_content) in enumerate(hq_hot_info):
            if row_index > 0:
                ppn_ic = str(row_content[0])
                week_data = eval(row_content[2])
                int_week_data = [int(x) for x in week_data]
                month_data = eval(row_content[3])
                int_month_data = [int(x) for x in month_data]
                if ppn_ic.upper() == ppn_str.upper():
                    if valid_week(int_week_data) and valid_month(int_month_data):
                        hot_result = 1
        result.append([ppn_str, manufactures[index], hot_result])
    ExcelHelp.add_arr_to_sheet(file_name=cate_source_file, sheet_name="HQ_hot_result", dim_arr=result)


# check week search data
def valid_week(week_data: list):
    result = False
    last_four = sorted(week_data[-4:])
    if last_four[-1] > 10 and last_four[1] > 2 and last_four[2] > 3:
        result = True
    return result


# check month search data
def valid_month(month_data: list):
    result = False
    # 条件1
    condition1_count = sum(1 for month_value in month_data if month_value < 5) < 3
    # 条件2
    condition2_count = sum(1 for month_value in month_data if month_value > 10) >= 5 and sum(
        1 for month_value in month_data if month_value > 20) >= 2 and sum(
        1 for month_value in month_data if month_value > 50) >= 1

    # 条件3
    condition3 = max(month_data[-3:]) > 10
    # 条件4 -> True
    condition4 = max(month_data) > 100 and min(month_data[-3:]) > 10
    # 条件5 -> False
    condition5 = max(month_data[-3:]) < 5
    # 验证条件
    if condition4:
        return True
    if condition5:
        return False
    if condition1_count and condition2_count and condition3:
        result = True
    return result


if __name__ == "__main__":
    HQ_hot_result()
    print('over')

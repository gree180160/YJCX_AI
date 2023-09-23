import pandas as pd
import os
from WRTools import ExcelHelp


def csv_to_xlsx_pd(file):
    csv = pd.read_csv(file + '.cvs', encoding='utf-8')
    csv.to_excel(file + ".xlsx", sheet_name='data')


def read_sheet_content(file_name):
    source_data = pd.read_csv(file_name)
    list2 = source_data.values.tolist()
    return list2


def jinshun2():
    fold = '/Users/liuhe/Desktop/progress/TReneseas_all/JinShun2/renesas/'
    list_file = os.listdir(fold)  # 返回指定目录
    result = []
    for temp_file in list_file:
        if temp_file.__contains__('.csv'):
            sheet_content = read_sheet_content(f"{fold}{temp_file}")
            for row in sheet_content:
                new_row = [row[3], row[4], row[6]]
                result.append(new_row)
    ExcelHelp.add_arr_to_sheet(file_name=f'{fold}sum.xlsx', sheet_name='ppn', dim_arr=result)


if __name__ == '__main__':
    jinshun2()
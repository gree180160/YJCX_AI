import pandas as pd
import os
from WRTools import ExcelHelp, PathHelp


def csv_to_xlsx_pd(file):
    csv = pd.read_csv(file + '.cvs', encoding='utf-8', encoding_errors='ignore')
    csv.to_excel(file + ".xlsx", sheet_name='data')


def read_title(file_name):
    title_row = pd.read_csv(file_name, encoding='utf-8', encoding_errors='ignore', header=0)
    list2 = title_row.columns.tolist()
    return list2


def read_sheet_content(file_name):
    source_data = pd.read_csv(file_name, encoding='utf-8', encoding_errors='ignore')
    list2 = source_data.values.tolist()
    return list2


def comineCVS_digikey():
    fold = '/Users/liuhe/Desktop/重点系列/'
    list_file = os.listdir(fold)  # 返回指定目录
    result = []
    firt_row = ['制造商零件编号', '制造商', '描述', '库存', '价格', 'status', 'kind']
    result.append(firt_row)
    for temp_file in list_file:
        if temp_file.__contains__('.csv'):
            sheet_content = read_sheet_content(f"{fold}{temp_file}")
            for row in sheet_content:
                new_row = [row[3], row[4], row[6], row[7], row[8], row[13], temp_file[0:2]]
                result.append(new_row)
    ExcelHelp.add_arr_to_sheet(file_name=f'{fold}TManuAndSeri.xlsx', sheet_name='ppn', dim_arr=result)


if __name__ == '__main__':
    source_file = "/Users/liuhe/Downloads/20241112_tfiber_xlsx.csv"
    save_file = PathHelp.get_file_path(None, 'TFiber.xlsx')
    octopart_file_arr(source_file, save_file)
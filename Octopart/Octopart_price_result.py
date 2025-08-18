import time

from WRTools import ExcelHelp, LogHelper, PathHelp, WaitHelp, MySqlHelp_recommanded, EmailHelper, PandasHelp
import os

# 文件夹

# fold = '/Users/liuhe/Desktop/CalcitrapaAIProject/TRU2407/144H/'
# save_file = PathHelp.get_file_path(None, 'TManuAndSeri_252H.xlsx') # f'{fold}TRU2405.xlsx'
def octopart_fold_csv_xlsx(fold, save_file):
    list_file = os.listdir(fold)  # 返回指定目录
    result = []
    firt_row = ['制造商零件编号', '制造商', '描述','供应商', '价格', '库存']
    result.append(firt_row)
    for temp_file in list_file:
        if temp_file.__contains__('.csv'):
            sheet_content = PandasHelp.read_sheet_content(f"{fold}{temp_file}")
            index_price = searchLowestIndex(f"{fold}{temp_file}")
            for (index, row) in enumerate(sheet_content):
                new_row = [row[0], row[2], row[5], row[index_price], row[index_price+3], row[index_price+6]]
                result.append(new_row)
    ExcelHelp.add_arr_to_sheet(file_name=save_file, sheet_name='octopart', dim_arr=result)


# 只有1个文件
def octopart_file_arr(source_file, save_file):
    result = []
    firt_row = ['制造商零件编号', '制造商', '描述', '供应商', '价格', '库存']
    result.append(firt_row)
    index_price = searchLowestIndex(source_file)
    if source_file.__contains__('.csv'):
        sheet_content = PandasHelp.read_sheet_content(source_file)
        for (index, row) in enumerate(sheet_content):
            new_row = [row[0], row[2], row[5], row[index_price], row[index_price+3], row[index_price+6]]
            result.append(new_row)
    ExcelHelp.add_arr_to_sheet(file_name=save_file, sheet_name='octopart', dim_arr=result)


def searchLowestIndex(source_file):
    titles = PandasHelp.read_title(source_file)
    for (index, row) in enumerate(titles):
        if row == 'Distributor [Lowest Price (Preferred Distributors)]':
            return index
    else:
        return 0


def read_record(save_file, task_name):
    record = MySqlHelp_recommanded.DBRecommandChip().octopart_market_read(f'task_name = "{task_name}"')
    ExcelHelp.add_arr_to_sheet(save_file, 'octopart', record)


if __name__ == "__main__":
    aim_file = PathHelp.get_file_path(None, 'TRenesasIsolators.xlsx')
    task_name = 'TRenesasIsolators'
    read_record(aim_file, task_name)

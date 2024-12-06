import time

from WRTools import ExcelHelp, LogHelper, PathHelp, WaitHelp, MySqlHelp_recommanded, EmailHelper, PandasHelp
import os


# 将cvs 中的内容保存到t_octopart_price 中
# def getData_fromCVS():
#     fold = '/Users/liuhe/Desktop/progress/TRuStock/2023.09/'
#     list_file = os.listdir(fold)  # 返回指定目录
#     result = []
#     for temp_file in list_file:
#         if temp_file.__contains__('.csv'):
#             sheet_content = PandasHelp.read_sheet_content(f"{fold}{temp_file}")
#             title_row = PandasHelp.read_title(f"{fold}{temp_file}")
#             supplier_row = sheet_content[0]
#             sku_indexs = []
#             stock_indexs = []
#             moq_indexs = []
#             price_indexs = []
#             for (cell_index, cell_value) in enumerate(title_row):
#                 if cell_value.startswith('SKU.') or cell_value == 'SKU':
#                     sku_indexs.append(cell_index)
#                 elif cell_value.startswith('MOQ.') or cell_value == 'MOQ':
#                     moq_indexs.append(cell_index)
#                 elif cell_value.startswith('In Stock') or cell_value == 'In Stock':
#                     stock_indexs.append(cell_index)
#                 elif str(cell_value).startswith('Unit Price') or cell_value == 'Unit Price':
#                     price_indexs.append(cell_index)
#             for (row_index, row) in enumerate(sheet_content):
#                 if row_index <= 0 :
#                     continue
#                 for (sku_sub_index, sku_sub) in enumerate(sku_indexs):
#                     if (row[sku_sub] is not None) and str(row[sku_sub]) != 'nan':
#                         new_row = [row[3], row[2], 1, str(supplier_row[sku_sub]), str(row[sku_sub]),
#                                    str(row[stock_indexs[sku_sub_index]]),
#                                    str(row[moq_indexs[sku_sub_index]]), 'USD', str(row[price_indexs[sku_sub_index]]), '--',
#                                    row[0], TaskManager.Taskmanger.task_name()
#                                    ]
#                         result.append(new_row)
#             MySqlHelp_recommanded.DBRecommandChip().octopart_price_write(result)
#             print(f'finish file:{temp_file}')
#             time.sleep(220)


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


if __name__ == "__main__":
    source_file = "/Users/liuhe/Desktop/京创智通/询价2412/octopart/"
    save_file = PathHelp.get_file_path(None, 'TRU202412.xlsx')
    octopart_fold_csv_xlsx(source_file, save_file)
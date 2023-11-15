import time

from WRTools import ExcelHelp, LogHelper, PathHelp, WaitHelp, MySqlHelp_recommanded, EmailHelper, PandasHelp
from  Manager import TaskManager
import os


# 将cvs 中的内容保存到t_octopart_price 中
def getData_fromCVS():
    fold = '/Users/liuhe/Desktop/progress/TRuStock/2023.09/'
    list_file = os.listdir(fold)  # 返回指定目录
    result = []
    for temp_file in list_file:
        if temp_file.__contains__('.csv'):
            sheet_content = PandasHelp.read_sheet_content(f"{fold}{temp_file}")
            title_row = PandasHelp.read_title(f"{fold}{temp_file}")
            supplier_row = sheet_content[0]
            sku_indexs = []
            stock_indexs = []
            moq_indexs = []
            price_indexs = []
            for (cell_index, cell_value) in enumerate(title_row):
                if cell_value.startswith('SKU.') or cell_value == 'SKU':
                    sku_indexs.append(cell_index)
                elif cell_value.startswith('MOQ.') or cell_value == 'MOQ':
                    moq_indexs.append(cell_index)
                elif cell_value.startswith('In Stock') or cell_value == 'In Stock':
                    stock_indexs.append(cell_index)
                elif str(cell_value).startswith('Unit Price') or cell_value == 'Unit Price':
                    price_indexs.append(cell_index)
            for (row_index, row) in enumerate(sheet_content):
                if row_index <= 0 :
                    continue
                for (sku_sub_index, sku_sub) in enumerate(sku_indexs):
                    if (row[sku_sub] is not None) and str(row[sku_sub]) != 'nan':
                        new_row = [row[3], row[2], 1, str(supplier_row[sku_sub]), str(row[sku_sub]),
                                   str(row[stock_indexs[sku_sub_index]]),
                                   str(row[moq_indexs[sku_sub_index]]), 'USD', str(row[price_indexs[sku_sub_index]]), '--',
                                   row[0], TaskManager.Taskmanger.task_name()
                                   ]
                        result.append(new_row)
            MySqlHelp_recommanded.DBRecommandChip().octopart_price_write(result)
            print(f'finish file:{temp_file}')
            time.sleep(220)


# [self.cate or "--", self.manu or "--", self.is_star, self.distribute, self.SKU, self.stock, self.MOQ,
#                   self.currency_type='USD', self.k_price, self.updated]
if __name__ == "__main__":
    getData_fromCVS()
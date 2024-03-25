# 计算cate
# 输入型号，爬取现货排名和ICCP和SSCP的库存数据，输出两个字段：
# （1） 靠谱供应商数量（ICCP+SSCP）
# （2） 靠谱库存数量（[现货排名库存总量+非现货排名ICCP库存总量+非现货排名SSCP库存总量]/6)

from openpyxl import workbook, load_workbook, Workbook
import base64
import IC_stock.IC_Stock_Info
import time
from WRTools import PathHelp, ExcelHelp, MySqlHelp_recommanded
from Manager import TaskManager

# IC_source_file = PathHelp.get_file_path('TVicor15H', 'IC_stock.xlsx')
cate_source_file = PathHelp.get_file_path(None, 'TLK240320.xlsx') #PathHelp.get_file_path(None, '/Users/liuhe/Downloads/TTIMilitary.xlsx')
result_save_file = cate_source_file


# 将同一个ppn到所有stock 累加，然后按照保存到数组中, 没有数据的，用/填充
def IC_stock_sum():
    pps = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn', col_index=1)
    manufactures = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn', col_index=2)
    result = []
    for (index, temp_ppn) in enumerate(pps):
        ppn_str = str(temp_ppn)
        valid_supplier_sum = 0
        valid_stock_sum = 0
        IC_stocks = ExcelHelp.read_sheet_content_by_name(cate_source_file, sheet_name='IC_stock')
        # (ppn	st_manu	supplier_manu	supplier	isICCP	isSSCP	iSRanking	isHotSell	isYouXian	batch	pakaging	stock_num	task_name	update_time)
        for (row_index, row_content) in enumerate(IC_stocks):
            ppn_ic = str(row_content[0])
            if ppn_ic.upper() == ppn_str.upper():
                isICCP = str(row_content[4]) == "1"
                isSSCP = str(row_content[5]) == "1"
                isSpotRanking = str(row_content[6]) == "1"
                stock_num = int(row_content[11])
                # if isSSCP or isICCP or isSpotRanking or isHotSell or isYouXian:
                if isSSCP or isICCP or isSpotRanking:
                    valid_supplier_sum += 1
                    valid_stock_sum += stock_num
        result.append([ppn_str, manufactures[index], valid_supplier_sum, int(valid_stock_sum)])
    ExcelHelp.add_arr_to_sheet(file_name=cate_source_file, sheet_name="IC_stock_sum", dim_arr=result)


def adjust():
    cate_source_file = PathHelp.get_file_path(None, 'TRuStock.xlsx')
    row_content = ExcelHelp.read_sheet_content_by_name(file_name=cate_source_file, sheet_name='IC_stock_sum')
    result = []
    for temp_row in row_content:
        row_value = [temp_row[0], temp_row[1], temp_row[2], temp_row[3]*6]
        result.append(row_value)
    ExcelHelp.add_arr_to_sheet(file_name=cate_source_file, sheet_name="IC_stock_sum2", dim_arr=result)


def printPPN():
    ppn = ExcelHelp.read_col_content('/Users/liuhe/Desktop/progress/TRuStock/2023.09/hxl.xlsx', 'Sheet1', col_index=1)
    print(ppn)


def addIC_info():
    sheet_content = ExcelHelp.read_sheet_content_by_name('/Users/liuhe/Desktop/progress/TRuStock/2023.09/hxl.xlsx', 'Sheet1')
    bom_price_info  =ExcelHelp.read_sheet_content_by_name('/Users/liuhe/Desktop/progress/TRuStock/2023.09/hxl.xlsx', 'Sheet2')
    result_arr = []
    for (row_idnex, row) in enumerate(sheet_content):
        ppn = row[0]
    ExcelHelp.add_arr_to_sheet('/Users/liuhe/Desktop/progress/TRuStock/2023.09/hxl.xlsx', 'Sheet5', result_arr)


if __name__ == "__main__":
    IC_stock_sum()
    print('over')

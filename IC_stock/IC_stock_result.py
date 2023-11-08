# 计算cate
# 输入型号，爬取现货排名和ICCP和SSCP的库存数据，输出两个字段：
# （1） 靠谱供应商数量（ICCP+SSCP）
# （2） 靠谱库存数量（[现货排名库存总量+非现货排名ICCP库存总量+非现货排名SSCP库存总量]/6)

from openpyxl import workbook, load_workbook, Workbook
import base64
import IC_stock.IC_Stock_Info
import time
from WRTools import PathHelp, ExcelHelp, MySqlHelp_recommanded

cate_source_file = PathHelp.get_file_path("Renesas_all_165H", 'Task.xlsx')
ICStock_file_arr = ["/Users/liuhe/Desktop/progress/TVicor/15H/11/IC_stock.xlsx",
                    "/Users/liuhe/Desktop/progress/TVicor/15H/sz/IC_stock.xlsx",
                    "/Users/liuhe/Desktop/progress/TVicor/15H/04/IC_stock.xlsx",
                    PathHelp.get_file_path('TVicor15H', 'IC_stock.xlsx')]
IC_source_file = PathHelp.get_file_path('TVicor15H', 'IC_stock.xlsx')
result_save_file = cate_source_file


# 将同一个ppn到所有stock 累加，然后按照保存到数组中, 没有数据的，用/填充
def IC_stock_sum():
    cate_source_file = PathHelp.get_file_path(None, 'TMitsubishi.xlsx')
    pps = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn', col_index=1)
    manufactures = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn', col_index=3)
    result = []
    for (index, temp_ppn) in enumerate(pps):
        ppn_str = str(temp_ppn)
        valid_supplier_sum = 0
        valid_stock_sum = 0
        IC_stocks = MySqlHelp_recommanded.DBRecommandChip().ic_stock_read(("update_time > '2023/10/28'"))
        # (`ppn`, `manu`, `supplier`, `isICCP`, `isSSCP`, `iSRanking`, `isHotSell`, `stock_num`, `update_time`)
        # IC_stocks = ExcelHelp.read_sheet_content_by_name(file_name=IC_source_file, sheet_name='IC_stock')
        for row_content in IC_stocks:
            ppn_ic = str(row_content[0])
            if ppn_ic == ppn_str:
                manufacturer = str(row_content[1])
                supplier = str(row_content[2])
                isICCP = str(row_content[3]) == "1"
                isSSCP = str(row_content[4]) == "1"
                isSpotRanking = str(row_content[5]) == "1"
                isHotSell = str(row_content[6]) == "1"
                stock_num = int(row_content[7])
                if isSSCP or isICCP or isSpotRanking:
                    valid_supplier_sum += 1
                    valid_stock_sum += stock_num
                    print(row_content)
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


if __name__ == "__main__":
    # combine_result(source_files=ICStock_file_arr, aim_file=IC_source_file)
    IC_stock_sum()
    print('over')




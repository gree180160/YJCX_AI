# 计算cate
# 输入型号，爬取现货排名和ICCP和SSCP的库存数据，输出两个字段：
# （1） 靠谱供应商数量（ICCP+SSCP）
# （2） 靠谱库存数量（[现货排名库存总量+非现货排名ICCP库存总量+非现货排名SSCP库存总量]/6)

from openpyxl import workbook, load_workbook, Workbook
import base64
import IC_stock.IC_Stock_Info
import time
from WRTools import PathHelp, ExcelHelp

cate_source_file = PathHelp.get_file_path("Renesas_MCU_115H", 'Task.xlsx')
ICStock_file_arr = ["/Users/liuhe/Desktop/progress/TRenesas_MCU/Renesas_MCU_115H/11/IC_stock.xlsx",
                    "/Users/liuhe/Desktop/progress/TRenesas_MCU/Renesas_MCU_115H/sz/IC_stock.xlsx",
                    "/Users/liuhe/Desktop/progress/TRenesas_MCU/Renesas_MCU_115H/04/IC_stock.xlsx",
                    PathHelp.get_file_path('TRenesas_MCU_115H', 'IC_stock.xlsx')]
IC_source_file = PathHelp.get_file_path('TRenesas_MCU_115H', 'IC_stock.xlsx')
result_save_file = cate_source_file


# 将同一个ppn到所有stock 累加，然后按照保存到数组中, 没有数据的，用/填充
def IC_stock_sum(IC_source_file: str, cate_source_file):
    pps = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn', col_index=1)
    manufactures = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn', col_index=2)
    result = []
    for (index, temp_ppn) in enumerate(pps):
        ppn_str = str(temp_ppn)
        valid_supplier_sum = 0
        valid_stock_sum = 0
        IC_stocks = ExcelHelp.read_sheet_content_by_name(file_name=IC_source_file, sheet_name='IC_stock')
        for row_content in IC_stocks:
            ppn_ic = str(row_content[0])
            if ppn_ic == ppn_str:
                manufacturer = str(row_content[1])
                supplier = str(row_content[2])
                iccp_str = str(row_content[3])
                isICCP = "notICCP" not in iccp_str
                sscp_str = str(row_content[4])
                isSSCP = "notSSCP" not in sscp_str
                isSpotRanking = "notSpotRanking" not in str(row_content[5])
                isHotSell = "notHotSell" not in str(row_content[5])
                stock_num = int(row_content[7])
                search_date = str(row_content[8])
                ic_Stock_Info = IC_stock.IC_Stock_Info.IC_Stock_Info(supplier=supplier, isICCP=isICCP, isSSCP=isSSCP,
                                                                     model=ppn_str,
                                                                     isSpotRanking=isSpotRanking, isHotSell=isHotSell,
                                                                     manufacturer=manufacturer, stock_num=stock_num,
                                                                     search_date=search_date)
                if ic_Stock_Info.is_valid_supplier():
                    valid_supplier_sum += 1
                    valid_stock_sum += ic_Stock_Info.get_valid_stock_num()
        result.append([ppn_str, manufactures[index], valid_supplier_sum, int(valid_stock_sum / 6)])
    ExcelHelp.add_arr_to_sheet(file_name=cate_source_file, sheet_name="IC_stock_sum", dim_arr=result)


def combine_result(source_files:[], aim_file):
    for temp in source_files:
        ExcelHelp.mergeSheet(temp, aim_sheet='IC_stock')
        if temp != aim_file:
            data = ExcelHelp.read_sheet_content_by_name(file_name=temp, sheet_name='IC_stock')
            ExcelHelp.add_arr_to_sheet(file_name=aim_file, sheet_name='IC_stock', dim_arr=data)
            time.sleep(2.0)


if __name__ == "__main__":
    combine_result(source_files=ICStock_file_arr, aim_file=IC_source_file)
    IC_stock_sum(IC_source_file, cate_source_file)




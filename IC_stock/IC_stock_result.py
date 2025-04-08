# 计算cate
# 输入型号，爬取现货排名和ICCP和SSCP的库存数据，输出两个字段：
# （1） 靠谱供应商数量（ICCP+SSCP）
# （2） 靠谱库存数量（[现货排名库存总量+非现货排名ICCP库存总量+非现货排名SSCP库存总量]/6)
import time

from WRTools import PathHelp, ExcelHelp, MySqlHelp_recommanded
import re
import os
# IC_source_file = PathHelp.get_file_path('TVicor15H', 'IC_stock.xlsx')
# cate_source_file = PathHelp.get_file_path(None, 'TLK240322.xlsx')


# 将同一个ppn到所有stock 累加，然后按照保存到数组中, 没有数据的，用/填充
def IC_stock_sum(cate_source_file):
    pps = ExcelHelp.read_col_content(file_name= cate_source_file, sheet_name='ppn3', col_index=1)
    manufactures = ExcelHelp.read_col_content(file_name= cate_source_file, sheet_name='ppn3', col_index=2)
    result = []
    for (index, temp_ppn) in enumerate(pps):
        ppn_str = str(temp_ppn)
        if ppn_str == 'ppn':
            continue
        valid_supplier_sum = 0
        rank_sum = 0
        valid_stock_sum = 0
        IC_stocks = ExcelHelp.read_sheet_content_by_name(cate_source_file, sheet_name='IC_stock')
        # (ppn,st_manu,supplier_ppn, supplier_manu,supplier,isICCP,isSSCP,iSRanking,isHotSell,isYouXian,batch,pakaging,stock_num,task_name,update_time)
        max_stock = 0 # 保留库存最大的供应商的所有信息
        max_info = []
        for (row_index, row_content) in enumerate(IC_stocks):
            ppn_ic = str(row_content[0])
            if ppn_ic.upper() == ppn_str.upper():
                isICCP = str(row_content[5]) == "1"
                isSSCP = str(row_content[6]) == "1"
                isSpotRanking = str(row_content[7]) == "1"
                stock_num = int(row_content[12])
                if stock_num > max_stock:
                    max_stock = stock_num
                    sup_manu = ruleManu(row_content[3], row_content[1])
                    max_info = [row_content[2], sup_manu, row_content[4], row_content[10], row_content[11], row_content[12]]
                # if isSSCP or isICCP or isSpotRanking or isHotSell or isYouXian:
                if isSSCP or isICCP or isSpotRanking:
                    if stock_num < 10:
                        valid_supplier_sum = round(valid_supplier_sum+0.01, 2)
                    else:
                        valid_supplier_sum = round(valid_supplier_sum+1.0, 2)
                    valid_stock_sum += stock_num
                    if isSpotRanking:
                        if stock_num < 10:
                            rank_sum = round(rank_sum+0.01, 2)
                        else:
                            rank_sum = round(rank_sum+1.0, 2)
        result.append([ppn_str, manufactures[index], valid_supplier_sum, rank_sum, int(valid_stock_sum)] + max_info)
    ExcelHelp.add_arr_to_sheet(file_name=cate_source_file, sheet_name="IC_stock_sum", dim_arr=result)


def ruleManu(input_string, st_manu):
    # if input_string == '--':
    #     return st_manu
    # 1. 删除 “/中文字”
    cleaned = re.sub(r'/[\u4e00-\u9fff]+', '', input_string)
    # 2. 删除 “(中文字)”
    cleaned = re.sub(r'\(（[\u4e00-\u9fff]+）\)', '', cleaned)
    # 3. 删除 “（中文字）”
    cleaned = re.sub(r'（[\u4e00-\u9fff]+）', '', cleaned)
    # 4. 删除 “(中文字)”
    cleaned = re.sub(r'\([\u4e00-\u9fff]+\)', '', cleaned)
    # 5. 删除字母后面的汉字
    cleaned = re.sub(r'[\u4e00-\u9fff]+', '', cleaned)
    return cleaned.strip()


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


def read_record(save_file, task_name):
    record = MySqlHelp_recommanded.DBRecommandChip().ic_stock_read(f'task_name = "{task_name}"')
    ExcelHelp.add_arr_to_sheet(save_file, 'IC_stock', record)


if __name__ == "__main__":
    aim_file = PathHelp.get_file_path(None, 'TNXPCircutProtect.xlsx')
    task_name = 'TNXPCircutProtect'
    read_record(aim_file, task_name)
    IC_stock_sum(aim_file)
    print('over')

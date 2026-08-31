# 将findchips 数据， IC——Stock， IC-Hot， price 合并到一个excel到all_info 中
import time
from WRTools import ExcelHelp, PathHelp
from IC_stock import IC_stock_result
from HQSearch import HQHotResult
from Findchips_stock import findchips_stock_cate
import IC_Search.IC_search_Image
import Statistic_data.statistic_price_sheet
from Bom_price import BomResult
import os

# ------------findchip----------------------
# 将临时保存的数据转移到汇总数据到excel
def findchips_move_data(source_file: str, source_sheet: str, aim_file: str, aim_sheet):
    ExcelHelp.move_sheet_to_row(source_file_list=[source_file], source_sheet=source_sheet, aim_file=aim_file, aim_sheet=aim_sheet)


def move_part_to_part(source_file: str,
                      source_sheet: str,
                      from_col: int,
                      to_col: int,
                      aim_file: str,
                      aim_sheet: str,
                      start_col: int):
    source_data = ExcelHelp.read_from_col_to_col(file_name=source_file, sheet_name=source_sheet, from_col=from_col, to_col=to_col)
    ExcelHelp.save_one_col(file_name=aim_file, sheet_name=aim_sheet, col_index=start_col, dim_arr=source_data, skip_row_count=1)


# 联科Task
def lkResult(rate):
    source_file = PathHelp.get_file_path("LiChuang", 'TLCClearance.xlsx')
    # HQHotResult.HQ_hot_result(source_file)
    # time.sleep(1.0)
    # IC_stock_result.IC_stock_sum(source_file)
    # time.sleep(1.0)
    # BomResult.bom_price_result(source_file)
    # time.sleep(1.0)
    first_row = ["型号", "品牌", "库存", "批次", "价格", "货期", "SPQ", "IC_supplier", "IC_rank", "IC_stock", "HQ_hot_week", 'HQ_hot_month', 'HQ_hot_avg', 'HQ_hot_result', 'oc_price', 'oc_stock', 'oc_supplier', 'oc_des', 'bom_price', 'IC_hot', 'IC_price',  'result']
    result = []
    result.append(first_row)
    try:
        source_info = ExcelHelp.read_sheet_content_by_name(source_file, 'source')
    except:
        source_info = []
    IC_info = ExcelHelp.read_sheet_content_by_name(source_file, 'IC_stock_sum')
    try:
        HQ_hot_info = ExcelHelp.read_sheet_content_by_name(source_file, 'HQ_hot_result')
    except:
        HQ_hot_info = []
    oc_info = ExcelHelp.read_sheet_content_by_name(source_file, 'octopart')
    bom_info = ExcelHelp.read_sheet_content_by_name(source_file, 'zhengnengliang_price_sum')
    ppns_info = ExcelHelp.read_sheet_content_by_name(source_file, 'ppn4')   # 先过滤HQ_hot_合格的ppn
    for (index, temp_ppnInfo) in enumerate(ppns_info):
        ppn_result = [temp_ppnInfo[0], temp_ppnInfo[1]]
        for temp_source in source_info:
            if temp_source[0] == temp_ppnInfo[0]:
                ppn_result += [temp_source[i] if i < len(temp_source) else '' for i in range(2, 7)]  # [temp_source[2], temp_ppnInfo[3], temp_ppnInfo[4], temp_source[5], temp_source[6]]
        for temp_IC in IC_info:
            if temp_IC[0] == temp_ppnInfo[0]:
                ppn_result += [temp_IC[2], temp_IC[3], temp_IC[4]]
        for temp_HQ in HQ_hot_info:
            if temp_HQ[0] == temp_ppnInfo[0]:
                ppn_result += [temp_HQ[2], temp_HQ[3], temp_HQ[4] , temp_HQ[5]]
        for temp_OC in oc_info:
            if temp_OC[0] == temp_ppnInfo[0]:
                try:
                    oc_price = round(float(temp_OC[4]) * rate, 2)
                except:
                    oc_price = ""
                ppn_result += [oc_price, temp_OC[5], temp_OC[3], temp_OC[2]]
                break;
        for temp_bom in bom_info:
            if temp_bom[0] == temp_ppnInfo[0]:
                ppn_result += [temp_bom[2]]
                break;
        result.append(ppn_result)
    ExcelHelp.add_arr_to_sheet(source_file, "LKResult", result)


# IC拍卖
def ICAuction():
    source_file = PathHelp.get_file_path(None, 'TICAuction240429.xlsx')
    HQHotResult.HQ_hot_result(source_file)
    time.sleep(1.0)
    IC_stock_result.IC_stock_sum(source_file)
    time.sleep(1.0)
    first_row = ["型号", "品牌", "库存", "批次", "价格", "IC_supplier","IC_rank", "IC_stock", "HQ_hot_week", 'HQ_hot_month', 'HQ_hot_avg', 'HQ_hot_result', '¥oc_price¥', 'oc_stock', 'oc_supplier', 'oc_des', 'IC_hot', 'IC_price', 'bom_price', 'result']
    result = []
    result.append(first_row)
    source_info = ExcelHelp.read_sheet_content_by_name(source_file, 'auction')
    IC_info = ExcelHelp.read_sheet_content_by_name(source_file, 'IC_stock_sum')
    HQ_hot_info = ExcelHelp.read_sheet_content_by_name(source_file, 'HQ_hot_result')
    oc_info = ExcelHelp.read_sheet_content_by_name(source_file, 'octopart')
    ppns_info = ExcelHelp.read_sheet_content_by_name(source_file, 'ppn')   # 先过滤HQ_hot_合格的ppn
    for (index, temp_ppnInfo) in enumerate(ppns_info):
        ppn_result = [temp_ppnInfo[0], temp_ppnInfo[1]]
        for temp_source in source_info:
            if temp_source[0] == temp_ppnInfo[0]:
                ppn_result += [temp_source[i] if i < len(temp_source) else '' for i in range(2, 5)]  # [temp_source[2], temp_ppnInfo[3], temp_ppnInfo[4], temp_source[5]]
        for temp_IC in IC_info:
            if temp_IC[0] == temp_ppnInfo[0]:
                ppn_result += [temp_IC[2], temp_IC[3], temp_IC[4]]
        for temp_HQ in HQ_hot_info:
            if temp_HQ[0] == temp_ppnInfo[0]:
                ppn_result += [temp_HQ[2], temp_HQ[3], temp_HQ[4], temp_HQ[5]]
        for temp_OC in oc_info:
            if temp_OC[0] == temp_ppnInfo[0]:
                ppn_result += [temp_OC[4], temp_OC[5], temp_OC[3], temp_OC[2]]
        result.append(ppn_result)
    ExcelHelp.add_arr_to_sheet(source_file, "auction_result", result)


#  HQ_hot, HQ_stock , IC_stock
def HQ_simple(save_file, ppn_sheet):
    source_file = save_file
    first_row = ["型号", "品牌","IC_supplier","IC_rank", "IC_stock", "IC_maxStock_supplier", "supplier_batch",
                 "HQ_supplier", "HQ_stock", "HQ_hot_week", 'HQ_hot_month', 'last_month', 'HQ_hot_avg', 'HQ_hot_result',
                 'digikey_des','digikey_status']
    result = []
    result.append(first_row)
    try:
        HQ_stock_info = ExcelHelp.read_sheet_content_by_name(source_file, 'HQ_stock_sum')
    except:
        HQ_stock_info = []
    try:
        HQ_hot_info = ExcelHelp.read_sheet_content_by_name(source_file, 'HQ_hot_result')
    except:
        HQ_hot_info = []
    try:
        IC_info = ExcelHelp.read_sheet_content_by_name(source_file, 'IC_stock_sum')
    except:
        IC_info = []
    try:
        dg_info = ExcelHelp.read_sheet_content_by_name(source_file, 'source') # or digikey
    except:
        dg_info = []
    ppns_info = ExcelHelp.read_sheet_content_by_name(source_file, ppn_sheet)  # 先过滤HQ_hot_合格的ppn
    for (index, temp_ppnInfo) in enumerate(ppns_info):
        ppn_result = [temp_ppnInfo[0], temp_ppnInfo[1], ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
                      ' ', ' ', ' ', ' ', ' ', ' ']
        for temp_IC in IC_info:
            if temp_IC[0] == temp_ppnInfo[0]:
                start = 2
                ppn_result[start] = temp_IC[2]
                ppn_result[start + 1] = temp_IC[3]
                ppn_result[start + 2] = temp_IC[4]
                ppn_result[start + 3] = temp_IC[7] if len(temp_IC) > 7 and temp_IC[7] is not None else ''
                ppn_result[start + 4] = temp_IC[8] if len(temp_IC) > 8 and temp_IC[8] is not None else ''
                break;
        for temp_hqStock in HQ_stock_info:
            if temp_hqStock[0] == temp_ppnInfo[0]:
                start = 7
                ppn_result[start] = temp_hqStock[2]
                ppn_result[start + 1] = temp_hqStock[3]
                break;
        for temp_HQ in HQ_hot_info:
            if temp_HQ[0] == temp_ppnInfo[0]:
                start = 9
                ppn_result[start] = temp_HQ[3]
                ppn_result[start + 1] = temp_HQ[4]
                ppn_result[start + 2] = temp_HQ[5]
                ppn_result[start + 3] = temp_HQ[6]
                ppn_result[start + 4] = temp_HQ[7]
                break;
        for temp_dg in dg_info:
            if temp_dg[0] == temp_ppnInfo[0]: # digikey 状态来自jason的原始文件
                start = 14
                if temp_dg.__len__() > 3:
                    ppn_result[start] = temp_dg[3]
                ppn_result[start + 1] = temp_dg[2]
                break;
        result.append(ppn_result)
    ExcelHelp.add_arr_to_sheet(save_file, "Result", result)
    time.sleep(3.0)
    ExcelHelp.set_col_width(save_file, 'Result', 14.0)


def IC_HQ_Result2(save_file, rate, ppn_sheet):
    source_file = save_file
    first_row = ["型号", "品牌","IC_supplier","IC_rank", "IC_stock", "IC_maxStock_supplier", "supplier_batch",
                 "efind_allSup","efind_priceSup", "efind_stockSup","wheat_global", "wheat_ru",
                 "HQ_supplier", "HQ_stock", "HQ_hot_week", 'HQ_hot_month', 'last_month', 'HQ_hot_avg', 'HQ_hot_result',
                 'oc_price', 'oc_stock','oc_supplier', 'digikey_des','digikey_status', 'bom_price','bom_supplier', 'future_leadT', 'arrow_leadT'
                 'IC_hot_max', 'IC_hot_min','IC_hot_avg', 'IC_price',  'result']
    result = []
    result.append(first_row)
    IC_info = ExcelHelp.read_sheet_content_by_name(source_file, 'IC_stock_sum')
    try:
        HQ_stock_info = ExcelHelp.read_sheet_content_by_name(source_file, 'HQ_stock_sum')
    except:
        HQ_stock_info = []
    try:
        HQ_hot_info = ExcelHelp.read_sheet_content_by_name(source_file, 'HQ_hot_result')
    except:
        HQ_hot_info = []
    try:
        oc_info = ExcelHelp.read_sheet_content_by_name(source_file, 'octopart')
    except:
        oc_info = []
    try:
        dg_info = ExcelHelp.read_sheet_content_by_name(source_file, 'digikey')
    except:
        dg_info = []
    try:
        efind_info = ExcelHelp.read_sheet_content_by_name(source_file, 'efind_supplier')
    except:
        efind_info = []
    try:
        wheat_info = ExcelHelp.read_sheet_content_by_name(source_file, 'wheat_record')
    except:
        wheat_info = []
    try:
        future_info = ExcelHelp.read_sheet_content_by_name(source_file, 'future')
    except:
        future_info = []
    try:
        arrow_info = ExcelHelp.read_sheet_content_by_name(source_file, 'arrow')
    except:
        arrow_info = []
    bom_info = ExcelHelp.read_sheet_content_by_name(source_file, 'zhengnengliang_price_sum')
    ppns_info = ExcelHelp.read_sheet_content_by_name(source_file, ppn_sheet)   # 先过滤HQ_hot_合格的ppn
    for (index, temp_ppnInfo) in enumerate(ppns_info):
        ppn_result = [temp_ppnInfo[0], temp_ppnInfo[1], ' ', ' ', ' ',' ', ' ', ' ',' ',' ',
                      ' ', ' ', ' ', ' ', ' ',' ',' ',' ',' ', ' ',
                      ' ', ' ', ' ', ' ', ' ',' ',
                      ' ', ' ', '', '', '', '', '']
        for temp_IC in IC_info:
            if temp_IC[0] == temp_ppnInfo[0]:
                start = 2
                ppn_result[start] = temp_IC[2]
                ppn_result[start+1] = temp_IC[3]
                ppn_result[start+2] = temp_IC[4]
                ppn_result[start+3] = temp_IC[7] if len(temp_IC) > 7 and temp_IC[7] is not None else ''
                ppn_result[start+4] = temp_IC[8] if len(temp_IC) > 8 and temp_IC[8] is not None else ''
                break;
        for temp_efind in efind_info:
            if temp_efind[0] == temp_ppnInfo[0]:
                start = 7
                ppn_result[start] = temp_efind[2]
                ppn_result[start+1] = temp_efind[3]
                ppn_result[start+2] = temp_efind[4]
                break;
        for temp_wheat in wheat_info:
            if temp_wheat[0] == temp_ppnInfo[0]:
                start = 10
                ppn_result[start] = temp_wheat[1]
                ppn_result[start+1] = temp_wheat[2]
                break;
        for temp_hqStock in HQ_stock_info:
            if temp_hqStock[0] == temp_ppnInfo[0]:
                start = 12
                ppn_result[start] = temp_hqStock[2]
                ppn_result[start+1] = temp_hqStock[3]
                break;
        for temp_HQ in HQ_hot_info:
            if temp_HQ[0] == temp_ppnInfo[0]:
                start = 14
                ppn_result[start] = temp_HQ[3]
                ppn_result[start+1] = temp_HQ[4]
                ppn_result[start+2] = temp_HQ[5]
                ppn_result[start+3] = temp_HQ[6]
                ppn_result[start+4] = temp_HQ[7]
                break;
        for temp_OC in oc_info:
            if temp_OC[7] == temp_ppnInfo[0]:
                try:
                    tax = 1.13
                    oc_price = round(float(temp_OC[6]) * rate, 2)
                except:
                    oc_price = ""
                start = 19
                ppn_result[start] = oc_price
                ppn_result[start+1] = temp_OC[4]
                ppn_result[start+2] = temp_OC[3]
                break;
        for temp_dg in dg_info:
            if temp_dg[0] == temp_ppnInfo[0]: # digikey 状态来自jason的原始文件
                ppn_result[22] = temp_dg[3]
                ppn_result[23] = temp_dg[2]
                break;
        for temp_bom in bom_info:
            if temp_bom[0] == temp_ppnInfo[0]:
                start = 24
                if temp_bom.__len__() > 2:
                    ppn_result[start] = temp_bom[2]
                    ppn_result[start+1] = temp_bom[3]
                else:
                    ppn_result[start] = ''
                    ppn_result[start+1] = ''
                break;
        for temp_future in future_info:
            if temp_future[2] == temp_ppnInfo[0]:
                start = 26
                ppn_result[start] = temp_future[6]
                break;
        for temp_arrow in arrow_info:
            if temp_arrow[3] == temp_ppnInfo[0]:
                start = 27
                ppn_result[start] = temp_arrow[5]
                break;
        result.append(ppn_result)
    ExcelHelp.add_arr_to_sheet(save_file, "Result", result)
    time.sleep(3.0)
    ExcelHelp.set_col_width(save_file, 'Result', 14.0)


def temp():
    result_file = PathHelp.get_file_path(None, 'TES_CO_TH.xlsx')
    result = []
    source_content = ExcelHelp.read_sheet_content_by_name(result_file, 'result')
    for source_row in source_content:
        row = [source_row[0], source_row[1], source_row[2], "", "", source_row[4], source_row[5], source_row[6]]
        price = str(source_row[3])
        if price.__contains__(">"):
            number = price.split(">")[0]
            per_price = price.split(">")[1]
        else:
            number = ''
            per_price = price
        row = [source_row[0], source_row[1], source_row[2], number, per_price, source_row[4], source_row[5], source_row[6]]
        result.append(row)
    ExcelHelp.add_arr_to_sheet(result_file, "result2", result)
    time.sleep(3.0)


def month_ave_20():
    source_fold = '/Users/liuhe/Desktop/京创智通/专项分析/Infineon/V2/'
    list_file = os.listdir(source_fold)  # 返回指定目录
    result = []
    for temp_file in list_file:
        if temp_file.__contains__('.xlsx'):
            task_file = (f"{source_fold}{temp_file}")
            content = ExcelHelp.read_sheet_content_by_name(task_file, 'HQ_hot_result')
            for temp_row in content:
                if temp_row.__len__() >= 8:
                    this_row = [temp_row[0], temp_row[1], temp_row[2], temp_row[3], temp_row[4], float(temp_row[6]), temp_row[7]]
                else:
                    this_row = [temp_row[0], temp_row[1], temp_row[2], temp_row[3], temp_row[4], float(temp_row[5]), temp_row[6]]
                result.append(this_row)

    result_file = PathHelp.get_file_path(None, 'TInfineonM20_V2.xlsx')
    ExcelHelp.add_arr_to_sheet(result_file, 'HQ_hot_result', result)


if __name__ == "__main__":
    aim_file = PathHelp.get_file_path(None, 'TBomHot.xlsx')
    # # IC_HQ_Result2(aim_file, 7.19, 'ppn2')
    HQ_simple(aim_file, 'ppn3')
    print('over')
    # month_ave_20()
    # temp()
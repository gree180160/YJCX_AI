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


# 将同一个ppn到所有stock 累加，然后按照保存到数组中, 没有数据的，用/填充
def findchips_stock_sum(source_file: str):
    pps = ExcelHelp.read_col_content(file_name=source_file, sheet_name='ppn', col_index=1)
    result = []
    for (index, temp_ppn) in enumerate(pps):
        ppn_info = [temp_ppn, '/']
        findchip_stocks = ExcelHelp.read_sheet_content_by_name(file_name=source_file, sheet_name='findchip_stock')
        for row_content in findchip_stocks:
            try:
                ppn = str(row_content[0])
            except:
                ppn = None
            if ppn:
                try:
                    stock = int(row_content[5])
                except:
                    stock = 0
                if ppn == temp_ppn:
                    # 第一条记录
                    if ppn_info[1] == '/':
                        ppn_info[1] = stock
                    else:
                        ppn_info[1] += stock

        result.append(ppn_info)
    ExcelHelp.add_arr_to_sheet(file_name=source_file, sheet_name="findchips_stock_sum", dim_arr=result)


# move part sheet_content to other sheet position
# 因为第一行为标题行，所有从第二行开始写入数据
def move_part_to_part(source_file: str,
                      source_sheet: str,
                      from_col: int,
                      to_col: int,
                      aim_file: str,
                      aim_sheet: str,
                      start_col: int):
    source_data = ExcelHelp.read_from_col_to_col(file_name=source_file, sheet_name=source_sheet, from_col=from_col, to_col=to_col)
    ExcelHelp.save_one_col(file_name=aim_file, sheet_name=aim_sheet, col_index=start_col, dim_arr=source_data, skip_row_count=1)


#   将ppn, manu 复制到all——info sheet 中
def move_ppn_to_allInfo(source_file: str):
    move_part_to_part(
        source_file=source_file,
        source_sheet='ppn',
        from_col=1,
        to_col=2,
        aim_file=source_file,
        aim_sheet='all_info',
        start_col=1)


#  将IC_supplier_count, IC_stock_count 复制到all——info sheet 中
def move_IC_stock_to_allInfo(source_file: str):
    move_part_to_part(
        source_file=source_file,
        source_sheet='IC_stock_sum',
        from_col=3,
        to_col=4,
        aim_file=source_file,
        aim_sheet='all_info',
        start_col=3)


#   将pm_record, pm,pr,grade,复制到all——info sheet 中
def move_BomOct_to_allInfo(source_file: str):
    # pm_record
    move_part_to_part(
        source_file=source_file,
        source_sheet='bom_octopart_price',
        from_col=7,
        to_col=8,
        aim_file=source_file,
        aim_sheet='all_info',
        start_col=5)
    # pm, pr
    move_part_to_part(
        source_file=source_file,
        source_sheet='bom_octopart_price',
        from_col=3,
        to_col=4,
        aim_file=source_file,
        aim_sheet='all_info',
        start_col=7)
    # grade
    move_part_to_part(
        source_file=source_file,
        source_sheet='bom_octopart_price',
        from_col=6,
        to_col=6,
        aim_file=source_file,
        aim_sheet='all_info',
        start_col=9)


#   将ppnd的stock sum, 复制到all——info sheet 中
def move_findchip_to_allInfo(source_file: str, findchip_file:str):
    findchip_file = findchip_file
    findchips_move_data(source_file=findchip_file, source_sheet='findchip_stock', aim_file=source_file, aim_sheet="findchip_stock")
    findchips_stock_sum(source_file=source_file)
    move_part_to_part(
        source_file=source_file,
        source_sheet='findchips_stock_sum',
        from_col=2,
        to_col=2,
        aim_file=source_file,
        aim_sheet='all_info',
        start_col=10)


# 结算IC—hot,并倒入all_info
def move_IC_hot(source_file: str):
    pps = ExcelHelp.read_col_content(file_name=source_file, sheet_name='ppn', col_index=1)
    week_data = ExcelHelp.read_sheet_content_by_name(file_name=source_file, sheet_name='IC_hot_week')
    week_record_ppns = ExcelHelp.read_col_content(file_name=source_file, sheet_name='IC_hot_week', col_index=1)
    month_data = ExcelHelp.read_sheet_content_by_name(file_name=source_file, sheet_name='IC_hot_month')
    month_record_ppns = ExcelHelp.read_col_content(file_name=source_file, sheet_name='IC_hot_month', col_index=1)
    all_ppn_hot = []
    for (index, temp_ppn) in enumerate(pps):
        if temp_ppn in week_record_ppns:
            value_index = week_record_ppns.index(temp_ppn)
            row_data = week_data[value_index]
            week_data_str_list = row_data[1:]
            week_data_int_list = []
            for cell_value in week_data_str_list:
                try:
                    week_data_int_list.append(int(cell_value))
                except:
                    print("move_IC_hot_week cell content error")
            first_week_value = week_data_int_list[0]
            week_data_int_list.sort()
            record_data = [temp_ppn, first_week_value, week_data_int_list[-1], week_data_int_list[-2], week_data_int_list[0]]
        else:
            record_data = [temp_ppn, "/", "/", "/", "/"]

        if temp_ppn in month_record_ppns:
            value_index = month_record_ppns.index(temp_ppn)
            row_data = month_data[value_index]
            month_data_str_list = row_data[1:]
            month_data_int_list = []
            for cell_value in month_data_str_list:
                try:
                    month_data_int_list.append(int(cell_value))
                except:
                    print("move_IC_hot_month cell content error")
            first_month_value = month_data_int_list[0]
            month_data_int_list.sort()
            record_data.append(first_month_value)
            record_data.append(month_data_int_list[-1])
            record_data.append(month_data_int_list[-2])
            record_data.append(month_data_int_list[0])
        else:
            record_data.append('/')
            record_data.append('/')
            record_data.append('/')
            record_data.append('/')
        all_ppn_hot.append(record_data)
    ExcelHelp.add_arr_to_sheet(file_name=source_file, sheet_name='IC_hot_sorted', dim_arr=all_ppn_hot)
    time.sleep(2.0)
    move_part_to_part(
        source_file=source_file,
        source_sheet='IC_hot_sorted',
        from_col=2,
        to_col=9,
        aim_file=source_file,
        aim_sheet='all_info',
        start_col=13)


def move_digiKey(source_file: str, digikey_file: str, source_sheet: str):
    ppns = ExcelHelp.read_col_content(file_name=source_file, sheet_name='ppn', col_index=1)
    digikey_data = ExcelHelp.read_sheet_content_by_name(file_name=digikey_file, sheet_name=source_sheet)
    result = []
    solved = (digikey_data[0][0] != 'Index' and digikey_data[0][0] != '索引')
    # 适合未处理的digikey 数据
    if solved:
        for (index, ppn) in enumerate(ppns):
            digi_record = [ppn, '/', '/']
            for (digi_index, digi_info) in enumerate(digikey_data):
                if ppn == digi_info[0]:
                    digi_record = digi_info
                    break
            result.append(digi_record)
    else:
        for (index, ppn) in enumerate(ppns):
            digi_record = [ppn, '/', '/']
            for (digi_index, digi_info) in enumerate(digikey_data):
                    if ppn == digi_info[3]:
                        digi_record = [digi_info[3], digi_info[1], digi_info[2], digi_info[4]]
                        break
            result.append(digi_record)

    ExcelHelp.add_arr_to_sheet(file_name=source_file, sheet_name='digikey_status', dim_arr=result)
    move_part_to_part(
        source_file=source_file,
        source_sheet='digikey_status',
        from_col=3,
        to_col=4,
        aim_file=source_file,
        aim_sheet='all_info',
        start_col=11)


#合并数据前的预处理，IC 结果统计，findchips 合计，digikey 合计
def pre_combine_data():
    cate_source_file = PathHelp.get_file_path("TVicor15H", 'Task.xlsx')
    # reco hot images
    hot_image_files = ['/Users/liuhe/Desktop/progress/TVicor/15H/11/IC_hot_images',
                       '/Users/liuhe/Desktop/progress/TVicor/15H/sz/IC_hot_images',
                       '/Users/liuhe/Desktop/progress/TVicor/15H/04/IC_hot_images',
                       PathHelp.get_IC_hot_image_fold("TVicor15H")
                       ]
    for hot_images in hot_image_files:
        IC_Search.IC_search_Image.rec_image(
            fold_path=hot_images)
        time.sleep(2.0)
    # price_level
    Statistic_data.statistic_price_sheet.calculater_price()
    #
    ICStock_file_arr = ["/Users/liuhe/Desktop/progress/TVicor/15H/11/IC_stock.xlsx",
                        "/Users/liuhe/Desktop/progress/TVicor/15H/sz/IC_stock.xlsx",
                        "/Users/liuhe/Desktop/progress/TVicor/15H/04/IC_stock.xlsx",
                       PathHelp.get_file_path('TVicor15H', 'IC_stock.xlsx')]
    IC_stock_result.combine_result(source_files=ICStock_file_arr, aim_file=PathHelp.get_file_path('TVicor15H', 'IC_stock.xlsx'))
    IC_stock_result.IC_stock_sum(IC_source_file=PathHelp.get_file_path('TVicor15H', 'IC_stock.xlsx'), cate_source_file=cate_source_file)
    findchips_stock_cate.combine_result(["/Users/liuhe/Desktop/progress/TVicor/15H/11/findchip_stock.xlsx",
                                         "/Users/liuhe/Desktop/progress/TVicor/15H/04/findchip_stock.xlsx",
                                         "/Users/liuhe/Desktop/progress/TVicor/15H/sz/findchip_stock.xlsx"],
                                        PathHelp.get_file_path('TVicor15H', 'findchip_stock.xlsx'))


# 统计汇总结果
def statistic_data():
    source_file = PathHelp.get_file_path('TVicor15H', 'Task.xlsx')
    move_ppn_to_allInfo(source_file=source_file)
    move_IC_stock_to_allInfo(source_file=source_file)
    move_BomOct_to_allInfo(source_file=source_file)
    move_findchip_to_allInfo(source_file=source_file, findchip_file=PathHelp.get_file_path('TVicor15H', 'findchip_stock.xlsx'))
    move_digiKey(source_file=source_file, digikey_file=PathHelp.get_file_path("TVicor15H", 'digikey_status.xlsx'), source_sheet='My Lists Worksheet')
    move_IC_hot(source_file=source_file)


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
    bom_info = ExcelHelp.read_sheet_content_by_name(source_file, 'bom_price_sum')
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


#  HQ_simple
def HQ_simple(source_file):
    first_row = ["型号", "品牌","status", "HQ_hot_week", 'HQ_hot_month', 'HQ_hot_avg', 'HQ_hot_result', 'oc_price', 'oc_stock','oc_supplier', 'oc_des']
    result = []
    result.append(first_row)
    HQ_hot_info = ExcelHelp.read_sheet_content_by_name(source_file, 'HQ_hot_result')
    try:
        oc_info = ExcelHelp.read_sheet_content_by_name(source_file, 'octopart')
    except:
        oc_info = []
    ppns_info = ExcelHelp.read_sheet_content_by_name(source_file, 'ppn')
    for (index, temp_ppnInfo) in enumerate(ppns_info):
        ppn_result = [temp_ppnInfo[0], temp_ppnInfo[1], temp_ppnInfo[2],
                      ' ', ' ', ' ', ' ',
                      ' ', ' ', ' ', ' ']
        for temp_HQ in HQ_hot_info:
            start = 3
            if temp_HQ[0] == temp_ppnInfo[0]:
                ppn_result[start] = temp_HQ[2]
                ppn_result[start+1] = temp_HQ[3]
                ppn_result[start+2] = temp_HQ[4]
                ppn_result[start+3] = temp_HQ[5]
                break;
        for temp_OC in oc_info:
            start = 7
            if temp_OC[0] == temp_ppnInfo[0]:
                try:
                    oc_price = round(float(temp_OC[4]), 2)
                except:
                    oc_price = ""
                ppn_result[start] = oc_price
                ppn_result[start+1] = temp_OC[5]
                ppn_result[start+2] = temp_OC[3]
                ppn_result[start+3] = temp_OC[2]
                break;
        result.append(ppn_result)
    ExcelHelp.add_arr_to_sheet(source_file, "Result", result)


def IC_HQ_Result2(save_file, rate, ppn_sheet):
    # HQHotResult.HQ_hot_result(source_file)
    # time.sleep(1.0)
    # IC_stock_result.IC_stock_sum(source_file)
    # time.sleep(1.0)
    # BomResult.bom_price_result(source_file)
    # time.sleep(1.0)
    source_file = save_file
    first_row = ["型号", "品牌","IC_supplier","IC_rank", "IC_stock", "IC_maxStock_supplier", "supplier_batch", "efind_allSup","efind_priceSup", "efind_stockSup", "HQ_hot_week", 'HQ_hot_month', 'HQ_hot_avg', 'HQ_hot_result', 'oc_price', 'oc_stock','oc_supplier', 'oc_des','digikey_status', 'bom_price','bom_supplier', 'IC_hot_max', 'IC_hot_min','IC_hot_avg', 'IC_price',  'result']
    result = []
    result.append(first_row)
    IC_info = ExcelHelp.read_sheet_content_by_name(source_file, 'IC_stock_sum')
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
    bom_info = ExcelHelp.read_sheet_content_by_name(source_file, 'bom_price_sum')
    ppns_info = ExcelHelp.read_sheet_content_by_name(source_file, 'ppn2')   # 先过滤HQ_hot_合格的ppn
    for (index, temp_ppnInfo) in enumerate(ppns_info):
        ppn_result = [temp_ppnInfo[0], temp_ppnInfo[1], ' ', ' ', ' ',' ', ' ', ' ',' ',' ',
                      ' ', ' ', ' ', ' ', ' ',
                      ' ', ' ', ' ', ' ', ' ',' ',
                      ' ', ' ', '', '', '']
        for temp_IC in IC_info:
            if temp_IC[0] == temp_ppnInfo[0]:
                start = 2
                ppn_result[start] = temp_IC[2]
                ppn_result[start+1] = temp_IC[3]
                ppn_result[start+2] = temp_IC[4]
                ppn_result[start+3] = temp_IC[7]
                ppn_result[start+4] = temp_IC[8]
                break;
        for temp_efind in efind_info:
            if temp_efind[0] == temp_ppnInfo[0]:
                start = 7
                ppn_result[start] = temp_efind[2]
                ppn_result[start+1] = temp_efind[3]
                ppn_result[start+2] = temp_efind[4]
                break;
        for temp_HQ in HQ_hot_info:
            if temp_HQ[0] == temp_ppnInfo[0]:
                start = 10
                ppn_result[start] = temp_HQ[2]
                ppn_result[start+1] = temp_HQ[3]
                ppn_result[start+2] = temp_HQ[4]
                ppn_result[start+3] = temp_HQ[5]
                break;
        for temp_OC in oc_info:
            if temp_OC[0] == temp_ppnInfo[0]:
                try:
                    tax = 1.13
                    oc_price = round(float(temp_OC[4]) * rate, 2)
                except:
                    oc_price = ""
                start = 14
                ppn_result[start] = oc_price
                ppn_result[start+1] = temp_OC[5]
                ppn_result[start+2] = temp_OC[3]
                ppn_result[start+3] = temp_OC[2]
                break;
        for temp_dg in dg_info:
            if temp_dg[0] == temp_ppnInfo[0]: # digikey 状态来自jason的原始文件
                ppn_result[18] = temp_dg[2]
                break;
        for temp_bom in bom_info:
            if temp_bom[0] == temp_ppnInfo[0]:
                start = 19
                if temp_bom.__len__() > 2:
                    ppn_result[start] = temp_bom[2]
                    ppn_result[start+1] = temp_bom[3]
                else:
                    ppn_result[start] = ''
                    ppn_result[start+1] = ''
                break;
        result.append(ppn_result)
    ExcelHelp.add_arr_to_sheet(save_file, "Result", result)


def temp():
    result_file = PathHelp.get_file_path(None, 'TFiber.xlsx')
    # file_fiber = '/Users/liuhe/Downloads/fiber.xlsx'
    source = ExcelHelp.read_sheet_content_by_name(result_file, 'IC_stock')
    result_file = result_file
    ppns = ExcelHelp.read_col_content(result_file, 'ppn4', 1)
    result = []
    for temp_source in source:
        if ppns.__contains__(temp_source[0]):
            result.append(temp_source)
    ExcelHelp.add_arr_to_sheet(result_file, 'IC_stock2', result)


if __name__ == "__main__":
    aim_file = PathHelp.get_file_path(None, 'TInfineonPowerManger.xlsx')
    IC_HQ_Result2(aim_file, 1.0, 'ppn2')
    print('over')
    # save_file = PathHelp.get_file_path(None, 'TAccelerationSensor.xlsx')
    # HQ_simple(save_file)


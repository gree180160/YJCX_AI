import time

from WRTools import ExcelHelp, PathHelp, PandasHelp, MySqlHelp_recommanded
import os


def change_file_name():
    path = "/Users/liuhe/Desktop/MMS_html_files"
    batch_rename(path, '.html')


# 给文件加上.html 后缀
def batch_rename(file_dir, new_ext):
    list_file = os.listdir(file_dir)  # 返回指定目录
    for file in list_file:
        if not (file.endswith('.html') or file.endswith('.htm') or file.endswith('.mhtml')):
            newfile = file + new_ext
            os.rename(os.path.join(file_dir, file),
                      os.path.join(file_dir, newfile))


# get page_more PN
def get_page_more_PN():
    source_file = ''
    page0_PNS = ExcelHelp.read_col_content(file_name='//TKWPage0.xlsx',
                                           sheet_name='all', col_index=1)
    all_PNInfo_arr = ExcelHelp.read_sheet_content_by_index(file_name='//TKWPageMore.xlsx', sheet_index=2)
    page_more_arr = []
    for PNInfo_ele in all_PNInfo_arr:
        pn = PNInfo_ele[0]
        if pn in page0_PNS:
            continue
        else:
            info_arr = [PNInfo_ele[0], PNInfo_ele[1]]
            page_more_arr.append(info_arr)
    ExcelHelp.add_arr_to_sheet(file_name='//TKWPageMore.xlsx',
                               sheet_name='page_more', dim_arr=page_more_arr)


# 将大项目拆分成一天天的任务
def createDayTask(unit:int):
    i = 15  # 删除ppn 里面的历史数据,Renesas_all_165H
    while i < 20:
        file_name = PathHelp.get_file_path(f'TVicor{i}H', 'Task.xlsx')
        ExcelHelp.remove_sheet(file_name, 'ppn')
        i += int(unit/100)
    # sheet_content = ExcelHelp.read_sheet_content_by_name(file_name=PathHelp.get_file_path(None, 'TNXP.xlsx'), sheet_name='discontinue')
    sheet_content = ExcelHelp.read_sheet_content_by_name(file_name=PathHelp.get_file_path(None, 'TVicor.xlsx'), sheet_name='ppn')
    sheet_content = sheet_content[1000:]
    task_value = []
    start_index = 15
    for (row_index, row_value) in enumerate(sheet_content):
        row_info = [row_value[0], 'Vicor']
        if row_value[0]:
            task_value.append(row_info)
            if task_value.__len__() == unit:
                file_name = PathHelp.get_file_path(f'TVicor{start_index}H', 'Task.xlsx')
                ExcelHelp.add_arr_to_sheet(file_name=file_name, sheet_name='ppn', dim_arr=task_value)
                task_value = []
                start_index += int(unit/100)


# 分解数量大的ppn列表
def decompositionPPN(unit: int):
    source_file = "/Users/liuhe/Desktop/CalcitrapaAIProject/TTISerail/TTISerial.xlsx"
    sava_fold = '/Users/liuhe/Desktop/CalcitrapaAIProject/TTISerail/'
    source_ppn = ExcelHelp.read_col_content(file_name=source_file, sheet_name='ppn', col_index=1)
    # source_ppn = source_ppn[0:2000]
    # history_sheets = []
    # history_ppn = set()
    # for sheet_name in history_sheets:
    #     history_ppn = history_ppn.union(set(ExcelHelp.read_col_content(file_name=source_file, sheet_name=sheet_name, col_index=1)))
    # ppn_all = list(set(source_ppn).difference(set(history_ppn)))

    ppn_all = source_ppn[0:]
    # ppn_all.sort()
    stop_quotient = 0
    result = []
    for (index, ppn) in enumerate(ppn_all):
        if ppn:
            quotient = int(index / unit)
            if quotient > stop_quotient:
                file_name = f'Sub{quotient}.xlsx'
                file_path = sava_fold + file_name
                ExcelHelp.add_arr_to_sheet(file_name=file_path, sheet_name='Sheet', dim_arr=result)
                result.clear()
                stop_quotient = quotient
            result.append([ppn])
        else:
            break
    if ppn_all.__len__() % unit > 0:
        # 保存最后的尾巴
        file_name = f'Sub{quotient + 1}.xlsx'
        file_path = sava_fold + file_name
        ExcelHelp.add_arr_to_sheet(file_name=file_path, sheet_name='Sheet', dim_arr=result)


def Ti():
    source_file = "/Users/liuhe/Desktop/progress/TRuStock/TRuStock.xlsx"
    arr1 = ExcelHelp.read_sheet_content_by_name(source_file, sheet_name='Sheet1')[0: 1000]
    arr2 = ExcelHelp.read_sheet_content_by_name(source_file, sheet_name='Sheet1')[1000: 2000]
    arr3 = ExcelHelp.read_sheet_content_by_name(source_file, sheet_name='Sheet1')[2000: 3000]
    result = [arr1, arr2, arr3]
    fold = '/Users/liuhe/Desktop/progress/TRu_needs'
    for (index, temp_row) in enumerate(result):
        ExcelHelp.add_arr_to_sheet(file_name=fold + f'Active {index}.xlsx', sheet_name='Sheet1', dim_arr=temp_row)


def ppn_vicor_all():
    fold = '/Users/liuhe/Downloads/ly/'
    file_name_list = os.listdir(fold)
    result = []
    for temp_file in file_name_list:
        try:
            content_sheet = PandasHelp.read_sheet_content(fold + temp_file)#ExcelHelp.read_sheet_content_by_name(file_name=temp_file, sheet_name='工作表 1')
        except:
            content_sheet = ''
            print(f'error file: {temp_file}')
        for row_content in content_sheet:
            result.append([row_content[3], row_content[4], row_content[6], row_content[12], row_content[13], os.path.basename(temp_file)])
    ExcelHelp.add_arr_to_sheet(file_name=PathHelp.get_file_path(None, 'TVicor.xlsx'), sheet_name='all_ppn_ser', dim_arr=result)


def write_ppn_to_sql():
    ppn_list_file = PathHelp.get_file_path(None, 'TMitsubishi.xlsx')
    sheet_name = 'Sheet1'
    ppn_file = ExcelHelp.read_col_content(ppn_list_file, sheet_name=sheet_name, col_index=1)
    # ppn_db = MySqlHelp_recommanded.DBRecommandChip().ppn_read('1')
    # ppn_db = [item[0] for item in ppn_db]
    ppn_list = ppn_file
    manu_id_list = ExcelHelp.read_col_content(ppn_list_file, sheet_name=sheet_name, col_index=3)
    manu_name_list = ExcelHelp.read_col_content(ppn_list_file, sheet_name=sheet_name, col_index=2)
    result = []
    for (index1, ppn) in enumerate(ppn_list):
        if ppn:
            row = [ppn, manu_id_list[index1],manu_name_list[index1], 'TinaMitsubishiIGBT']
            result.append(row)
    MySqlHelp_recommanded.DBRecommandChip().ppn_write(result)


def ru_stock_nonRepeat():
    new_path = '/Users/liuhe/Desktop/progress/TRuStock/2023.10/oc/RuInquire2023.10sum.xlsx'
    new_ppnInfo = ExcelHelp.read_sheet_content_by_name(new_path, sheet_name='ppn')
    old_path = PathHelp.get_file_path(None, 'TRuStock.xlsx')
    old1 = ExcelHelp.read_col_content(old_path, sheet_name='ppn_M8', col_index=1)
    old2 = ExcelHelp.read_col_content(old_path, sheet_name='ppn_M9', col_index=1)
    old_all = old2 + old1
    result = []
    for temp_row in new_ppnInfo:
        if old_all.__contains__(temp_row[0]):
            continue
        else:
            new_list_cell = []
            if temp_row[0]:
                new_list_cell.append(temp_row[0])
            if temp_row[1]:
                new_list_cell.append(temp_row[1])
            if temp_row[2]:
                new_list_cell.append(temp_row[2])
            if temp_row[3]:
                new_list_cell.append(temp_row[3])
            result.append(new_list_cell)
    ExcelHelp.add_arr_to_sheet(new_path, 'ppn_new', dim_arr=result)


def jinshunRenesas2():
    file = '/Users/liuhe/Desktop/progress/TReneseas_all/JinShun2/renesas/sum.xlsx'
    excel_ppn = ExcelHelp.read_col_content(file, 'ppn', 1)
    renesas_old = ExcelHelp.read_col_content('/Users/liuhe/Desktop/progress/TReneseas_all/TRenesa.xlsx', 'only_ppn', 1)
    result = list(set(excel_ppn).difference(set(renesas_old)))
    ExcelHelp.add_arr_to_col(file, 'new_ppn', result)


def huaqiang_ppn():
    cate_source_file = PathHelp.get_file_path(None, 'TRuStock.xlsx')
    pps = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn_M9', col_index=1)
    manus = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn_M9', col_index=2)
    ic_hots = ExcelHelp.read_col_content(cate_source_file, 'IC_search_m', 1)
    ic_stocks = ExcelHelp.read_col_content(cate_source_file, 'IC_stock_sum2M9', 1)
    findchips = ExcelHelp.read_col_content(cate_source_file, 'M9_findchips', 1)
    result = []
    for (ppn_index, ppn) in enumerate(pps):
        try:
            ic_hot_index = ic_hots.index(ppn)
            ic_hot_value = int(ExcelHelp.read_sheet_content_by_name(cate_source_file, 'IC_search_m')[ic_hot_index][2])
        except:
            ic_hot_value = 0

        try:
            ic_stock_index = ic_stocks.index(ppn)
            ic_stock_value = int(ExcelHelp.read_sheet_content_by_name(cate_source_file, 'IC_stock_sum2M9')[ic_stock_index][2])
        except:
            ic_stock_value = 0

        try:
            findchip_index = findchips.index(ppn)
            findchip_value = int(ExcelHelp.read_sheet_content_by_name(cate_source_file, 'M9_findchips')[findchip_index][2])
        except:
            findchip_value = 0
        if ic_hot_value >= 500 and ic_stock_value <= 4 and findchip_value <= 10:
            ppnInfo = [ppn, manus[ppn_index], ic_hot_value, ic_stock_value, findchip_value]
            result.append(ppnInfo)
    ExcelHelp.add_arr_to_sheet(cate_source_file, 'js2', result)


def ali():
    cate_source_file = PathHelp.get_file_path(None, 'TRuStock.xlsx')
    pps = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn_M9', col_index=1)
    manus = ExcelHelp.read_col_content(file_name=cate_source_file, sheet_name='ppn_M9', col_index=2)
    ic_hots = ExcelHelp.read_col_content(cate_source_file, 'IC_search_m', 1)
    ic_stocks = ExcelHelp.read_col_content(cate_source_file, 'IC_stock_sum2M9', 1)
    findchips = ExcelHelp.read_col_content(cate_source_file, 'M9_findchips', 1)
    result = []
    for (ppn_index, ppn) in enumerate(pps):
        try:
            ic_hot_index = ic_hots.index(ppn)
            ic_hot_value = int(ExcelHelp.read_sheet_content_by_name(cate_source_file, 'IC_search_m')[ic_hot_index][2])
        except:
            ic_hot_value = 0

        try:
            ic_stock_index = ic_stocks.index(ppn)
            ic_stock_value = int(ExcelHelp.read_sheet_content_by_name(cate_source_file, 'IC_stock_sum2M9')[ic_stock_index][2])
        except:
            ic_stock_value = 0

        try:
            findchip_index = findchips.index(ppn)
            findchip_value = int(ExcelHelp.read_sheet_content_by_name(cate_source_file, 'M9_findchips')[findchip_index][2])
        except:
            findchip_value = 0
        if ic_hot_value >= 600 and ic_stock_value >= 8 and findchip_value >= 3:
            ppnInfo = [ppn, manus[ppn_index], ic_hot_value, ic_stock_value, findchip_value]
            result.append(ppnInfo)
    ExcelHelp.add_arr_to_sheet(cate_source_file, 'hxl2', result)


def temp():
    ppn_file = '/Users/liuhe/Desktop/卖什么/hxl.xlsx'
    ppn_list = ExcelHelp.read_col_content(ppn_file, 'TIBrandS1', col_index=1)
    search_data_file = '/Users/liuhe/Desktop/progress/TTI/S1/Task.xlsx'
    search_sheet = ExcelHelp.read_sheet_content_by_name(search_data_file, 'ic_search')
    result = []
    for ppn1 in ppn_list:
        for info in search_sheet:
            if ppn1 == info[0]:
                result.append(info)
                break;
    ExcelHelp.add_arr_to_sheet(ppn_file, 'ic_search', result)


def find_macTask_folders(folder_path):
    task_file_paths = []
    for root, dirs, files in os.walk(folder_path):
        if "mac" in dirs:
            mac_folder = os.path.join(root, "mac")
            for mac_root, mac_dirs, mac_files in os.walk(mac_folder):
                for file in mac_files:
                    if file == "Task.xlsx":
                        task_file_paths.append(os.path.join(mac_root, file))
    return task_file_paths


def getAllICStockRecord():
    result_file = '/Users/liuhe/Desktop/IC_supplier10+2.xlsx'
    fold1 = '/Users/liuhe/Desktop/progress/TRenesas_MCU'
    fold2 = '/Users/liuhe/Desktop/progress/TRenesas_RL78'
    fold3 = '/Users/liuhe/Desktop/progress/TReneseas_all'
    fold4 = '/Users/liuhe/Desktop/progress/TVicor/p2_15H'
    folder_paths = [fold1, fold2, fold3, fold4]
    macTask_fiels = find_macTask_folders(folder_paths[3])
    for excel in macTask_fiels:
        try:
            sheetContent = ExcelHelp.read_sheet_content_by_name(excel, 'IC_Stock')
        except:
            try:
                sheetContent = ExcelHelp.read_sheet_content_by_name(excel, 'IC_stock_sum')
            except:
                print("error : {excel}")
                sheetContent = [[]]
        ExcelHelp.add_arr_to_sheet(result_file, 'IC_Stock', sheetContent)
        time.sleep(1.0)


def filterNeeds():
    source_file = '/Users/liuhe/Desktop/progress/TYjcxCloudStock/p1/TYjcxCloundStock.xlsx'
    finished_ppn = ExcelHelp.read_col_content(source_file, 'ppn1', 1)
    waiting_data = ExcelHelp.read_sheet_content_by_name(source_file, 'needs')
    result = []
    for row_value in waiting_data:
        temp_ppn = row_value[0]
        if finished_ppn.__contains__(temp_ppn):
            continue
        else:
            result.append(row_value)
    ExcelHelp.add_arr_to_sheet(source_file, 'needs2', result)


# delet finished ppn
def deletFinished_ppn():
    wait_file = PathHelp.get_file_path(None, 'TTI_10USD.xlsx')
    waiting_ppns = ExcelHelp.read_sheet_content_by_name(wait_file, 'source')
    history_files = [PathHelp.get_file_path(None, 'TTISTOCK2404.xlsx'),
                     PathHelp.get_file_path(None, 'TRU2405.xlsx'),
                     PathHelp.get_file_path(None, 'TTIMilitary.xlsx'),
                     PathHelp.get_file_path(None, 'TTIMilitary.xlsx'),
                     PathHelp.get_file_path(None, 'TManuAndSeri_willTC.xlsx')
                     ]
    history_ppns = []
    for temp_file in history_files:
        temp_ppns = ExcelHelp.read_col_content(temp_file, 'ppn', 1)
        history_ppns += temp_ppns
    result = []
    for row_value in waiting_ppns:
        if not history_ppns.__contains__(row_value[0]):  #历史去重
            history_ppns.append(row_value[0]) # 自身去重
            result.append(row_value)
    ExcelHelp.add_arr_to_sheet(wait_file, sheet_name='ppn', dim_arr=result)
    print(result)


if __name__ == "__main__":
    # time.sleep(3.0)
    # ali()
    # getAllICStockRecord()
    deletFinished_ppn()
    # decompositionPPN(500)
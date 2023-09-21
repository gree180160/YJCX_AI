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
    source_file = PathHelp.get_file_path(None, 'TNXP.xlsx')
    source_ppn = ExcelHelp.read_col_content(file_name=source_file, sheet_name='ppn7', col_index=1)
    source_ppn = source_ppn[0:726]
    history_sheets = []
    history_ppn = set()
    for sheet_name in history_sheets:
        history_ppn = history_ppn.union(set(ExcelHelp.read_col_content(file_name=source_file, sheet_name=sheet_name, col_index=1)))
    sava_fold = '/Users/liuhe/Desktop/progress/TNXP/discontiue/p7/'
    ppn_all = list(set(source_ppn).difference(set(history_ppn)))

    ppn_all = ppn_all[0:]
    ppn_all.sort()
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
    source_file = "/Users/liuhe/Desktop/progress/TRu_needs/RuNeeds0918.xlsx"
    arr1 = ExcelHelp.read_sheet_content_by_name(source_file, sheet_name='Sheet1')[0: 1000]
    arr2 = ExcelHelp.read_sheet_content_by_name(source_file, sheet_name='Sheet1')[1000: 2000]
    arr3 = ExcelHelp.read_sheet_content_by_name(source_file, sheet_name='Sheet1')[2000: 3000]
    result = [arr1, arr2, arr3]
    fold = '/Users/liuhe/Desktop/progress/TRu_needs'
    for (index, temp_row) in enumerate(result):
        ExcelHelp.add_arr_to_sheet(file_name=fold + f'Active {index}.xlsx', sheet_name='Sheet1', dim_arr=temp_row)


def mcu2():
    svicor_sheet = ExcelHelp.read_sheet_content_by_name(file_name=PathHelp.get_file_path(None, 'TVicor.xlsx'), sheet_name='jason')
    his = ExcelHelp.read_col_content(file_name=PathHelp.get_file_path(None, 'TVicor.xlsx'), sheet_name='ppn', col_index=1)
    result = []
    for row_value in svicor_sheet:
        if not his.__contains__(row_value[0]):
            result.append(row_value)
            his.append(row_value[0])
    ExcelHelp.add_arr_to_sheet(file_name=PathHelp.get_file_path(None, 'TVicor.xlsx'), sheet_name='jason2', dim_arr=result)
    print(result)


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
    ppn_list_file = PathHelp.get_file_path(None, 'TVicor.xlsx')
    ppn_file = ExcelHelp.read_col_content(ppn_list_file, sheet_name='ppn', col_index=1)
    ppn_db = MySqlHelp_recommanded.DBRecommandChip().ppn_read('1')
    ppn_db = [item[0] for item in ppn_db]
    ppn_list = list(set(ppn_file).difference(set(ppn_db)))
    result = []
    for ppn in ppn_list:
        if ppn:
            row = [ppn, 2089, 'Vicor', 'sales_dijikey']
            result.append(row)
    MySqlHelp_recommanded.DBRecommandChip().ppn_write(result)


def ros_cate():
    path = '/Users/liuhe/Desktop/progress/TTender_info/ros_tender/ros_keyword.xlsx'
    arr1 = ExcelHelp.read_col_content(path, sheet_name='keywords1', col_index=1)
    arr2 = ExcelHelp.read_col_content(path, sheet_name='keywords2', col_index=1)
    result = list(set(arr2).difference(set(arr1)))
    ExcelHelp.add_arr_to_col(path, 'keword_new',dim_arr=result)



if __name__ == "__main__":
    # get_ICSupplierAndHot(20, 300)
    # get_wheat()
    # adjustopn()
    # createDayTask(500)
    # decompositionPPN(500)
    # adi_stock()
    Ti()

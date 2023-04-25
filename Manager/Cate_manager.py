from WRTools import ExcelHelp, PathHelp
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
def createDayTask():
    i = 75  # 删除ppn 里面的历史数据
    while i < 125:
        file_name = PathHelp.get_file_path(f'TRenesasAll_{i}H', 'Task.xlsx')
        ExcelHelp.remove_sheet(file_name, 'ppn')
        i += 5
    sheet_content = ExcelHelp.read_sheet_content_by_name(file_name=PathHelp.get_file_path(None, 'TRenesa.xlsx'), sheet_name='ppn')
    sheet_content = sheet_content[7500:12000]
    task_value = []
    start_index = 75
    for (row_index, row_value) in enumerate(sheet_content):
        if row_value[0] and str(row_value[2]) != '1':
            task_value.append(row_value)
            if task_value.__len__() == 500:
                file_name = PathHelp.get_file_path(f'TRenesasAll_{start_index}H', 'Task.xlsx')
                ExcelHelp.add_arr_to_sheet(file_name=file_name, sheet_name='ppn', dim_arr=task_value)
                task_value = []
                start_index += 5


# 分解数量大的ppn列表
def decompositionPPN(unit: int):
    source_file = PathHelp.get_file_path(None, 'TSTM.xlsx')
    source_ppn = ExcelHelp.read_col_content(file_name=source_file, sheet_name='ppn4', col_index=1)
    history_sheets = ['ppn1', 'ppn2', 'ppn3']
    history_ppn = set()
    for sheet_name in history_sheets:
        history_ppn = history_ppn.union(set(ExcelHelp.read_col_content(file_name=source_file, sheet_name=sheet_name, col_index=1)))
    sava_fold = '/Users/liuhe/Desktop/progress/TSTM/discontiue/digikey/p4/'
    ppn_all = list(set(source_ppn).difference(set(history_ppn)))
    ppn_all = ppn_all[0:]
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


def get_ICSupplierAndHot(IC_supplier_max, hot_min):
    '''
    / Users / liuhe / Desktop / progress / TInfineon / 5 H / TInfenion_5H.xlsx, .....80H
    / Users / liuhe / Desktop / progress / TReneseas_all / 5H / mac / Task.xlsx....90H
    '''
    index = 5
    result = []
    while index <= 75:
        try:
            file = f'/Users/liuhe/Desktop/progress/TReneseas_all/{index}H/mac/Task.xlsx'
            sheet_content = ExcelHelp.read_sheet_content_by_name(file_name=file, sheet_name='all_info')
            default_max_row = 14
            for (row_index, row) in enumerate(sheet_content):
                if row_index == 0:
                    if str(row[14]) != 'max_month1':
                        for (cell_index, cell) in enumerate(row):
                            if str(cell) == 'max_month1':
                                default_max_row = cell_index
                    print(f'max month index is :{default_max_row}')
                else:
                    try:
                        max_m_value = int(row[default_max_row])
                        print(f'max_m_value is:{max_m_value}')
                    except:
                        max_m_value = 0
                        print(f'change to int error : {str(row[default_max_row])}')
                    if max_m_value >= 300:
                        try:
                            IC_supplier = int(row[2])
                        except:
                            IC_supplier = 0

                        if IC_supplier <= IC_supplier_max:
                            result.append([row[0], row[1], row[default_max_row]])
                            print(f'+ ic supplier is : {IC_supplier}')
                        else:
                            print(f'ic supplier is : {IC_supplier}')
        except Exception as e:
            print(f'1 get max_m error file is: {file}')
        index += 5
    ExcelHelp.add_arr_to_sheet('/Users/liuhe/Desktop/TWheat.xlsx', 'Sheet3', result)


def get_wheat():
    source_file = '/Users/liuhe/Desktop/TWheat.xlsx'
    sheet1 = ExcelHelp.read_sheet_content_by_name(file_name=source_file, sheet_name='Sheet1')
    sheet2 = ExcelHelp.read_sheet_content_by_name(file_name=source_file, sheet_name='Sheet3')
    sheet3 = ExcelHelp.read_sheet_content_by_name(file_name=source_file, sheet_name='Sheet3')
    sheet_all = sheet1 + sheet2 + sheet3
    result = []
    for row in sheet_all:
        try:
            hot_value = int(row[2])
        except:
            hot_value = 0
        if hot_value >= 500:
            result.append(row)
        elif hot_value >= 400 and str(row[1]).__contains__('Infineon'):
            result.append(row)
        elif hot_value >= 300 and str(row[1]).__contains__('Renesas'):
            result.append(row)
    ExcelHelp.add_arr_to_sheet(file_name=source_file, sheet_name='ppn', dim_arr=result)


if __name__ == "__main__":
    # get_unfinished_RenesasPPN()
    # decompositionPPN(unit=300)
    # createDayTask()
    # get_ICSupplierAndHot(20, 300)
    # get_wheat()
    result_save_file = PathHelp.get_file_path('Wheat', 'wheat_buyer.xlsx')
    arr = [
        ['IRF3710STRLPBF', '2021-06-15', 'Ао Нпотэл Digtel%23x1eАо Нпотэл%23x1eАо Нпотэл Digtel', 'Infineon Technologies',
         'ТРАНЗИСТОР irf3710strlpbf - ПОЛЕВОЙ МДП (МЕТАЛ-ДИЭЛЕКТРИК-ПОЛУПРОВОДНИК) ТРАНЗИСТОР, n-КАНАЛЬНЫЙ, БОЛЬШОЙ МОЩНОСТИ ( 1ВТ). НАПРЯЖЕНИЕ ПРОБОЯ СТОК-ИСТОК - 100 В, НАПРЯЖЕНИЕ ПРОБОЯ ЗАТВОР-ИСТОК - 20 В НЕПРЕРЫВНЫЙ ТОК СТОКА - 57 А, РАССЕЯНИЕ МОЩНОСТИ',
         '俄罗斯', '荷兰', '2023-04-24']]
    ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name='NetComponent_sup', dim_arr=arr)

from WRTools import ExcelHelp, PathHelp
import os
import time


def get_ICSupplierAndHot_Infineon(hot_min):
    '''
    / Users / liuhe / Desktop / progress / TInfineon / 5 H / TInfenion_5H.xlsx, .....80H
    '''
    index = 5
    result = []
    while index <= 80:
        try:
            file = f'/Users/liuhe/Desktop/progress/TInfineon/{index}H/mac/Task.xlsx'
            sheet_content = ExcelHelp.read_sheet_content_by_name(file_name=file, sheet_name='all_info')
            default_max_row = 14
            for (row_index, row) in enumerate(sheet_content):
                if row_index == 0:
                    if str(row[default_max_row]) != 'max_month1':
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
                    if max_m_value >= hot_min:
                        try:
                            IC_supplier = int(row[2])
                        except:
                            IC_supplier = 0
                        result.append([row[0], row[1], row[default_max_row]])
                        print(f'+ ic supplier is : {IC_supplier}')
        except Exception as e:
            print(f'1 get max_m error file is: {file}')
        index += 5
    ExcelHelp.add_arr_to_sheet(PathHelp.get_file_path('Wheat', 'Task.xlsx'), 'Sheet2', result)


def get_ICSupplierAndHot_renesas(hot_min):
    '''
    / Users / liuhe / Desktop / progress / TReneseas_all / 5H / mac / Task.xlsx....90H
    '''
    index = 5
    result = []
    while index <= 100:
        try:
            file = f'/Users/liuhe/Desktop/progress/TReneseas_all/{index}H/mac/Task.xlsx'
            sheet_content = ExcelHelp.read_sheet_content_by_name(file_name=file, sheet_name='all_info')
            default_max_row = 17
            for (row_index, row) in enumerate(sheet_content):
                if row_index == 0:
                    if str(row[default_max_row]) != 'max_month1':
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
                    if max_m_value >= hot_min:
                        result.append([row[0], row[1], row[default_max_row]])
        except Exception as e:
            print(f'1 get max_m error file is: {file}')
        index += 5
    ExcelHelp.add_arr_to_sheet(PathHelp.get_file_path('Wheat', 'Task.xlsx'), 'Sheet3', result)


def get_wheat():
    source_file = PathHelp.get_file_path('Wheat', 'Task.xlsx')
    sheet1 = ExcelHelp.read_sheet_content_by_name(file_name=source_file, sheet_name='Sheet1')
    sheet2 = ExcelHelp.read_sheet_content_by_name(file_name=source_file, sheet_name='Sheet2')
    sheet3 = ExcelHelp.read_sheet_content_by_name(file_name=source_file, sheet_name='Sheet3')
    sheet_all = sheet1 + sheet2 + sheet3
    result = []
    for row in sheet_all:
        try:
            hot_value = int(row[2])
        except:
            print('int error')
            hot_value = 0
        if hot_value >= 500:
            result.append(row)
        elif hot_value >= 400 and str(row[1]).__contains__('Infineon'):
            result.append(row)
        elif hot_value >= 300 and str(row[1]).__contains__('Renesas'):
            result.append(row)
    history_ppn = ExcelHelp.read_col_content(file_name=source_file, sheet_name='ppn_all', col_index=1)
    new_ppn = []
    for temp_ppn_info in result:
        if not(temp_ppn_info[0] in history_ppn):
            new_ppn.append([temp_ppn_info[0], temp_ppn_info[1], temp_ppn_info[2], time.strftime('%Y-%m-%d', time.localtime())])
    ExcelHelp.add_arr_to_sheet(file_name=source_file, sheet_name='ppn_all', dim_arr=new_ppn)


if __name__ == "__main__":
    # decompositionPPN(unit=300)
    # createDayTask()
    # get_ICSupplierAndHot(20, 300)
    # get_wheat()
    # adjustopn()
    # get_ICSupplierAndHot_renesas(300)
    # get_ICSupplierAndHot_Infineon(400)
    get_wheat()
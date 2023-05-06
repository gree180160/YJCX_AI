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
    source_file = PathHelp.get_file_path(None, 'TSkyworks.xlsx')
    source_ppn = ExcelHelp.read_col_content(file_name=source_file, sheet_name='ppn3', col_index=1)
    history_sheets = ['ppn1', 'ppn2']
    history_ppn = set()
    for sheet_name in history_sheets:
        history_ppn = history_ppn.union(set(ExcelHelp.read_col_content(file_name=source_file, sheet_name=sheet_name, col_index=1)))
    sava_fold = '/Users/liuhe/Desktop/progress/TSkyworks/discontiue/digikey/p3/'
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


if __name__ == "__main__":
    # decompositionPPN(unit=300)
    # createDayTask()
    # get_ICSupplierAndHot(20, 300)
    # get_wheat()
    # adjustopn()
    get_wheat()

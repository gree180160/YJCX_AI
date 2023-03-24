from WRTools import ExcelHelp, PathHelp
import os


def get_zmz_cate():
    # want add
    source_file_arr = ["/Users/liuhe/Desktop/zmz/商友库存整理2022.09.20.xlsx",
                       "/Users/liuhe/Desktop/zmz/商友库存整理2022.09.22.xlsx",
                       "/Users/liuhe/Desktop/zmz/商友库存整理2022.09.26.xlsx"]
    all_lists = []
    for temp_file in source_file_arr:
        file_cates = ExcelHelp.read_col_content(file_name=temp_file, sheet_name='型号明细', col_index=2)[1:]
        all_lists = list(set(all_lists).union(set(file_cates)))
    all_lists = list(filter(None, all_lists))
    all_lists.sort()
    # used
    used_cate_files = ["/Users/liuhe/PycharmProjects/YJCX_AI/T0806.xlsx",
                       "/Users/liuhe/PycharmProjects/YJCX_AI/T0815.xlsx",
                       "/Users/liuhe/PycharmProjects/YJCX_AI/T0829zmz.xlsx",
                       "/Users/liuhe/PycharmProjects/YJCX_AI/T0907zmz.xlsx",
                       "/Users/liuhe/PycharmProjects/YJCX_AI/T0909.xlsx",
                       "/Users/liuhe/PycharmProjects/YJCX_AI/T0921.xlsx"
                       ]
    used_lists = []
    for temp_file in used_cate_files:
        file_cates = ExcelHelp.read_col_content(file_name=temp_file, sheet_name='all', col_index=1)
        used_lists = list(set(all_lists).union(set(file_cates)))
    used_lists = list(filter(None, used_lists))
    used_lists.sort()
    # valid
    result_list = list(set(all_lists).difference(set(used_lists)))
    ExcelHelp.save_one_col(file_name='//T0927.xlsx', sheet_name='all', dim_arr=result_list)


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
    all_PNInfo_arr = ExcelHelp.read_sheet_content_by_index(
        file_name='//TKWPageMore.xlsx', sheet_index=2)
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


# 分解数量大的ppn列表
def decompositionPPN(unit: int):
    ppn_all = ExcelHelp.read_col_content(file_name='/Users/liuhe/Desktop/NXP_files/TNXP.xlsx', sheet_name='ppn',
                                         col_index=1)
    stop_quotient = 0
    result = []
    for (index, ppn) in enumerate(ppn_all):
        quotient = int(index / unit)
        if quotient > stop_quotient:
            file_name = f'TNXP_sub的副本{quotient}.xlsx'
            file_path = f'/Users/liuhe/Desktop/NXP_files/{file_name}'
            ExcelHelp.add_arr_to_sheet(file_name=file_path, sheet_name='ppn', dim_arr=result)
            result.clear()
            stop_quotient = quotient
        result.append([ppn])
    # 保存最后的尾巴
    file_name = f'TNXP_sub的副本{stop_quotient+1}.xlsx'
    file_path = f'/Users/liuhe/Desktop/NXP_files/{file_name}'
    ExcelHelp.add_arr_to_sheet(file_name=file_path, sheet_name='ppn', dim_arr=result)


# 将大项目拆分成一天天的任务
def createDayTask(project_file: str, start_index:int, end_index:int, aim_file):
    ppns = ExcelHelp.read_col_content(file_name=project_file, sheet_name='ppn', col_index=1)
    manus = ExcelHelp.read_col_content(file_name=project_file, sheet_name='ppn', col_index=1)
    result = []
    for index in range(start_index, end_index):
        if ppns[index] and manus[index]:
            result.append([ppns[index], manus[index]])
        else:
            break
    ExcelHelp.add_arr_to_sheet(file_name=aim_file, sheet_name='ppn', dim_arr=result)


def get_unfinished_RenesasPPN():
    source_file = PathHelp.get_file_path(None, 'TRenesa.xlsx')
    source_cates = ExcelHelp.read_col_content(file_name=source_file, sheet_name='repeat_ppn', col_index=1)
    unfinished_cates = source_cates

    finished_files = [
                      '/Users/liuhe/Desktop/progress/TRenesas_RL78/5H/mac/Task.xlsx',
                      '/Users/liuhe/Desktop/progress/TRenesas_RL78/10H/mac/Task.xlsx',
                      '/Users/liuhe/Desktop/progress/TRenesas_RL78/15H/mac/Task.xlsx',
                      '/Users/liuhe/Desktop/progress/TReneseas_Speed/mac/Task.xlsx',
    '/Users/liuhe/PycharmProjects/YJCX_AI/TRenesas_Inspur/Task.xlsx']
    finished_sets = set()
    for temp_file in finished_files:
        print(temp_file)
        temp_ppns = ExcelHelp.read_col_content(file_name=temp_file, sheet_name='ppn', col_index=1)
        finished_sets = set(temp_ppns).union(finished_sets)
    repeated = list(finished_sets.difference(set(source_cates))) # list(set(source_cates).difference(finished_sets))
    ExcelHelp.add_arr_to_col(file_name=source_file, sheet_name='difference', dim_arr=repeated)


def renesas_file_ByFindchips():
    source_file = PathHelp.get_file_path(None, 'TRenesa.xlsx')
    all_ppn = ExcelHelp.read_col_content(file_name=source_file, sheet_name='ppn', col_index=1)
    current_ppn = all_ppn[2998:6000]
    findchips_files = ['/Users/liuhe/Desktop/progress/TReneseas_all/findchip_stock/TRenesa_findchips-04.xlsx',
                       '/Users/liuhe/Desktop/progress/TReneseas_all/findchip_stock/TRenesa_findchips-mac.xlsx']
    unvalid_ppn = []
    for temp_file in findchips_files:
        sheetContent = ExcelHelp.read_sheet_content_by_name(file_name=temp_file, sheet_name='findchip_stock')
        for row in sheetContent:
            if row[3] == 'False' or row[3] == False:
                unvalid_ppn.append(str(row[0]))
    print(unvalid_ppn)
    result = list(set(current_ppn).difference(set(unvalid_ppn)))
    result.sort()
    ExcelHelp.add_arr_to_col(file_name=source_file, sheet_name='filted_ppn', dim_arr=result)


if __name__ == "__main__":
    get_unfinished_RenesasPPN()

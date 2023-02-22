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
    used_cate_files = ["/Users/liuhe/PycharmProjects/SeleniumDemo/T0806.xlsx",
                       "/Users/liuhe/PycharmProjects/SeleniumDemo/T0815.xlsx",
                       "/Users/liuhe/PycharmProjects/SeleniumDemo/T0829zmz.xlsx",
                       "/Users/liuhe/PycharmProjects/SeleniumDemo/T0907zmz.xlsx",
                       "/Users/liuhe/PycharmProjects/SeleniumDemo/T0909.xlsx",
                       "/Users/liuhe/PycharmProjects/SeleniumDemo/T0921.xlsx"
                       ]
    used_lists = []
    for temp_file in used_cate_files:
        file_cates = ExcelHelp.read_col_content(file_name=temp_file, sheet_name='all', col_index=1)
        used_lists = list(set(all_lists).union(set(file_cates)))
    used_lists = list(filter(None, used_lists))
    used_lists.sort()
    # valid
    result_list = list(set(all_lists).difference(set(used_lists)))
    ExcelHelp.save_one_col(file_name='/Users/liuhe/PycharmProjects/SeleniumDemo/T0927.xlsx', sheet_name='all', dim_arr=result_list)


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
    page0_PNS = ExcelHelp.read_col_content(file_name='/Users/liuhe/PycharmProjects/SeleniumDemo/TKWPage0.xlsx',
                                           sheet_name='all', col_index=1)
    all_PNInfo_arr = ExcelHelp.read_sheet_content_by_index(
        file_name='/Users/liuhe/PycharmProjects/SeleniumDemo/TKWPageMore.xlsx', sheet_index=2)
    page_more_arr = []
    for PNInfo_ele in all_PNInfo_arr:
        pn = PNInfo_ele[0]
        if pn in page0_PNS:
            continue
        else:
            info_arr = [PNInfo_ele[0], PNInfo_ele[1]]
            page_more_arr.append(info_arr)
    ExcelHelp.add_arr_to_sheet(file_name='/Users/liuhe/PycharmProjects/SeleniumDemo/TKWPageMore.xlsx',
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

def get_unfinished_IC_hot_cates():
    source_file = PathHelp.get_file_path('TSumNvmNdt', 'Task.xlsx')
    source_cates = ExcelHelp.read_col_content(file_name=source_file, sheet_name='source', col_index=1)
    unfinished_cates = source_cates

    finished_files = ['/Users/liuhe/Desktop/progress/TDiscontinue/finished/TCY7C.xlsx',
                      '/Users/liuhe/Desktop/progress/TDiscontinue/finished/TCY8C/TCY8C_IC_Hot.xlsx',
                      '/Users/liuhe/Desktop/progress/TDiscontinue/finished/TFDC_FDD_VNH_VNQ_XMC/TFDC_FDD_VNH_VNQ_XMC.xlsx',
                      '/Users/liuhe/Desktop/progress/TDiscontinue/finished/TS25_IC_Hot.xlsx',
                      '/Users/liuhe/Desktop/progress/TDiscontinue/finished/TS29.xlsx',
                      '/Users/liuhe/Desktop/progress/TDiscontinue/finished/TMMS_NRV/TMMS_NRV.xlsx',
                      '/Users/liuhe/Desktop/progress/TDiscontinue/finished/ACS/TACS_SI7.xlsx',
                      '/Users/liuhe/Desktop/progress/TSemiStar/TSemiStart.xlsx',
                      '/Users/liuhe/Desktop/progress/TMegSensor/TMagneticSensor.xlsx',
                      '/Users/liuhe/Desktop/progress/TInfineon/5H/TInfenion_5H.xlsx',
                      '/Users/liuhe/Desktop/progress/TInfineon/10H/TInfenion_10H.xlsx',
                      '/Users/liuhe/Desktop/progress/TInfineon/15H/TInfenion_15H.xlsx',
                      '/Users/liuhe/Desktop/progress/TInfineon/20H/TInfenion_20H.xlsx']
    finished_sets = set()
    for temp_file in finished_files:
        print(temp_file)
        temp_ppns = ExcelHelp.read_col_content(file_name=temp_file, sheet_name='ppn', col_index=1)
        finished_sets = set(temp_ppns).union(finished_sets)
    need_search_arr = list(set(source_cates) - finished_sets)
    need_search_col = []
    for temp_ppn in need_search_arr:
        need_search_col.append([temp_ppn])
    ExcelHelp.add_arr_to_sheet(file_name=source_file, sheet_name='ppn', dim_arr=need_search_col)


def getMagSensor():
    finished_opn = ExcelHelp.read_col_content(file_name=PathHelp.get_file_path(None, 'TInfineon_keywords.xlsx'), sheet_name='opn', col_index=1)
    wait_opn = ExcelHelp.read_col_content(file_name="/Users/liuhe/Desktop/TMagneticSensor.xlsx", sheet_name='source', col_index=1)
    copy_opn = list(set(finished_opn) & set(wait_opn))
    opn = list(set(wait_opn) - set(finished_opn))
    copy_list = []
    for temp in copy_opn:
        copy_list.append([temp])
    ExcelHelp.add_arr_to_sheet(file_name="/Users/liuhe/Desktop/TMagneticSensor.xlsx", sheet_name='copy', dim_arr=copy_list)
    opn_list = []
    for temp_opn in opn:
        opn_list.append([temp_opn])
    ExcelHelp.add_arr_to_sheet(file_name="/Users/liuhe/Desktop/TMagneticSensor.xlsx", sheet_name='opn',
                               dim_arr=opn_list)


def get_finished_ppn():
    finished_opn = ExcelHelp.read_col_content(file_name="/Users/liuhe/Desktop/TMagneticSensor.xlsx", sheet_name='copy', col_index=1)
    finished_ppn = []
    source = ExcelHelp.read_sheet_content_by_name(file_name=PathHelp.get_file_path(None, 'TInfineon_keywords.xlsx'), sheet_name='repeat_ppn')
    for (index, row_content) in enumerate(source):
        print(f'index is: {index}')
        ppn = str(row_content[0])
        opn = str(row_content[2]) + str(row_content[3])
        if ppn and opn:
            if opn in finished_opn:
                finished_ppn.append([ppn, 'Infineon', opn])
        else:
            break
    ExcelHelp.add_arr_to_sheet(file_name="/Users/liuhe/Desktop/TMagneticSensor.xlsx", sheet_name='finished_ppn',
                               dim_arr=finished_ppn)





if __name__ == "__main__":
    # get_zmz_cate()
    # change_file_name()
    # get_page_more_PN()
    # get_unfinished_IC_hot_cates()
    # decompositionPPN(1000)
    # projectf_ile = PathHelp.get_file_path(None, 'TInfineon_keywords.xlsx')
    # current_task = PathHelp.get_file_path(None, 'TInfenion_20H.xlsx')
    # createDayTask(project_file=projectf_ile, start_index=1500, end_index=2000, aim_file=current_task)
    get_unfinished_IC_hot_cates()

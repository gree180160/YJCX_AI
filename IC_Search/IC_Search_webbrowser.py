from WRTools import UserAgentHelper, ExcelHelp, PathHelp, WaitHelp, UserInput
import webbrowser
import os


#  manu part
def get_url(cate_name, isWeek) -> str:
    if isWeek:
        search_url = f'https://icpi.ic.net.cn/icpi/detail.php?key={cate_name}'
    else:
        search_url = f'https://icpi.ic.net.cn/icpi/detail_month.php?key={cate_name}'
    return search_url


def open_url(isWeek):
    pn_file = PathHelp.get_file_path('TSumNvmNdt', 'Task.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=1)
    for (index, ppn) in enumerate(ppn_list):
        if index in range(0, 74): #
            url = get_url(cate_name=ppn, isWeek=isWeek)
            print(f'index is：{index} USL is: {url}')
            # UserInput.input_url(url, wait_time_kind=1)
            webbrowser.open(url)
            WaitHelp.waitfor_account_import(is_load_page=True, isDebug=False)
            # UserInput.webpage_saveAndClose()

# def open_url(isWeek):
#     pn_file = PathHelp.get_file_path('TMagSensor', 'TMagneticSensor.xlsx')
#     ppn_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=1)
#     for (index, ppn) in enumerate(ppn_list):
#         if index in range(0, 28): # 0-180
#             url = get_url(cate_name=ppn, isWeek=isWeek)
#             print(f'index is：{index} USL is: {url}')
#             # UserInput.input_url(url, wait_time_kind=1)
#             webbrowser.open(url)
#             WaitHelp.waitfor_account_import(is_load_page=True, isDebug=False)
#             # UserInput.webpage_saveAndClose()


# 将pn 写入excel的某一行中
def input_cate(isWeek):
    pn_file = PathHelp.get_file_path("TInfenion_10H", 'TInfenion_10H.xlsx')
    pns = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=1)
    for (index, pn) in enumerate(pns):
        ExcelHelp.write_cell(file_name=pn_file, sheet_name='search_week' if isWeek else 'search_month', col=2 + index,
                             row=1, value=pn)


def change_screenShotName(fold_path):
    pn_file = PathHelp.get_file_path('TSumNvmNdt', 'Task.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=1)[0:74]
    file_name_list = os.listdir(fold_path)
    valid_files = []
    for (index, temp) in enumerate(file_name_list):
        if temp.startswith("火狐截图_"):
            valid_files.append(temp)
    print(valid_files)
    valid_files.sort()
    for (index, temp) in enumerate(valid_files):
        print(temp)
        if True:
            is_week_data = index < ppn_list.__len__()
            print(ppn_list[index % ppn_list.__len__()])
            imageName_new = ppn_list[index % ppn_list.__len__()] + ('_W' if is_week_data else '_M') + '.png'
            os.rename(fold_path + '/' + temp, fold_path + '/' + imageName_new)


if __name__ == '__main__':
    open_url(isWeek=True)
    # change_screenShotName(fold_path='/Users/liuhe/Desktop/temp_hot')
    # input_cate(True)
    # input_cate(False)

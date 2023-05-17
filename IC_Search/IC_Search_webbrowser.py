from WRTools import UserAgentHelper, ExcelHelp, PathHelp, WaitHelp, UserInput
import Manager.URLManager
import webbrowser
import os
from Manager import TaskManager


# #  manu part
# def get_url(cate_name, isWeek) -> str:
#     if isWeek:
#         search_url = f'https://icpi.ic.net.cn/icpi/detail.php?key={cate_name}'
#     else:
#         search_url = f'https://icpi.ic.net.cn/icpi/detail_month.php?key={cate_name}'
#     return search_url


def open_url(isWeek):
    pn_file = PathHelp.get_file_path(TaskManager.Taskmanger().task_name, 'Task.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=1)
    for (index, ppn) in enumerate(ppn_list):
        if index in range(TaskManager.Taskmanger.start_index, TaskManager.Taskmanger.end_index):
            url = Manager.URLManager.IC_hot_url(ppn, isWeek)
            print(f'index is：{index} USL is: {url}')
            # UserInput.input_url(url, wait_time_kind=1)

            webbrowser.open(url)
            WaitHelp.waitfor_account_import(is_load_page=True, isDebug=False)
            # UserInput.webpage_saveAndClose()


def change_screenShotName(fold_path):
    pn_file = PathHelp.get_file_path(TaskManager.Taskmanger().task_name, 'Task.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=1)[TaskManager.Taskmanger.start_index: TaskManager.Taskmanger.end_index]
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
            right_ppn = ppn_list[index % ppn_list.__len__()].replace('/', '%2F')
            imageName_new = right_ppn + ('_W' if is_week_data else '_M') + '.png'
            os.rename(fold_path + '/' + temp, fold_path + '/' + imageName_new)


if __name__ == '__main__':
     open_url(isWeek=True)
    # change_screenShotName(fold_path='/Users/liuhe/Desktop/temp_hot')
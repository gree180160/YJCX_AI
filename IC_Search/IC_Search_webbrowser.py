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


if __name__ == '__main__':
     open_url(isWeek=True)
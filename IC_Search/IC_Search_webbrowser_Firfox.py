from WRTools import ExcelHelp, PathHelp, WaitHelp
import Manager.URLManager
import webbrowser
from Manager import TaskManager


# #  manu part
# def get_url(cate_name, isWeek) -> str:
#     if isWeek:
#         search_url = f'https://icpi.ic.net.cn/icpi/detail.php?key={cate_name}'
#     else:
#         search_url = f'https://icpi.ic.net.cn/icpi/detail_month.php?key={cate_name}'
#     return search_url


def open_url(isWeek):
    firefox_path = '/Applications/Firefox.app/Contents/MacOS/firefox'
    webbrowser.register('firefox', None, webbrowser.BackgroundBrowser(firefox_path))

    pn_file = PathHelp.get_file_path(None, f'{TaskManager.Task_IC_hot_C_manger().task_name}.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=1)
    for (index, ppn) in enumerate(ppn_list):
        if index in range(TaskManager.Task_IC_hot_F_manger().start_index, TaskManager.Task_IC_hot_F_manger.end_index):
            url = Manager.URLManager.IC_hot_url(ppn, isWeek)
            print(f'index is：{index} USL is: {url}')
            webbrowser.get('firefox').open_new(url)
            WaitHelp.waitfor_account_import(is_load_page=True, isDebug=False)


if __name__ == '__main__':
     open_url(isWeek=True)
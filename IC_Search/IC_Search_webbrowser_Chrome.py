from WRTools import ExcelHelp, PathHelp, WaitHelp
import Manager.URLManager
import webbrowser


# #  manu part
# def get_url(cate_name, isWeek) -> str:
#     if isWeek:
#         search_url = f'https://icpi.ic.net.cn/icpi/detail.php?key={cate_name}'
#     else:
#         search_url = f'https://icpi.ic.net.cn/icpi/detail_month.php?key={cate_name}'
#     return search_url


def open_url(isWeek):
    chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    webbrowser.register('Chrome', None, webbrowser.BackgroundBrowser(chrome_path))

    pn_file = PathHelp.get_file_path(None, f'00.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=1)
    for (index, ppn) in enumerate(ppn_list):
        if index in range(0, 0):
            url = Manager.URLManager.IC_hot_url(ppn)
            print(f'index is：{index} USL is: {url}')
            webbrowser.get('Chrome').open_new(url)
            WaitHelp.waitfor_account_import(is_load_page=True, isDebug=False)


if __name__ == '__main__':
     open_url(isWeek=True)
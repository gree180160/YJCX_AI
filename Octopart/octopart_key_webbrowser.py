import webbrowser
from WRTools import ExcelHelp, PathHelp, UserInput
from Manager import URLManager


def open_ppn():
    keyword_source_file = PathHelp.get_file_path(super_path=None, file_name='TNXP.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='opn', col_index=1)
    for (index, ppn) in enumerate(ppn_list):
        if index in range(1720, 2500):
            manu = "NXP"
            url = URLManager.octopart_get_code_url(key_name=ppn, page=1, manu=manu)
            print(f'index is: {index} url is: {url}')
            UserInput.input_url(url, wait_time_kind=-1)
            UserInput.webpage_saveAndClose()


def open_url():
    keyword_source_file = PathHelp.get_file_path(super_path=None, file_name='TSkyworks.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='url_pagemore2', col_index=1)
    for (index, url) in enumerate(ppn_list):
        if index in range(309, 500):  # 0-450, 450-900,900-1350,1350-1800
            print(f'index is: {index} url is: {url}')
            UserInput.input_url(url, wait_time_kind=-1)
            UserInput.webpage_saveAndClose()


if __name__ == "__main__":
    open_ppn()
    #  open_url()
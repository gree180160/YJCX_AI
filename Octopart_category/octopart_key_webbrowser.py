import webbrowser
from WRTools import ExcelHelp, PathHelp, UserInput
from Manager import URLManager

def open_url():
    keyword_source_file = PathHelp.get_file_path(super_path='TInfineionAgencyStock2', file_name='TInfineonAgencyStock2.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='ppn', col_index=1)
    for (index, ppn) in enumerate(ppn_list):
        if index in range(0, 50):  # 0-450, 450-900,900-1350,1350-1800
            manu = URLManager.Octopart_manu.Infineon
            url = URLManager.octopart_get_page_url(key_name=ppn, page=1, manu=manu)
            print(f'index is: {index} url is: {url}')
            UserInput.input_url(url, wait_time_kind=-1)
            UserInput.webpage_saveAndClose()


if __name__ == "__main__":
    open_url()
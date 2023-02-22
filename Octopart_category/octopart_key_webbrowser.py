import webbrowser
from WRTools import ExcelHelp, PathHelp, UserInput
import os


#  通用的octopart url 获取
def get_url(key_name, page, alpha, manu_ids) -> str:
    manu_param = '&manufacturer_id=' + manu_ids.replace(';', '&manufacturer_id=')
    page_param = '' if page == 1 else '&start=' + str(page*10 - 10)
    url = f'view-source:https://octopart.com/search?q={key_name}{alpha}&currency=USD&specs=0{manu_param}{page_param}'
    return url


# infenion
def get_url_infenion(key_name, page) -> str:
    #url = f'view-source:https://octopart.com/search?q={key_name}&currency=USD&specs=0'
    url = get_url(key_name=key_name, alpha='', page=page, manu_ids='453;202;706;12547;196')
    return url


def open_url():
    keyword_source_file = PathHelp.get_file_path(super_path='TInfineionAgencyStock2', file_name='TInfineonAgencyStock2.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='ppn', col_index=1)
    for (index, ppn) in enumerate(ppn_list):
        if index in range(0, 50):  # 0-450, 450-900,900-1350,1350-1800
            url = get_url_infenion(key_name=ppn, page=0)
            print(f'index is: {index} url is: {url}')
            UserInput.input_url(url, wait_time_kind=-1)
            UserInput.webpage_saveAndClose()


if __name__ == "__main__":
    open_url()
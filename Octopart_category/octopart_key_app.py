import webbrowser
from WRTools import ExcelHelp, PathHelp, WaitHelp
from pathlib import Path


def open_url():
    keyword_source_file = PathHelp.get_file_path(super_path=None, file_name='TKeywords.xlsx')
    url_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='urls', col_index=1)
    for (index, temp_url) in enumerate(url_list):
        if index in range(252, 252+36) and index%3 == 0:
            print(index)
            webbrowser.open(temp_url)
            WaitHelp.waitfor(True, False)


def open_url_notDefalut():
    chromePath = "/Applications/Google Chrome.app"
    webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chromePath))
    webbrowser.get('chrome').open("https://www.baidu.com/index.php?tn=monline_3_dg", new=1, autoraise=True)
    webbrowser.open("https://www.baidu.com/index.php?tn=monline_3_dg")
    return
    keyword_source_file = PathHelp.get_file_path(super_path=None, file_name='TKeywords.xlsx')
    url_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='urls', col_index=1)
    valid_urls = url_list[36 * 4:36 * 5]
    for (index, temp_url) in enumerate(valid_urls):
        if index % 3 == 0:
            chromePath = r"/Applications/Google Chrome.app"
            webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chromePath))
            webbrowser.open(temp_url)
            WaitHelp.waitfor_octopart(True, False)


if __name__ == "__main__":
    open_url()
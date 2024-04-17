import ssl
import time
from WRTools import ChromeDriverManager
from selenium.webdriver.common.by import By

from WRTools import LogHelper, ExcelHelp, WaitHelp, EmailHelper, PathHelp

ssl._create_default_https_context = ssl._create_unverified_context


driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(1000)

default_url = 'https://www.b2b-center.ru/'


result_save_file = PathHelp.get_file_path("Tender", 'Task.xlsx')
result_save_sheet = 'actual'

log_file = PathHelp.get_file_path(super_path="Tender", file_name='B2BLog.txt')


# 跳转到下一个指定的型号 page , 的那一页
def go_to_page(url):
    try:
        driver.get(url)
        WaitHelp.waitfor_octopart(True, False)
        analyth_html(url)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'go_to_cate except: {e}')
        if str(e.msg).__contains__('Timed out'):
            driver.reconnect()


# 解析html，获取cate，manu
def analyth_html(url):
    try:
        all_cates_table = driver.find_elements(By.TAG_NAME, 'tbody')
        if all_cates_table.__len__() > 0:
            showed_rows = all_cates_table[0].find_elements(By.CSS_SELECTOR, 'tr.c2')
        # 默认直接显示的row
        table_value = []
        for temp_cate_row in showed_rows:
            try:
                tds = temp_cate_row.find_elements(By.TAG_NAME, 'td')
                row_content_arr = []
                for temp_td in tds:
                    row_content_arr.append(temp_td.text)
                table_value.append(row_content_arr)
            except Exception as e:
                LogHelper.write_log(log_file_name=log_file, content=f'{url} 当个cate 解析异常：{e} ')
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{url} 页面 解析异常：{e} ')
    ExcelHelp.add_arr_to_sheet(
        file_name=result_save_file,
        sheet_name=result_save_sheet,
        dim_arr=table_value)


def main():
    total_page = 45
    page = 1
    while page <= total_page:
        if page % 15 == 0:
            time.sleep(60*10)
        url = f'https://www.b2b-center.ru/market/realizatsiia-elektrotekhnicheskogo-oborudovaniia-i-avtomatiki-i/tender-3374892/?action=positions&from={(page-1)*20}'
        print(url)
        go_to_page(url=url)
        page += 1


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(True, False)
    main()

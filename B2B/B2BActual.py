import os.path
import ssl
import math
import time
from datetime import datetime, timedelta

from WRTools import ChromeDriverManager
from selenium.webdriver.common.by import By

from WRTools import LogHelper, ExcelHelp, WaitHelp, EmailHelper, PathHelp

ssl._create_default_https_context = ssl._create_unverified_context

driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(1000)

default_url = 'https://www.b2b-center.ru/'
result_save_file = PathHelp.get_file_path("B2B", 'Task.xlsx')
result_save_sheet = 'Sheet'
log_file = PathHelp.get_file_path(super_path="Tender", file_name='B2BLog.txt')

sourceFile_dic = {'fileName': PathHelp.get_file_path("B2B", 'Task.xlsx'),
                  'sourceSheet': 'keywords',
                  'colIndex': 1,
                  'startIndex': 124,
                  'endIndex': 173} #199

current_page = 1
total_page = 1

detail_url_list = []
No_value_list = []


def set_total_page():
    global total_page
    search_ctrls = driver.find_element(By.ID, 'search-result')
    types = search_ctrls.find_elements(By.TAG_NAME, 'a')
    if types.__len__() > 0:
        actual = types[0].text.replace(" ", '').replace('Актуально•', '')
        total_page = math.ceil(int(actual)/20)


def get_url(keyword, page):
    today = datetime.today() - timedelta(days=1)
    yesterday = datetime.today() - timedelta(days=1)
    data_start = today.strftime("%d.%m.%Y")
    data_end = yesterday.strftime("%d.%m.%Y")
    actural_url = f'https://www.b2b-center.ru/market/?f_keyword={keyword}&searching=1&company_type=2&price_currency=0&date=1&date_start_dmy={data_start}&date_end_dmy={data_end}&trade=buy&from={(page -1)*20}#search-result'
    archive_url = f'https://www.b2b-center.ru/market/?f_keyword={keyword}&searching=1&company_type=2&price_currency=0&date=1&date_start_dmy=01.08.2018&date_end_dmy=08.08.2023&trade=buy&show=archive&from={(page -1)*20}#search-result'
    result = actural_url
    return result


# 跳转到下一个指定的型号 page , 的那一页
def go_to_page(keyword, page):
    try:
        url = get_url(keyword, page)
        driver.get(url)
        print(f'keyword is: {keyword}, current_pages is: {current_page} total_page is: {total_page}')
        WaitHelp.waitfor_octopart(True, False)
        analyth_page(url, keyword)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'go_manu except: {e}')
        if str(e.msg).__contains__('Timed out'):
            driver.reconnect()


def analyth_keyword(keyword):
    global current_page
    total_page = 1
    current_page = 1
    while current_page <= total_page:
        go_to_page(keyword, current_page)
        if current_page == 1:
            set_total_page()
        current_page += 1


# 解析html，获取cate，manu
def analyth_page(url, keyword):
    global No_value_list, detail_url_list
    table_value = []
    try:
        tables = driver.find_elements(By.CSS_SELECTOR, 'table.table.table-hover.table-filled.search-results')
        if tables.__len__() > 0:
            table = tables[0]
            tbody = table.find_element(By.TAG_NAME, 'tbody')
            trs = tbody.find_elements(By.TAG_NAME, 'tr')
            No = title = detail = link = org = published = relevant = ''
            for row in trs:
                tds = row.find_elements(By.TAG_NAME, 'td')
                for (td_index, temp_td) in enumerate(tds):
                    if td_index == 0:
                        link = temp_td.find_element(By.CSS_SELECTOR, 'a.search-results-title.visited').get_attribute(
                            "href")
                        No = temp_td.find_element(By.TAG_NAME, 'a').text
                        index = No.index('№ ')
                        No = No[index + 2:-1]
                        if str(No).__contains__('\n'):
                            index2 = No.index('\n')
                            No = No[0:index2]
                        try:
                            title = temp_td.find_elements(By.TAG_NAME, 'div')[0].text
                            No = str(No).replace(title, '')
                        except Exception as e:
                            title = ''
                            print(f'title or {e}')
                        try:
                            detail = temp_td.find_elements(By.TAG_NAME, 'div')[1].text
                        except Exception as e:
                            detail = ''
                            print(f'detail or {e}')
                    elif td_index == 1:
                        org = temp_td.text
                    elif td_index == 2:
                        published = temp_td.text
                    else:
                        relevant = temp_td.text
                row_value = [keyword, No, title, detail, link, org, published, relevant]
                if No_value_list.__contains__(No) or detail_url_list.__contains__(link):
                    print(f'repeated value: {No} ; {link}')
                else:
                    table_value.append(row_value)
                    No_value_list.append(No)
                    detail_url_list.append(link)
        else:
            row_value = [keyword, 'No record']
            table_value.append(row_value)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{url} 页面 解析异常：{e} ')
    if table_value.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(
            file_name=result_save_file,
            sheet_name=result_save_sheet,
            dim_arr=table_value)


def sendEmail(result_file):
    EmailHelper.sendAttachment(result_save_file, 'B2B_Actual')


def main():
    keyword_list = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    adjust_excel()
    for (keyword_index, keyword) in enumerate(keyword_list):
        if keyword_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            if keyword:
                print(f'cate_index is: {keyword_index}  cate_name is: {keyword}')
                analyth_keyword(keyword)
    sendEmail(result_save_file)


def adjust_excel():
    global result_save_file
    today = time.strftime('%Y-%m-%d', time.localtime())
    result_save_file = PathHelp.get_file_path('B2B', f'b2b_actual_{today}_.xlsx')
    if not os.path.exists(result_save_file):
        ExcelHelp.create_excel_file(result_save_file)
        title_arr = [["keyword", "No", "title", "detail", "link", "org", "published", "relevant"]]
        ExcelHelp.add_arr_to_sheet(result_save_file, result_save_sheet, title_arr)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(True, False)
    while True:
        now = datetime.datetime.now()
        h_value = now.hour
        if h_value > 1:
            time.sleep(60 * 50)
        else:
            break
    main()

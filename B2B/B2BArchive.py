import ssl
import math
import time
from datetime import datetime, timedelta

# 获取今天的日期
today = datetime.today()

# 计算前三天的日期
three_days_ago = today - timedelta(days=3)

# 将日期转换为指定的格式
formatted_date = three_days_ago.strftime("%d.%m.%Y")

# 输出结果
print(formatted_date)


from selenium.webdriver.common.by import By

from WRTools import LogHelper, ExcelHelp, WaitHelp, EmailHelper, PathHelp

ssl._create_default_https_context = ssl._create_unverified_context

from selenium import webdriver
options = webdriver.ChromeOptions()
# 去除“Chrome正受到自动测试软件的控制”的显示
options.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=options)
# 设置headers
driver.execute_cdp_cmd("Network.setExtraHTTPHeaders",
                       {"headers":
                            {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
                                }
                        })

# 防止网站检测selenium的webdriver
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => False
            })
        """})



default_url = 'https://www.b2b-center.ru/'
result_save_file = PathHelp.get_file_path("B2B", 'Task.xlsx')
#todo for page
result_save_sheet = 'archive_page'
log_file = PathHelp.get_file_path(super_path="Tender", file_name='B2BLog.txt')

sourceFile_dic = {'fileName': PathHelp.get_file_path("B2B", 'Task.xlsx'),
                  'sourceSheet': 'keywords',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 226}

current_page = 1
total_page = 1


def set_total_page(keyword):
    global total_page
    search_ctrls = driver.find_element(By.ID, 'search-result')
    types = search_ctrls.find_elements(By.TAG_NAME, 'a')
    if types.__len__() > 0:
        archive = types[1].text.replace(' ', '').replace('Вархиве•', '')
        total_page = math.ceil(int(archive) / 20)
        arr = [[keyword, archive]]
        ExcelHelp.add_arr_to_sheet(result_save_file, result_save_sheet, arr)
        # print(f'{driver.current_url} total_page is: {total_page}')


def get_url(keyword, page):
    today = datetime.today()
    three_years_ago = today - timedelta(days=365*3)
    data_start = three_years_ago.strftime("%d.%m.%Y")
    data_end = today.strftime("%d.%m.%Y")
    # https://www.b2b-center.ru/market/?f_keyword=ASUS&searching=1&company_type=2&price_currency=0&date=1&date_start_dmy=60.08.2023&date_end_dmy=09.08.2023&trade=buy&show=archive#search-result
    #actual_url = f'https://www.b2b-center.ru/market/?f_keyword={keyword}&searching=1&company_type=2&price_currency=0&date=1&date_start_dmy=01.08.2018&date_end_dmy=08.08.2023&trade=buy&from={(page - 1) * 20}#search-result'
    achive_url = f'https://www.b2b-center.ru/market/?f_keyword={keyword}&searching=1&company_type=2&price_currency=0&date=1&date_start_dmy={data_start}&date_end_dmy={data_end}&trade=buy&show=archive&from={(page -1)*20}#search-result'
    result = achive_url
    return result


# 跳转到下一个指定的型号 page , 的那一页
def go_to_page(keyword, page):
    try:
        url = get_url(keyword, page)
        driver.get(url)
        WaitHelp.waitfor_account_import(True, False)
        analyth_page(url, keyword)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'go_manu except: {e}')
        if str(e.msg).__contains__('Timed out'):
            driver.reconnect()


def analyth_keyword(keyword):
    global current_page, total_page
    total_page = 1
    current_page = 1
    # todo for page
    while current_page <= 1: #total_page:
        go_to_page(keyword, current_page)
        if current_page == 1:
            set_total_page(keyword)
        current_page += 1


# 解析html，获取cate，manu
def analyth_page(url, keyword):
    table_value = []
    try:
        table = driver.find_element(By.CSS_SELECTOR, 'table.table.table-hover.table-filled.search-results')
        if table:
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
                        try:
                            title = temp_td.find_elements(By.TAG_NAME, 'div')[0].text
                            No = No.replace(title, '')
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
                row_value = [keyword, No, title, detail, link, org, published, relevant,
                             time.strftime('%Y-%m-%d', time.localtime())]
                table_value.append(row_value)
        else:
            row_value = [keyword, '0']
            table_value.append(row_value)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{url} 页面 解析异常：{e} ')
    # todo for page
    # if table_value.__len__() > 0:
    #     ExcelHelp.add_arr_to_sheet(
    #         file_name=result_save_file,
    #         sheet_name=result_save_sheet,
    #         dim_arr=table_value)


def main():
    keyword_list = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    for (keyword_index, keyword) in enumerate(keyword_list):
        if keyword_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {keyword_index}  cate_name is: {keyword}')
            analyth_keyword(keyword)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(True, False)
    main()

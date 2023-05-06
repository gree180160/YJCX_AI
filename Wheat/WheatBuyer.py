# 根据ppn获取buyer
import datetime
import time
'''
# 链接：https://app.51wheatsearch.com/gs/index.html#/login
# 选择子账号登录
# 公司名称：深圳市元极创新电子有限公司
#  19805243800   Yjcx12345!
#  13316837463    Yjcx12345!
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import ssl
from WRTools import IPHelper, UserAgentHelper, ExcelHelp, WaitHelp, PathHelp, LogHelper
import time

ssl._create_default_https_context = ssl._create_unverified_context

sourceFile_dic = {'fileName': PathHelp.get_file_path('Wheat', 'WheatTask.xlsx'),
                  'sourceSheet': 'manu',
                  'colIndex': 1,
                  'startIndex': 2,
                  'endIndex': 15}
result_save_file = PathHelp.get_file_path('Wheat', 'wheat_buyer.xlsx')
logFile = PathHelp.get_file_path('Wheat', 'Wheat_buyer_log.txt.txt')

login_url = 'https://app.51wheatsearch.com/gs/index.html#/login'
default_url = 'https://app.51wheatsearch.com/gs/index.html#/resource/gather/customs'
total_page = 1
current_page = 1 # infenion 15

driver_option = webdriver.ChromeOptions()
driver_option.add_argument(f'--proxy-server=http://{IPHelper.getRandowCityIP()}')
driver_option.add_argument("–incognito")
#  等待初始HTML文档完全加载和解析，
driver_option.page_load_strategy = 'eager'
driver_option.add_argument(f'user-agent="{UserAgentHelper.getRandowUA_Mac()}"')
prefs = {"profile.managed_default_content_settings.images": 2}
driver_option.add_experimental_option('prefs', prefs)
driver = uc.Chrome(use_subprocess=True)
driver.set_page_load_timeout(1000)


# 登陆
def loginAction(aim_url):
    WaitHelp.waitfor_account_import(True, False)


# search one ppn
def goToPPN(ppn: str, manu: str):
    try:
        #set ppn
        try:
            clear_button = driver.find_elements(By.CSS_SELECTOR, "span.ant-input-clear-icon.ant-input-clear-icon-has-suffix")[0]
            svg = clear_button.find_element(By.TAG_NAME,'svg')
            svg.click()
        except:
            print('can not click keyword clear button')
        input_area_keyword = driver.find_elements(By.CSS_SELECTOR, value='input.ant-input')[1]
        input_area_keyword.send_keys(ppn)
        # set supplier
        if manu and manu.__len__() > 0:
            try:
                clear_button = \
                driver.find_elements(By.CSS_SELECTOR, "span.ant-input-clear-icon")[4]
                svg = clear_button.find_element(By.TAG_NAME, 'svg')
                svg.click()
            except:
                print('can not click supplier clear button')
            input_area_supplier = driver.find_elements(By.CSS_SELECTOR, value='input.ant-input')[4]
            input_area_supplier.send_keys(manu)
        search_button = driver.find_elements(By.CSS_SELECTOR, 'button.ant-btn.ant-btn-primary')[2]
        search_button.click()
    except:
        print('input ppn error')


def get_page_info(for_current):
    global current_page, total_page
    if for_current:
        try:
            current = driver.find_element(By.CSS_SELECTOR, 'li.ant-pagination-item-active')
            current_page = int(current.text)
            print(f'current_page is: {current_page}')
        except:
            print('get current page error')
    else:
        try:
            page_container = driver.find_elements(By.TAG_NAME, 'ul')[3]
            page_elements = page_container.find_elements(By.TAG_NAME, 'li')
            if page_elements.__len__() == 3:
                total_page = 1
            else:
                total_page_li = page_elements[-3]
                total_page = int(total_page_li.text)
            print(f'total_page is: {total_page}')
        except:
            total_page = 0
            print('get total page error')


def go_to_next_page(cate_index, cate_name):
    now = datetime.datetime.now()
    h_value = (now.hour)
    if h_value >= 22 or h_value <= 9:
        return
    if current_page < total_page:
        try:
            next_page_li = driver.find_element(By.CSS_SELECTOR, 'li.ant-pagination-next')
            next_button = next_page_li.find_element(By.CSS_SELECTOR, 'button.ant-pagination-item-link')
            next_button.click()
            WaitHelp.waitfor_account_import(True, False)
            anly_webdriver(cate_index, cate_name)
        except:
            print('click next page button error')


# 分析html 文件
def anly_webdriver(cate_index, cate_name):
    get_page_info(for_current=True)
    if total_page == 1:
        get_page_info(for_current=False)
    if total_page <= 0:
        return
    result = []
    try:
        table_container = driver.find_element(By.CSS_SELECTOR, 'div.ant-table.ant-table-ping-right.ant-table-fixed-column.ant-table-scroll-horizontal.ant-table-has-fix-right')
        table = table_container.find_element(By.TAG_NAME, 'table')
        tbody = table.find_element(By.CSS_SELECTOR, 'tbody.ant-table-tbody')
        row_list = tbody.find_elements(By.CSS_SELECTOR, 'tr.ant-table-row.ant-table-row-level-0')
        for row in row_list:
            row_info = get_rowInfo(cate_name, row)
            result.append(row_info)
        if row_list.__len__() > 0:
            ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name='manu_record', dim_arr=result)
            if current_page < total_page:
                go_to_next_page(cate_index, cate_name)
    except Exception as e:
        print('anly_webdriver error')



def get_rowInfo(cate_name, row):
    # ['cate_name', 'data', 'buyer', 'supplier', 'des', 'buy_contry', 'supplier_contry', current_time]
    td_list = row.find_elements(By.TAG_NAME, 'td')
    result = [cate_name, td_list[0].text, td_list[1].text.replace('/', '%2F'), td_list[2].text, td_list[3].text, td_list[4].text, td_list[5].text, time.strftime('%Y-%m-%d', time.localtime())]
    return result


def main():
    global total_page, current_page
    all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    for (cate_index, cate_name) in enumerate(all_cates):
        now = datetime.datetime.now()
        h_value = now.hour
        if h_value >= 22 or h_value <= 9:
            continue
        if cate_name is None or cate_name.__contains__('?'):
            continue
        elif cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
            goToPPN(ppn=cate_name, manu=cate_name)
            WaitHelp.waitfor_account_import(True, False)
            current_page = total_page = 1
            anly_webdriver(cate_index=cate_index, cate_name=cate_name)


if __name__ == "__main__":
    driver.get(default_url)
    loginAction(default_url)
    main()

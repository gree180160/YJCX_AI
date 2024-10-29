# 根据ppn获取buyer index 4 page 134 goon;
# ['Siemens', '2022-02-24', 'Ооо Сименс', 'Siemens Building Technologies Ltd', 'ИЗДЕЛИЕ ИЗ ПЛАСТМАСС (ШТАМПОВКА):', '俄罗斯', '德国', '2023-05-14', '42']
# 2021-07-16

import datetime
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from WRTools import ChromeDriverManager
import ssl
from Manager import AccManage, TaskManager
from WRTools import ExcelHelp, WaitHelp, PathHelp, LogHelper
import time
import re

accouts_arr = [AccManage.Wheat['c'], AccManage.Wheat['n'], AccManage.Wheat['p']]
ssl._create_default_https_context = ssl._create_unverified_context

# sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TInfineonIGBT.xlsx'),
#                   'sourceSheet': 'ppn',
#                   'colIndex': 1,
#                   'startIndex': 793,
#                   'endIndex': 1000}
sourceFile_dic = {'fileName': PathHelp.get_file_path('TradeWebs', 'Mornsun.xlsx'),
                  'sourceSheet': 'brand',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 4}
result_save_file = PathHelp.get_file_path('TradeWebs', 'Mornsun.xlsx')
result_save_sheet = 'Wheat_buyer'
logFile = PathHelp.get_file_path('Wheat', 'Wheat_log.txt')
login_url = 'https://app.51wheatsearch.com/gs/index.html#/login'
# default_url = 'https://app.51wheatsearch.com/gs/index.html#/resource/gather/customs'
default_url = 'https://app.51wheatsearch.com/gs/index.html#/resource/customs/queryTools'
total_page = 1
current_page = 1 #infenion 305

driver_option = webdriver.ChromeOptions()
driver_option.add_argument("–incognito")
#  等待初始HTML文档完全加载和解析，
driver_option.page_load_strategy = 'eager'
prefs = {"profile.managed_default_content_settings.images": 2}
driver_option.add_experimental_option('prefs', prefs)
driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(1000)


# 登陆
def loginAction(aim_url):
    driver.get(aim_url)
    time.sleep(5.0)
    login_types = driver.find_elements(By.CSS_SELECTOR, 'div.ant-tabs-tab')
    if login_types.__len__() > 0:
        time.sleep(10.0)
        sub_long = login_types[1]
        sub_long.click()
        time.sleep(3.0)
        company_name = driver.find_element(By.CSS_SELECTOR, '#mobileOrName')
        company_name.clear()
        company_name.send_keys(accouts_arr[0])
        use_name = driver.find_element(By.CSS_SELECTOR, '#emailOrMobile')
        use_name.clear()
        use_name.send_keys(accouts_arr[1])
        pw = driver.find_element(By.CSS_SELECTOR, '#password')
        pw.clear()
        pw.send_keys(accouts_arr[2])
        time.sleep(3.0)
        login_button = driver.find_elements(By.TAG_NAME, 'button')[-1]
        login_button.click()
        WaitHelp.waitfor(True, False)
    else:
        print('login error')
        sys.exit()


def set_filter(start_date:str, end_date:str):
    driver.get(default_url)
    WaitHelp.waitfor(True, False)
    #submit form
    card_one = driver.find_elements(By.CSS_SELECTOR, 'div.ant-card-body')[0]
    sub_form = card_one.find_elements(By.CSS_SELECTOR, 'div.ant-space-item')[2]
    sub_form.click()
    WaitHelp.waitfor(False, False)
    #set filters
    # clear default date
    ac = ActionChains(driver)
    pick_start = driver.find_elements(By.CSS_SELECTOR, 'span.ant-picker-suffix')[0]
    ac.move_to_element(pick_start)
    ac.click(pick_start).perform()
    start_picker = driver.find_elements(By.CSS_SELECTOR, 'div.ant-picker')[0]
    start_input = start_picker.find_element(By.TAG_NAME, 'input')
    start_input.send_keys(start_date)
    # end date
    # clear default date
    pick_end = driver.find_elements(By.CSS_SELECTOR, 'span.ant-picker-suffix')[1]
    ac.move_to_element(pick_end)
    ac.click(pick_end).perform()
    end_picker = driver.find_elements(By.CSS_SELECTOR, 'div.ant-picker')[1]
    end_picker = end_picker.find_element(By.TAG_NAME, 'input')
    end_picker.send_keys(end_date)
    # 为了让结束日期有效，假装设置提单号，让日历选择器结束工作
    input_card_content(0, '')


# search one ppn
def goToPPN(ppn: str, manu: str):
    try:
        input_card_content(1, ppn)
        if manu and manu.__len__() > 0:
            input_card_content(4, manu)
        time.sleep(2.0)
        #ant-btn ant-btn-primary , 保持搜索按钮在关键词下面
        search_button = driver.find_elements(By.CSS_SELECTOR, 'button.ant-btn.ant-btn-primary')[2]
        search_button.click()
    except Exception as e:
        LogHelper.write_log(logFile, f'click search_button error {e}')


# 在input 中delete old content ,input new content
# item: [提单号, 产品关键词, 产品关键词HS, 采购商名称, 供应商名称]
def input_card_content(item_index: int , new_content: str):
    try:
        filter_form_area = driver.find_element(By.CSS_SELECTOR, value='form.ant-form.ant-form-vertical')
        input_item = filter_form_area.find_elements(By.CSS_SELECTOR, value='input.ant-input')[item_index]
        old_keyword = input_item.get_attribute('value')
        if old_keyword and old_keyword.__len__() > 0:
            ac = ActionChains(driver)
            try:
                clear_button = filter_form_area.find_elements(By.CSS_SELECTOR, value='span.ant-input-clear-icon')[
                    item_index]
                svg = clear_button.find_element(By.TAG_NAME, 'svg')
                ac.move_to_element(svg)
                ac.click(svg).perform()
            except:
                print('can not click keyword clear button')
        input_item.send_keys(new_content)
    except Exception as e:
        LogHelper.write_log(logFile, f'set input content error item_index is: {item_index}, new content is :{new_content} {e}')


# 分析html 文件
def anly_webdriver(cate_index, cate_name):
    try:
        numberStr = driver.find_elements(By.CSS_SELECTOR, 'div.ant-tabs-tab-btn')[0].text
        numberStr = numberStr.replace('进出口数据(', '')
        numberStr = numberStr.replace(')', '')
        result = [cate_name, numberStr]
        ExcelHelp.add_arr_to_sheet(sourceFile_dic['fileName'], 'wheat_buyer_count', [result])
    except Exception as e:
        print('no record')
        LogHelper.write_log(logFile, f'anly_webdriver error {e}')


def main():
    global total_page, current_page
    all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    for (cate_index, cate_name) in enumerate(all_cates):
        now = datetime.datetime.now()
        h_value = now.hour
        if h_value >= 22 or h_value <= 8:
            continue
        if cate_name is None or cate_name.__contains__('?'):
            continue
        elif cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
            goToPPN(ppn=cate_name, manu="")
            WaitHelp.waitfor_account_import(True, False)
            current_page = total_page = 1
            anly_webdriver(cate_index=cate_index, cate_name=cate_name)


if __name__ == "__main__":
    loginAction(default_url)
    driver.get(default_url)
    set_filter(start_date='2023-10-28', end_date='2024-10-28')
    main()

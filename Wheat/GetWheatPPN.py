# 根据ppn获取buyer index 4 page 134 goon;
# ['Siemens', '2022-02-24', 'Ооо Сименс', 'Siemens Building Technologies Ltd', 'ИЗДЕЛИЕ ИЗ ПЛАСТМАСС (ШТАМПОВКА):', '俄罗斯', '德国', '2023-05-14', '42']
# 2021-07-16
# 全世界是最近三年，俄罗斯是打仗前3年


import datetime
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from WRTools import ChromeDriverManager
import ssl
from Manager import AccManage
from WRTools import ExcelHelp, WaitHelp, PathHelp, LogHelper, MySqlHelp_recommanded
import time


accouts_arr = [AccManage.Wheat['c'], AccManage.Wheat['n'], AccManage.Wheat['p']]
ssl._create_default_https_context = ssl._create_unverified_context

# sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TInfineonIGBT.xlsx'),
#                   'sourceSheet': 'ppn',
#                   'colIndex': 1,
#                   'startIndex': 793,
#                   'endIndex': 1000}
sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TInfineonPowerManger.xlsx'),
                  'sourceSheet': 'ppn2',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 6}
task_name = "TInfineonPowerManger"
result_save_file = PathHelp.get_file_path(None, 'TInfineonPowerManger.xlsx')
result_save_sheet = 'Wheat_buyer'
logFile = PathHelp.get_file_path('Wheat', 'Wheat_log.txt')

login_url = 'https://app.51wheatsearch.com/gs/#/login'
default_url = 'https://app.51wheatsearch.com/gs/index.html#/resource/customs/queryTools' # 海关数据
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


def set_filter_all():
    # 获取今天的日期
    today = datetime.date.today()
    # 计算三年前的日期
    three_years_ago = today - datetime.timedelta(days=365 * 3)  # 近似三年
    # 格式化日期为 'YYYY-MM-DD' 格式
    end_date = today.strftime('%Y-%m-%d')
    start_date = three_years_ago.strftime('%Y-%m-%d')
    set_filter("", start_date, end_date)


def set_filter_all():
    start_date = '2019-12-31'
    end_date = '2021-12-31'
    set_filter("俄罗斯", start_date, end_date)


def set_filter(country:str, start_date:str, end_date:str):
    driver.get(default_url)
    WaitHelp.waitfor(True, False)
    # submit form
    card_one = driver.find_element(By.CSS_SELECTOR, 'div.ant-tabs-nav-list')
    sub_form = card_one.find_elements(By.CSS_SELECTOR, 'div.ant-tabs-tab')[2]
    sub_form.click()
    WaitHelp.waitfor(False, False)
    # set filters
    if country.__len__() > 0:
        select_contry = driver.find_elements(By.CSS_SELECTOR, 'span.anticon.anticon-down')[0]
        select_contry.click()
        time.sleep(3.0)
        alert_area = driver.find_elements(By.CSS_SELECTOR, 'div.ant-modal-body')[0]
        xpath = f"//button[@title='{country}']"
        ru_button = alert_area.find_elements(By.XPATH, xpath)[0]
        ru_button.click()
    # from date
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
        input_card_content(0, ppn)
        # if manu and manu.__len__() > 0:
        #     input_card_content(12, manu)
        time.sleep(2.0)
        #ant-btn ant-btn-primary , 保持搜索按钮在关键词下面
        search_button = driver.find_elements(By.CSS_SELECTOR, 'button.ant-btn.ant-btn-primary')[1]
        search_button.click()
    except Exception as e:
        LogHelper.write_log(logFile, f'click search_button error {e}')


# 在input 中delete old content ,input new content
# item: [提单号, 产品关键词, 产品关键词HS, 采购商名称, 供应商名称]
def input_card_content(item_index: int, new_content: str):
    try:
        input_item = driver.find_elements(By.CSS_SELECTOR, value='input.ant-input')[item_index]
        old_keyword = input_item.get_attribute('value')
        if old_keyword and old_keyword.__len__() > 0:
            ac = ActionChains(driver)
            try:
                clear_button = driver.find_elements(By.CSS_SELECTOR, value='span.ant-input-clear-icon')[item_index]
                svg = clear_button.find_element(By.TAG_NAME, 'svg')
                ac.move_to_element(svg)
                ac.click(svg).perform()
            except:
                print('can not click keyword clear button')
        input_item.send_keys(new_content)
    except Exception as e:
        LogHelper.write_log(logFile, f'set input content error item_index is: {item_index}, new content is :{new_content} {e}')


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
            page_container = driver.find_elements(By.TAG_NAME, 'ul')[2]
            page_elements = page_container.find_elements(By.TAG_NAME, 'li')
            if page_elements.__len__() == 3:
                total_page = 1
            else:
                total_page_li = page_elements[-3]
                total_page = int(total_page_li.text)
                total_page = min(50, total_page) #max page is 50
            print(f'total_page is: {total_page}')
        except Exception as e:
            total_page = 0
            LogHelper.write_log(logFile, f'get total page error {e}')


def set_page_count():
    try:
        page_area = driver.find_elements(By.CSS_SELECTOR, 'li.ant-pagination-options')
        if page_area.__len__() > 0:
            page_selection_items = page_area[0].find_elements(By.CSS_SELECTOR, 'span.ant-select-selection-item')
            if page_selection_items.__len__() > 0:
                page_selection_items[-1].click()
                time.sleep(2.0)
                select_options = driver.find_elements(By.CSS_SELECTOR, 'div.ant-select-item.ant-select-item-option')
                if select_options.__len__() > 0:
                    max_option = select_options[-1]
                    max_option.click()
                    WaitHelp.waitfor(True, False)
        else:
            print('no page selection')
    except Exception as e:
        LogHelper.write_log(logFile, f'set_page_count error {e}')


def go_to_next_page(cate_index, cate_name):
    now = datetime.datetime.now()
    h_value = (now.hour)
    if h_value >= 22 or h_value <= 8:
        return
    if current_page < total_page:
        try:
            next_page_li = driver.find_element(By.CSS_SELECTOR, 'li.ant-pagination-next')
            next_button = next_page_li.find_element(By.CSS_SELECTOR, 'button.ant-pagination-item-link')
            next_button.click()
            WaitHelp.waitfor_account_import(True, False)
            anly_webdriver(cate_index, cate_name)
        except Exception as e:
            LogHelper.write_log(f'click next page button error {e}')
            return


# 分析html 文件
def anly_webdriver(cate_index, cate_name, isRU):
    get_page_info(for_current=True)
    if total_page == 1: # 只获取一次total_page
        get_page_info(for_current=False)
    if total_page <= 0:
        return
    try:
        print('do what you want')
          # todo
    except Exception as e:
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
            set_page_count()
            current_page = total_page = 1
            anly_webdriver(cate_index=cate_index, cate_name=cate_name)


if __name__ == "__main__":
    loginAction(default_url)
    driver.get(default_url)
    set_filter(start_date='2019-12-31', end_date='2021-12-31')
    main()

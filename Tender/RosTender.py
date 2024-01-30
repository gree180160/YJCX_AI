#  记录Task 提供的型号，在IC 中的库存信息
import base64
import math
import re
import datetime
from selenium.webdriver.common.by import By
import time
import undetected_chromedriver as uc
import ssl
from WRTools import ExcelHelp, WaitHelp, PathHelp, EmailHelper, StringHelp, MySqlHelp_recommanded, RateHelp
from Manager import AccManage
import os

# https://rostender.info/login
# Логин: tim616
# Пароль: 4IPZjmst
# https://rostender.info/category/tendery-elektronnye-komponenty

ssl._create_default_https_context = ssl._create_unverified_context
# 定义要爬取的url

login_url = "https://rostender.info/login"
search_base_url = 'https://rostender.info/category/tendery-elektronnye-komponenty'
result_save_file = PathHelp.get_file_path('Tender', 'Task.xlsx')
result_save_sheet = 'Sheet'

# 定义一个变量来记录当前的页码

current_page = 1
total_page = 0

try:
    driver = uc.Chrome(use_subprocess=True)
    driver.set_page_load_timeout(1000)
except Exception as e:
    print(e)


def login_action():
    try:
        username = driver.find_element(By.ID, 'username')
        username.clear()
        username.send_keys(AccManage.ros['n'])
        password = driver.find_element(By.ID, 'password')
        password.clear()
        password.send_keys(AccManage.ros['p'])
        button = driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-block.btn-danger.btn-lg.login-action')
        button.click()
        # loging success url:https://rostender.info/profile
        WaitHelp.waitfor_account_import(True, False)
    except:
        print('login_action error')

def set_total_page():
    global total_page
    try:
        total_data = driver.find_elements(By.CSS_SELECTOR, 'b.main-tabs__count.count')[1].text
        total_data = total_data.replace(' ', '')
        total_page = math.ceil(int(total_data)/10)
    except:
        total_page = 0
        print(f'{driver.current_url} ; set_total_page error')


def set_currentPage():
    global current_page
    try:
        page_area = driver.find_element(By.CSS_SELECTOR, 'div.pagination')
        current_page_ele = page_area.find_elements(By.CSS_SELECTOR, 'span.current')[-1]
        current_page = int(current_page_ele.text)
    except:
        # current_page = total_page
        print(f'{driver.current_url} ; set_currentPage error')
        print(f'current_page is :{current_page} total_page is :{total_page}')
        exit(0)


def need_next_page():
    if int(current_page) < int(total_page):
        return True
    return False


def goto_nextPage():
    try:
        next_ele = driver.find_element(By.CSS_SELECTOR, 'a.page-link.next')
        driver.execute_script("arguments[0].click();", next_ele)
    except:
        print(f'{driver.current_url} ; goto_nextPage error')


def main():
    # 定义一个循环，直到爬取完所有的页码或者达到最大页码限制
    while True:
        # 打印当前的页码
        close_alert()
        print(f"正在爬取第{current_page}页...")
        # 访问网页
        # 找到所有的搜索结果，它们都在class为search-result-item的div标签里面
        items = driver.find_elements(By.CSS_SELECTOR, "div.card-item")
        # 判断是否有搜索结果
        page_result = []
        # 遍历每一个搜索结果
        for temp_item in items:
            try:
                print('analython html')
            except Exception as e:
               print('error')
        print(f'current page is {current_page}')
        ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name=result_save_sheet, dim_arr=page_result)
        # 找到下一页的按钮，它在class为next-page的a标签里面
        set_currentPage()
        next_page = need_next_page()
        # 判断是否找到下一页的按钮
        if next_page:
            # 模拟点击下一页的按钮
            goto_nextPage()
            WaitHelp.waitfor_account_import(True, False)
            set_currentPage()
        else:
            # 如果没有找到下一页的按钮，说明已经爬取完所有的页码，跳出循环
            print(f"没有更多搜索结果，爬取结束。 current_page is:{current_page} total_page is: {total_page}")
            break
    sendEmail(result_save_file)


def change_money_ru(source_str: str):
    result = source_str.replace(' ', '')
    result = result.replace(',', '.')
    numbers = re.findall(r'\d+\.?\d*', result)
    if result[-1] == '₽':
        result = result.replace('₽', '')
    elif result[-1] == '$':
        if result[0] == '0':
            result = result.replace('$', '')
        else:
            result = RateHelp.USDtoRUB(numbers)
    elif result[-1] == '€':
        if result[0] == '0':
            result = result.replace('€', '')
        else:
            result = RateHelp.EURtoRUB(numbers)
    else:
        result = result[:-1]
    if result.__len__() > 0:
        try:
            result = float(result.replace(' ', ''))
        except:
            result = 0.00
    return result


def sendEmail(result_file):
    EmailHelper.sendAttachment(result_save_file, 'Tender_info_A')


def close_alert():
    try:
        close_buttons = driver.find_elements(By.CSS_SELECTOR, 'button.button-red.refresh-button')
        if close_buttons.__len__() > 0:
            close_buttons[0].click()
            time.sleep(60.0)
    except Exception as e:
        print('close_alert error')
        # print(e)


def adjust_excel():
    global result_save_file
    today = time.strftime('%Y-%m-%d', time.localtime())
    result_save_file = PathHelp.get_file_path('Tender', f'ros_tender_{today}.xlsx')
    if not os.path.exists(result_save_file):
        ExcelHelp.create_excel_file(result_save_file)
        title_arr = [
            ['grade', 'No', 'title_ru', 'starting_price', 'application_security', 'contract_security', 'status',
             'published',
             'apply_data', 'show_data', 'org_name', 'org_TinKpp', 'org_contact', 'cus_name', 'cus_TinKppReg',
             'cus_contact',
             'cus_address', 'detail_url', 'page']]
        ExcelHelp.add_arr_to_sheet(result_save_file, result_save_sheet, title_arr)


if __name__ == "__main__":
    driver.get(login_url)
    WaitHelp.waitfor_account_import(True, False)
    login_action()
    adjust_excel()
    time.sleep(2.0)
    driver.get(search_base_url)
    set_total_page()
    while True:
        now = datetime.datetime.now()
        h_value = now.hour
        if h_value > 1:
            time.sleep(60*50)
        else:
            break
    main()
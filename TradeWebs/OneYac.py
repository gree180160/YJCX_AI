# https://www.oneyac.com/brand/874.html
# https://www.oneyac.com/brand/875.html
# https://www.oneyac.com/brand/1062.html

import ssl
from WRTools import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp
import time

ssl._create_default_https_context = ssl._create_unverified_context

driver_option = webdriver.ChromeOptions()
driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(480)

default_url = 'https://www.oneyac.com/page/sqdl.html'


result_save_file = PathHelp.get_file_path('TradeWebs', 'OneYac.xlsx')
log_file = PathHelp.get_file_path('TradeWebs', 'log.txt')
current_page = 42
total_page = 0


# 获取当前页面的数据
def get_page_data(manu):
    print(f'total page {total_page} , current_page {current_page}')
    result = []
    table = driver.find_element(By.ID, 'list_tbody_list')
    product_models = table.find_elements(By.TAG_NAME, 'tr')
    for model in product_models:
        try:
            # ppn, manu, stock, date_line, minNum, addNum, packageNum, price_num, price
            ppn = model.find_elements(By.CSS_SELECTOR, 'a.listPro_code.preText')[0].text
            manu = manu

            stock_td = model.find_elements(By.CSS_SELECTOR, 'div.listPro_tdCon')[5]
            stock = stock_td.find_element(By.CSS_SELECTOR, 'span.text-warning.text-bold.fs-14').text.replace(",", '')
            date_line = stock_td.find_elements(By.TAG_NAME, 'p')[-1].text.replace("交期：", '')
            packageNum = stock_td.find_elements(By.TAG_NAME, 'p')[-2].text.replace("MPQ：", '')

            price_td = model.find_elements(By.CSS_SELECTOR, 'div.listPro_tdCon')[4]
            price_table = price_td.find_element(By.TAG_NAME, 'table')
            tr_price = price_table.find_elements(By.TAG_NAME, 'tr')[-1]
            price_num = tr_price.find_elements(By.TAG_NAME, 'td')[0].text.replace('：', '')
            price = tr_price.find_elements(By.TAG_NAME, 'td')[1].text.replace('¥', '')
            row = [ppn, manu, stock, date_line, packageNum, price_num, price]
        except Exception as e:
            print(f'get_page_data : {e}')
            row = []
        result.append(row)
    # 保存数据到excel
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'OneYac', result)


def go_to_kind(manu_index, manu):
    url = 'https://www.oneyac.com/brand/' + manu
    print(url)
    driver.get(url)
    WaitHelp.waitfor_account_import(True, False)
    exit_item()
    time.sleep(5.0)
    setTotal_page()
    manu_names = ['TDK', 'YAGEO', 'TE Connectivity']
    while current_page <= total_page:
        get_page_data(manu_names[manu_index])
        if current_page == total_page:
            break;
        else:
            go_nextPage()


def setTotal_page():
    global total_page
    try:
        total_page = int(driver.find_element(By.ID, 'list_totalPages').text)
    except:
        print('get total_page error')
        total_page = 0
        driver.get(default_url)
        time.sleep(10.0)


def go_nextPage():
    global current_page
    next_page_button = driver.find_element(By.ID, 'list_page_next')
    # # 获取按钮的位置
    # location = next_page_button.location
    # button_height = next_page_button.size['height']
    # # 计算需要滑动的距离，使按钮显示在浏览器窗口中心
    # window_height = driver.execute_script("return window.innerHeight")
    # scroll_distance = location['y'] - (window_height / 2) + (button_height / 2)
    # # 滚动页面
    # driver.execute_script(f"window.scrollTo(0, {scroll_distance});")
    # # 等待一段时间以查看效果
    time.sleep(5)
    next_page_button.click()
    WaitHelp.waitfor_account_import(True, False)
    current_page += 1


def main():
    manu_list = [
        # '874',
        # '875',
        '1062'
    ]
    for (manu_index, manu) in enumerate(manu_list):
        go_to_kind(manu_index, manu)


# 有货&有价格
def exit_item():
    fileter = driver.find_element(By.CSS_SELECTOR, 'div.listHd')
    exit = fileter.find_elements(By.TAG_NAME, 'label')[0]
    # # 获取按钮的位置
    # location = exit.location
    # button_height = exit.size['height']
    # # 计算需要滑动的距离，使按钮显示在浏览器窗口中心
    # window_height = driver.execute_script("return window.innerHeight")
    # scroll_distance = location['y'] - (window_height / 2) + (button_height / 2)
    # # 滚动页面
    # driver.execute_script(f"window.scrollTo(0, {scroll_distance});")
    # # 等待一段时间以查看效果
    # time.sleep(5)
    exit.click()
    time.sleep(5.0)
    price = fileter.find_elements(By.TAG_NAME, 'label')[1] # driver.find_element(By.ID, 'have-price-input')
    price.click()
    time.sleep(5.0)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(False, False)
    main()

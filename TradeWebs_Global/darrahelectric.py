# 世强硬创
import math
import ssl
from WRTools import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp
import time
import random

ssl._create_default_https_context = ssl._create_unverified_context


driver_option = webdriver.ChromeOptions()
driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(480)

default_url = 'https://www.darrahelectric.com/'


result_save_file = PathHelp.get_file_path('TradeWebs_Global', 'darrahelectric.xlsx')
log_file = PathHelp.get_file_path('TradeWebs_Global', 'log.txt')
current_page = 1
total_page = 0


# 获取当前页面的数据
def get_page_data(manu):
    result = []
    scroll_height = 5.0 + random.uniform(1, 10)
    driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_height)
    print(f'manu is: {manu} current page is :{current_page} total page is :{total_page}')
    product_list = driver.find_elements(By.CSS_SELECTOR, 'div.prod-item.columns')
    for temp_ppn in product_list:
        # ppn, manu, price, instock
        ppn = temp_ppn.find_element(By.CSS_SELECTOR, 'a.pi-heading').text
        try:
            price = temp_ppn.find_element(By.CSS_SELECTOR, 'span.pi-cur-price').text
        except:
            price = '--'
        try:
            instock_text = temp_ppn.find_element(By.CSS_SELECTOR, 'a.pi-cart.btn').text
            if instock_text == 'ADD TO CART':
                instock = '1'
            else:
                instock = '0'
        except:
            instock = '0'
        info = [ppn, manu, price, instock]
        result.append(info)
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'ppn', result)


def go_to_manu(manu):
    global current_page
    time.sleep(2.0)
    # eg:'https://www.darrahelectric.com/brands/mitsubishi-electric'
    new_url = f'https://www.darrahelectric.com/brands/{manu}'
    driver.get(new_url)
    # input = driver.find_element(By.ID, 'searchText')
    # input.clear()
    # input.send_keys(manu)
    # search_button = driver.find_element(By.ID, 'searchBtn')
    # search_button.click()
    WaitHelp.waitfor_account_import(True, False)
    setTotal_page()
    current_page = 1
    while current_page <= total_page:
        get_page_data(manu)
        if current_page == total_page:
            break;
        else:
            go_nextPage(manu)


def setTotal_page():
    global total_page
    try:
        total_page_str = driver.find_element(By.CSS_SELECTOR, 'li.page-total').text
        total_page = int(total_page_str.split(" ")[1])
    except Exception as e:
        print('get total_page error {e}')
        total_page = 1 # 只有一页，不显示页数
        driver.get(default_url)
        time.sleep(10.0)


def go_nextPage(manu):
    global current_page
    page_area = driver.find_element(By.CSS_SELECTOR, 'ul.paging')
    next_a = page_area.find_element(By.CSS_SELECTOR, 'li.next').find_element(By.TAG_NAME, 'a')
    next_a.click()
    WaitHelp.waitfor_account_import(True, False)
    current_page += 1


def main():
    manus = ['mitsubishi-electric', 'powerex', 'semikron'] # ['dynex', 'hitachi-energy', 'ixys-westcode', 'lem', 'mitsubishi-electric', 'powerex', 'semikron']
    for temp_manu in manus:
        go_to_manu(temp_manu)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor(True, False)
    main()

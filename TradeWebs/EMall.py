import ssl
import math
from WRTools import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, LogHelper, PathHelp, WaitHelp
import time

ssl._create_default_https_context = ssl._create_unverified_context

driver_option = webdriver.ChromeOptions()
driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(480)

default_url = 'https://www.e-mall.com/product_list/spot'


result_save_file = PathHelp.get_file_path('TradeWebs', 'EMall.xlsx')
log_file = PathHelp.get_file_path('TradeWebs', 'log.txt')
current_page = 1
total_page = 0


# 获取当前页面的数据
def get_page_data():
    print(f'total page {total_page} , current_page {current_page}')
    result = []
    product_models = driver.find_elements(By.CSS_SELECTOR, 'tr.ant-table-row.ant-table-row-level-0')
    for model in product_models:
        try:
            # ppn, manu, stock, date_line, minNum, addNum, packageNum, price_num, price
            ppn = model.find_element(By.CSS_SELECTOR, 'span.standard_item___3pEsP').text
            manu = model.find_element(By.CSS_SELECTOR, 'span.value___SNh4r').text
            stock = model.find_elements(By.CSS_SELECTOR, 'span.stock_value___18suI')[0].text
            date_line = model.find_elements(By.CSS_SELECTOR, 'span.stock_value___18suI')[1].text
            minNum = model.find_elements(By.CSS_SELECTOR, 'span.stock_value___18suI')[2].text
            addNum = model.find_elements(By.CSS_SELECTOR, 'span.stock_value___18suI')[3].text
            packageNum = model.find_elements(By.CSS_SELECTOR, 'span.stock_value___18suI')[4].text
            price_area = model.find_elements(By.CSS_SELECTOR, 'div.price-row___hRnLs')[-1]
            price_num = price_area.find_elements(By.TAG_NAME, 'span')[0].text
            price = price_area.find_elements(By.TAG_NAME, 'span')[-1].text
            row = [ppn, manu, stock, date_line, minNum, addNum, packageNum, price_num, price]
        except Exception as e:
            row = []
        result.append(row)
    # 保存数据到excel
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'molex', result)


def go_to_manu():
    print('please select manu')
    WaitHelp.waitfor_account_import(True, False)
    setTotal_page()
    while current_page <= total_page:
        get_page_data()
        if current_page == total_page:
            break;
        else:
            go_nextPage()


def setTotal_page():
    global total_page
    try:
        total_page = int(driver.find_elements(By.CSS_SELECTOR, 'li.ant-pagination-item')[-1].text)
    except:
        print('get total_page error')
        total_page = 0
        driver.get(default_url)
        time.sleep(10.0)


def go_nextPage():
    global current_page
    # 滚动到页面底部
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # 让我们暂停一下，以便查看效果
    time.sleep(5.0)
    next_page_button = driver.find_elements(By.CSS_SELECTOR, 'button.ant-pagination-item-link')[-1]
    next_page_button.click()
    WaitHelp.waitfor_account_import(True, False)
    current_page += 1


def main():
    go_to_manu()


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(False, False)
    main()

import ssl
import math
from WRTools import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, LogHelper, PathHelp, WaitHelp
from selenium.webdriver.common.action_chains import ActionChains
import time

ssl._create_default_https_context = ssl._create_unverified_context

driver_option = webdriver.ChromeOptions()
driver = ChromeDriverManager.getWebDriver(0)
driver.set_page_load_timeout(480)

default_url = 'https://www.verical.com/'


result_save_file = PathHelp.get_file_path(None, 'THolt2411.xlsx')
log_file = PathHelp.get_file_path('Holt', 'log.txt')
current_page = 1
total_page = 0


# 获取当前页面的数据
def get_page_data():
    result = []
    print(f'total page is: {total_page}, current_page is : {current_page}')
    product_models = driver.find_elements(By.CSS_SELECTOR, 'div.search-results__products_item')
    for model in product_models:
        try:
            # ppn, manu, stock, des
            ppn_info = model.find_element(By.CSS_SELECTOR, 'div.search-results__products_item_description')
            ppn = ppn_info.find_element(By.CSS_SELECTOR, 'div.search-results__products_item_description-mpn').text
            manu = ppn_info.find_element(By.CSS_SELECTOR, 'div.search-results__products_item_description-manufacturer').text
            des = ppn_info.find_element(By.CSS_SELECTOR, 'div.search-results__products_item_description-info').text
            stock = ppn_info.find_element(By.CSS_SELECTOR, 'div.search-results__products_item_description-available').text.replace('Available: ', '')
            result.append([ppn, manu, des, stock])
        except Exception as e:
            print(f"without ppn")
    # 保存数据到CSV
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'verical', result)


def go_to_manu():
    time.sleep(2.0)
    input = driver.find_element(By.ID, 'mat-input-2')
    input.clear()
    input.send_keys('Holt Integrated Circuits')
    time.sleep(5.0)

    time.sleep(20.0)

    # manu = '1177'
    # driver.get(f'https://www.verical.com/s/HOLT/{current_page}?mfr={manu}')
    # WaitHelp.waitfor(True, False)
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
        page_str = driver.find_element(By.CSS_SELECTOR, 'div.pagination__page-count').text
        total_page = int(page_str.split(' ')[0])
    except:
        print('get total_page error')
        total_page = 6 # //TODO wr
        # driver.get(default_url)
        time.sleep(10.0)


def go_nextPage():
    global current_page
    actions = ActionChains(driver)
    next_button = driver.find_element(By.CSS_SELECTOR, 'a.icon-arrow-right-fill')
    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
    actions.move_to_element(next_button).click().perform()
    WaitHelp.waitfor(True, False)
    current_page += 1


def main():
    go_to_manu()


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor(True, False)
    main()

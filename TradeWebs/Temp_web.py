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

default_url = 'https://www.te.com.cn/chn-zh/home.html'


result_save_file = PathHelp.get_file_path('TradeWebs', 'TESignalRelay.xlsx')
log_file = PathHelp.get_file_path('TESignalRelay.xlsx', 'log.txt')
current_page = 1
total_page = 0


# 获取当前页面的数据
def get_page_data():
    result = []
    print(f'total page is: {total_page}, current_page is : {current_page}')
    product_models = driver.find_elements(By.CSS_SELECTOR, 'tr.mat-row.cdk-row')
    for model in product_models:
        try:
            # ppn, manu, stock, date_line, minnum, factory_date, minpakage, batch, price_num, price
            ppn_info = model.find_elements(By.TAG_NAME, 'td')[1]
            ppn = ppn_info.find_element(By.CSS_SELECTOR, 'a.oplp-url-right-grid').text
            try:
                internal = ppn_info.find_element(By.CSS_SELECTOR, 'span.internal-number.product-values').text
            except:
                internal = ''
                print(f"without interal ppn")
            result.append([ppn, 'TE', internal])
        except Exception as e:
            print(f"without ppn")
    # 保存数据到CSV
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'TESignalRelay', result)


def go_to_manu():
    time.sleep(2.0)
    driver.get('https://www.te.com.cn/chn-zh/search.html?q=%E4%BF%A1%E5%8F%B7%E7%BB%A7%E7%94%B5%E5%99%A8&type=products&inStoreWithoutPL=false&q2=')
    WaitHelp.waitfor(True, False)
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
        page_area = driver.find_element(By.CSS_SELECTOR, 'div.pagination')
        total_page = int(page_area.find_elements(By.CSS_SELECTOR, 'li')[-1].text)
    except:
        print('get total_page error')
        total_page = 0
        driver.get(default_url)
        time.sleep(10.0)


def go_nextPage():
    global current_page
    new_url = f'https://www.te.com.cn/chn-zh/search.html?q=%E4%BF%A1%E5%8F%B7%E7%BB%A7%E7%94%B5%E5%99%A8&type=products&p={current_page+1}&inStoreWithoutPL=false&q2='
    driver.get(new_url)
    WaitHelp.waitfor(True, False)
    current_page += 1


def main():
    go_to_manu()


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(False, False)
    main()

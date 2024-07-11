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

default_url = 'https://list.szlcsc.com/zk2201126.html'

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TManuAndSeri_144H.xlsx'),
                  'sourceSheet': 'manu',
                  'colIndex': 1,
                  'startIndex': 26,
                  'endIndex': 29}
result_save_file = PathHelp.get_file_path(None, 'TManuAndSeri_144H.xlsx')
log_file = PathHelp.get_file_path('LiChuang', 'lichuangLog.txt')
current_page = 1
total_page = 0


# 获取当前页面的数据
def get_page_data(manu):
    result = []
    product_models = driver.find_elements(By.CSS_SELECTOR, 'table.inside.inside-page.tab-data.list-items')
    for model in product_models:
        try:
            model_name = model.find_element(By.CSS_SELECTOR, 'a.ellipsis.product-name-link.goto-item-detail.item-go-detail').text
            manufacturer = model.find_element(By.CSS_SELECTOR, 'a.brand-name').text
            discount = model.find_element(By.CSS_SELECTOR, 'li.three-nr-01').find_element(By.TAG_NAME, 'span').text
            discount = discount.replace(' 折起', '')
            discount = discount.replace(' 折', '')
            price_li = model.find_elements(By.CSS_SELECTOR, 'li.three-nr-item')[-1]
            minOrderNum = price_li.find_element(By.TAG_NAME, 'span').get_attribute('minordernum')
            price = price_li.find_element(By.TAG_NAME, 'span').text
            stock_js = model.find_element(By.CSS_SELECTOR, 'div.stock-nums-js').find_element(By.TAG_NAME, 'span').text
            stock_gd = model.find_element(By.CSS_SELECTOR, 'div.stock-nums-gd').find_element(By.TAG_NAME, 'span').text
            stock = int(stock_js) + int(stock_gd)
            result.append([model_name, manufacturer, discount, stock, minOrderNum, price, manu, current_page])
        except Exception as e:
            print(f"Error processing element: {e}")
    # 保存数据到CSV
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'lcRecord', result)


def go_to_manu(manu):
    global current_page
    current_page = 1
    input_area = driver.find_element(By.ID, 'localQueryKeyword')
    input_area.clear()
    input_area.send_keys(manu)
    time.sleep(2.0)
    try:
        search_button = driver.find_element(By.ID, 'searchInResults')
        search_button.click()
    except:
        print('click search button error?')
    time.sleep(2.0)
    WaitHelp.waitfor_account_import(True, False)
    setTotal_page()
    while current_page <= total_page:
        get_page_data(manu)
        if current_page == total_page:
            break;
        else:
            go_nextPage()


def setTotal_page():
    global total_page
    try:
        count_str = driver.find_element(By.CSS_SELECTOR, 'div.g01').find_elements(By.TAG_NAME, 'span')[1].text
        total_page = math.ceil(int(count_str) / 20)
    except:
        print('get total_page error')
        total_page = 0
        driver.get(default_url)
        time.sleep(10.0)


def go_nextPage():
    global current_page
    # input_area = driver.find_element(By.CSS_SELECTOR, 'input.page-input')
    # input_area.clear()
    # input_area.send_keys(str(current_page+1))
    # button = driver.find_element(By.CSS_SELECTOR, 'input.confirm-page')
    ul = driver.find_element(By.CSS_SELECTOR, 'ul.page-left')
    next_page_button = ul.find_elements(By.TAG_NAME, 'li')[-1].find_element(By.TAG_NAME, 'a')
    next_page_button.click()
    WaitHelp.waitfor_account_import(True, False)
    current_page += 1


def main():
    all_manus = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=1)
    for (manu_index, manu) in enumerate(all_manus):
        while WaitHelp.isSleep_time():
                time.sleep(60*5)
        if manu is None or manu.__contains__('?'):
            continue
        elif manu_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'manu_index is: {manu_index}  pn is: {manu}')
            go_to_manu(manu)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(False, False)
    main()

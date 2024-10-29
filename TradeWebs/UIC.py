# 硬之城
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

default_url = 'https://www.uicmall.com//'


result_save_file = PathHelp.get_file_path('TradeWebs', 'UIC.xlsx')
log_file = PathHelp.get_file_path('TradeWebs', 'log.txt')
current_page = 1
total_page = 0


# 获取当前页面的数据
def get_page_data(manu_id):
    result = []
    print(f'manu_id is: {manu_id} current page is :{current_page} total page is :{total_page}')
    product_models = driver.find_element(By.ID, 'search_result').find_elements(By.TAG_NAME, 'tr')
    for model in product_models:
        ppnInfo = []
        try:
            product_info = model.find_element(By.CSS_SELECTOR, 'td.product_info')

            ppn = product_info.find_elements(By.TAG_NAME, 'p')[1].find_element(By.TAG_NAME, 'a').text
            manu = product_info.find_elements(By.TAG_NAME, 'p')[3].find_element(By.TAG_NAME, 'a').text
            des = product_info.find_elements(By.TAG_NAME, 'p')[2].find_element(By.TAG_NAME, 'a').text

            stock = model.find_elements(By.TAG_NAME, 'td')[3].find_element(By.TAG_NAME, 'p').text

            mpq_str = model.find_elements(By.TAG_NAME, 'td')[4].find_elements(By.TAG_NAME, 'p')[1].text
            mpq = mpq_str.split('=')[1].replace('个', '').replace(')', '')
            moq = model.find_elements(By.TAG_NAME, 'td')[4].find_element(By.CSS_SELECTOR, 'input.num_t').get_attribute("value")

            price_info = model.find_elements(By.TAG_NAME, 'td')[2].find_elements(By.TAG_NAME, 'dl')
            price_str = ''
            for price_item in price_info:
                dt = price_item.find_element(By.TAG_NAME, 'dt').text.replace('+', '')
                dd = price_item.find_element(By.TAG_NAME, 'dd').text.replace('￥', '')
                item_price = f'[{dt} : {dd}] '
                price_str += item_price
            ppnInfo = [ppn, manu, des, mpq, moq, stock, price_str, '1天']
        except Exception as e:
            print('get_page_data error : {e}')
        result.append(ppnInfo)
    # 保存数据到CSV
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'UIC', result)


def go_to_manu(manuID):
    global current_page
    time.sleep(2.0)
    new_url = f'https://www.uicmall.com/brand/{manuID}'
    driver.get(new_url)
    WaitHelp.waitfor_account_import(True, False)
    setTotal_page()
    current_page = 1
    while current_page <= total_page:
        get_page_data(manuID)
        if current_page == total_page:
            break;
        else:
            go_nextPage(manuID)


def setTotal_page():
    global total_page
    try:
        pages_area = driver.find_element(By.ID, 'page')
        pages_str = pages_area.find_elements(By.TAG_NAME, 'strong')[1].text
        total_page = int(pages_str.split('/')[1])
    except:
        print('get total_page error')
        total_page = 1 # 只有一页，不显示页数
        driver.get(default_url)
        time.sleep(10.0)


def go_nextPage(manu_id):
    global current_page
    next_btton = driver.find_element(By.ID, 'page').find_elements(By.TAG_NAME, 'a')[-1]
    next_btton.click()
    WaitHelp.waitfor_account_import(True, False)
    current_page += 1


def main():
    # https://www.uicmall.com/brand/10
    manus = [29] # 7,
    for temp_id in manus:
        go_to_manu(temp_id)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(False, False)
    main()

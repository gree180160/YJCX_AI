# 芯城电子商城
import ssl
from WRTools import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, LogHelper, PathHelp, WaitHelp
import time

ssl._create_default_https_context = ssl._create_unverified_context


driver_option = webdriver.ChromeOptions()
driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(480)

default_url = 'https://icshops.cn/consignment/1.html'  #'https://icshops.cn/support/'


result_save_file = PathHelp.get_file_path('TradeWebs', 'ICShop.xlsx')
log_file = PathHelp.get_file_path('TradeWebs', 'log.txt')
current_page = 1
total_page = 0


# 获取当前页面的数据
def get_page_data():
    result = []
    print(f'current page is :{current_page} total page is :{total_page}')
    product_models = driver.find_element(By.CSS_SELECTOR, 'div.list_mainbox').find_elements(By.TAG_NAME, 'form')
    for model in product_models:
        ppnInfo = []
        try:
            # ppn, manu,des, stock, date_line, moq, mpq, maq, batch, price
            dl_array = model.find_elements(By.TAG_NAME, 'dl')
            ppn = dl_array[1].find_element(By.TAG_NAME, 'dd').text
            manu = dl_array[2].find_element(By.TAG_NAME, 'dd').text
            des = dl_array[3].find_element(By.TAG_NAME, 'dd').text
            mpq = dl_array[5].find_elements(By.TAG_NAME, 'dd')[0].text.replace('最小包: ', '')
            moq = dl_array[5].find_elements(By.TAG_NAME, 'dd')[1].text.replace('起订量: ', '')
            maq = dl_array[5].find_elements(By.TAG_NAME, 'dd')[2].text.replace('递增量: ', '')
            stock = dl_array[6].find_element(By.TAG_NAME, 'dd').text
            price = dl_array[7].find_element(By.TAG_NAME, 'dd').text.split('\n')[-1].replace('￥','')
            date_line = dl_array[8].find_element(By.TAG_NAME, 'dd').text
            ppnInfo = [ppn, manu, des, mpq, moq, maq, stock, price, date_line]
        except Exception as e:
            print('get_page_data error : {e}')
        result.append(ppnInfo)
    # 保存数据到CSV
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'ICShops_consignment2', result)


def go_to_manu():
    time.sleep(2.0)
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
        pages_area = driver.find_element(By.CSS_SELECTOR, 'div.pages')
        pages_str = pages_area.find_element(By.TAG_NAME, 'cite').text
        total_page = int(pages_str.split('/')[1].replace('页', ''))
    except:
        print('get total_page error')
        total_page = 0
        driver.get(default_url)
        time.sleep(10.0)


def go_nextPage():
    global current_page
    # pages_area = driver.find_element(By.CSS_SELECTOR, 'div.pages')
    # next_page_button = pages_area.find_elements(By.TAG_NAME, 'a')[2]
    # next_page_button.click()
    new_url = f'https://icshops.cn/consignment/{current_page + 1}.html'
    driver.get(new_url)
    WaitHelp.waitfor_account_import(True, False)
    current_page += 1


def main():
    go_to_manu()


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(False, False)
    main()

import math
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

default_url = 'https://www.sekorm.com/supply/?utm_source=Channel&utm_medium=yingchuangshangcheng&utm_campaign=&p1=1&p3=16&p4=3&p5=1&p6=30&p8=1&p9=4'


result_save_file = PathHelp.get_file_path('TradeWebs', 'Sekorm.xlsx')
log_file = PathHelp.get_file_path('TradeWebs', 'log.txt')
current_page = 1
total_page = 0


# 获取当前页面的数据
def get_page_data(manu):
    result = []
    print(f'manu is: {manu} current page is :{current_page} total page is :{total_page}')
    product_models = driver.find_element(By.CSS_SELECTOR, 'table.sk-fs12').find_elements(By.TAG_NAME, 'tr')[2:]
    for model in product_models:
        tds = model.find_elements(By.TAG_NAME, 'td')
        if tds.__len__() > 1:
            ppnInfo = []
            try:
                # ppn, manu,des, stock, date_line, moq, mpq, maq, batch, price
                ppn = model.find_element(By.CSS_SELECTOR, 'a.model-on').text
                manu = model.find_element(By.CSS_SELECTOR, 'a.model-brand').text
                des = model.find_element(By.CSS_SELECTOR, 'p.desc-category').text
                stock = model.find_element(By.CSS_SELECTOR, 'span.information-content.pcs.inStock').text
                mpq = model.find_element(By.CSS_SELECTOR, 'p.min-pack-amount').text
                single_price_str = model.find_element(By.CSS_SELECTOR, 'span.single-price').text
                if single_price_str.__len__() > 0:
                    price_str = single_price_str.replace('\n', '')
                else:
                    price_info = model.find_elements(By.CSS_SELECTOR, 'span.ladderPrice-item')
                    price_str = ''
                    for price_item in price_info:
                        price_str += (price_item.text + '\n')
                date_line = model.find_element(By.CSS_SELECTOR, 'span.information-content.delivery-content').text
                ppnInfo = [ppn, manu, des, mpq, stock, price_str, date_line]
            except Exception as e:
                print('get_page_data error : {e}')
            result.append(ppnInfo)
    # 保存数据到CSV
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'Sekorm', result)


def go_to_manu(manu):
    global current_page
    time.sleep(2.0)
    # urls = ['https://www.sekorm.com/Web/Search/channel?tab=4&shelfId=3&searchWord=Renesas&ugc=k',
    #         'https://www.sekorm.com/Web/Search/channel?tab=4&shelfId=3&searchWord=AMPHENOL%20SENSORS&ugc=k',
    #         'https://www.sekorm.com/Web/Search/channel?tab=4&shelfId=3&searchWord=TE%20Connectivity&ugc=k',
    #         'https://www.sekorm.com/Web/Search/channel?tab=4&shelfId=3&searchWord=LITTELFUSE&ugc=k']
    input = driver.find_element(By.ID, 'searchText')
    input.clear()
    input.send_keys(manu)
    search_button = driver.find_element(By.ID, 'searchBtn')
    search_button.click()
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
        pages_area = driver.find_element(By.CSS_SELECTOR, 'div.search-result-title')
        pages_str = pages_area.find_elements(By.TAG_NAME, 'span')[-1].text
        total_page = math.ceil(int(pages_str)/50)
    except Exception as e:
        print('get total_page error {e}')
        total_page = 1 # 只有一页，不显示页数
        driver.get(default_url)
        time.sleep(10.0)


def go_nextPage(manu):
    global current_page
    next_a = driver.find_element(By.CSS_SELECTOR, 'div.page-block.page-next').find_element(By.TAG_NAME, 'a')
    next_a.click()
    WaitHelp.waitfor_account_import(True, False)
    current_page += 1


def main():
    # 'https://www.sekorm.com/supply/?utm_source=Channel&utm_medium=yingchuangshangcheng&utm_campaign=&p1=1&p3=16&p4=3&p5=1&p6=30&p8=1&p9=4'
    manus = ['Renesas', 'AMPHENOL%20SENSORS', 'TE%20Connectivity', 'LITTELFUSE']
    for temp_manu in manus:
        go_to_manu(temp_manu)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(False, False)
    main()

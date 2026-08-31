# es electronic source
import ssl
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp, ChromeDriverManager
import re
import time
from selenium.webdriver.support import expected_conditions as EC
import traceback
from selenium.webdriver.support.ui import WebDriverWait


ssl._create_default_https_context = ssl._create_unverified_context
try:
    driver = ChromeDriverManager.getWebDriver(0)
except Exception as e:
    print(e)

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TEVG.xlsx'),
                  'sourceSheet': 'cate',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 8}
task_name = 'TEVG.xlsx'
home_url = 'https://www.galco.com/'
cate_url = 'https://www.galco.com/manufacturer'


current_page = 1
total_page = 1


# 获取当前页面的数据
def get_page_data(url, index):
    # [model, manufacturer, stock, price1, price2]
    table_container = driver.find_element(By.CSS_SELECTOR, 'div.dataitems_container')
    product_list = table_container.find_elements(By.CSS_SELECTOR, 'div.tabs-right-block')
    page_data = []
    for product in product_list:
        model = manufacturer = stock = price1 = price2 = ''
        try:
            model = product.find_element(By.CSS_SELECTOR, 'div.dt_mfrpn').text
            manufacturer = product.find_element(By.CSS_SELECTOR, 'div.dt_mfrpnname').text
            stock = product.find_element(By.CSS_SELECTOR, 'div.stockamount').text
            price_infos = product.find_elements(By.CSS_SELECTOR, 'div.pricelv')
            if price_infos.__len__() > 0:
                price_info = price_infos[0]
                price1 = price_info.find_elements(By.CSS_SELECTOR, 'div.qty_lv')[0].text + ">" + \
                         price_info.find_elements(By.CSS_SELECTOR, 'div.price_lv')[0].text
                price_list = price_info.find_elements(By.TAG_NAME, 'div')
                if len(price_list) > 6:
                    price2 = price_info.find_elements(By.CSS_SELECTOR, 'div.qty_lv')[-1].text + ">" + \
                             price_info.find_elements(By.CSS_SELECTOR, 'div.price_lv')[-1].text
            else:
                pirce_infos = product.find_elements(By.CSS_SELECTOR, 'div.discountprice')
                if pirce_infos.__len__() > 0:
                    price_info = pirce_infos[0]
                    price1 = price_info.find_element(By.CSS_SELECTOR, 'div.dcp_data.dcp_savedata').text
                    price2 = price_info.find_element(By.CSS_SELECTOR, 'div.dcp_data.dcp_netpricedata').text
            item = [model, manufacturer, stock, price1, price2, index, current_page]
            page_data.append(item)
        except Exception as e:
            print(e)
    ExcelHelp.add_arr_to_sheet(sourceFile_dic['fileName'], 'result', page_data)
    time.sleep(3.0)


def go_to_manu(url, index):
    global current_page, total_page
    if index == 4:
        current_page = 2
        total_page = 20
    else:
        current_page = 1
        total_page = 1
    while current_page <= total_page:
        # https://www.es.co.th/tabs.asp?catc=040&t=1&p=4&keyword=&mfrc=
        new_url = f"{url}&isspecialpage=&maxcatclv=N&instock=y&p={current_page}"
        driver.get(new_url)
        WaitHelp.waitfor(True, False)
        get_page_data(url, index)
        if current_page == 1:
            set_total_page()
        current_page += 1


def set_total_page():
    global total_page
    try:
        # 方式1：直接滑动到页面底部（最常用）
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(20.0)
        total_page_str = driver.find_element(By.CSS_SELECTOR, 'div.PaginatorBottomByTab').find_element(By.TAG_NAME, 'div').text
        # Page 9 of 16
        print(f"total page string is: {total_page_str}")
        total_page = int(total_page_str.split(" of ")[-1])
    except Exception as e:
        total_page = 1
    print(f"total page is: {total_page}")


def get_cate_urls():
    driver.get(cate_url)
    WaitHelp.waitfor(True, False)
    result = []
    manu_container = driver.find_element(By.CSS_SELECTOR, 'section.ambrands-letters-list')
    table1 = manu_container.find_elements(By.TAG_NAME, 'ul')[0]
    links = table1.find_elements(By.TAG_NAME, 'a')
    for link in links:
        href = link.get_attribute('href')
        title = link.text
        if href.startswith('https://www.galco.com/'):
            result.append([href, title])
    ExcelHelp.add_arr_to_sheet(sourceFile_dic['fileName'], 'cate_link', result)


def main():
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                          sourceFile_dic['colIndex'])
    for (index, url) in enumerate(all_manu):
        while WaitHelp.isSleep_time():
            time.sleep(60 * 5)
        if index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'index: {index}, url is: {url}')
            go_to_manu(url, index)
    # get_cate_urls()


if __name__ == "__main__":
    # driver.get(home_url)
    # WaitHelp.waitfor(True, False)
    # main()
    get_cate_urls()
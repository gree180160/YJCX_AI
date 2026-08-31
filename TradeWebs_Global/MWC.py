# es electronic source
import ssl
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp, ChromeDriverManager
import re
import time


ssl._create_default_https_context = ssl._create_unverified_context
try:
    driver = ChromeDriverManager.getWebDriver(0)
except Exception as e:
    print(e)

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TMWC.xlsx'),
                  'sourceSheet': 'cate_link',
                  'colIndex': 1,
                  'startIndex': 23,
                  'endIndex': 26}
task_name = 'TMWC.xlsx'
home_url = 'https://mwc-llc.com/'
cate_url = 'https://mwc-llc.com/'


start = 0


# 获取当前页面的数据
def get_page_data(url, index):
    # [model, manufacturer, stock]
    table = driver.find_element(By.ID, 'productsList')
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    product_list = tbody.find_elements(By.TAG_NAME, 'tr')
    page_data = []
    for product in product_list:
        try:
            info = product.find_element(By.CSS_SELECTOR, 'td.product-sku')
            model = info.find_element(By.TAG_NAME, 'a').text
            manufacturer = info.text.replace(model, '')
            stock = product.find_element(By.CSS_SELECTOR, 'td.quantity-available').text
            int_stock = int(stock)
            if not stock == '-' and int_stock > 5:
                page_data.append([model, manufacturer, stock])
        except Exception as e:
            print(e)
    return page_data


def go_to_manu(url, index):
    global start
    driver.get(url)
    WaitHelp.waitfor(True, False)
    try:
        page_container = driver.find_element(By.CSS_SELECTOR, 'ul.pagination')
        end = page_container.find_elements(By.CSS_SELECTOR, 'a.page-link')[-1]
    except Exception as e:
        print("get page error: {e}")
        return
    page_data = get_page_data(url, index)
    while end.text == 'End':  # 最后一页
        page_data = get_page_data(url, index)
        if page_data.__len__() == 0:
            break
        else:
            ExcelHelp.add_arr_to_sheet(sourceFile_dic['fileName'], 'TMWC', page_data)
            start += 25
            new_url = url + f'?start={start}'
            print(new_url)
            driver.get(new_url)
            WaitHelp.waitfor(True, False)
            page_container = driver.find_element(By.CSS_SELECTOR, 'ul.pagination')
            end = page_container.find_elements(By.CSS_SELECTOR, 'a.page-link')[-1]


# step 1: get all manufacturers' urls
def get_cate_urls():
    driver.get(cate_url)
    WaitHelp.waitfor(True, False)
    result = []
    cate_container = driver.find_elements(By.CSS_SELECTOR, 'div.custom')[3]
    table1 = cate_container.find_elements(By.CSS_SELECTOR, 'table')[0]
    links = table1.find_elements(By.TAG_NAME, 'a')
    for link in links:
        href = link.get_attribute('href')
        if href.startswith('https://mwc-llc.com/'):
            result.append(href)
    table2 = cate_container.find_elements(By.CSS_SELECTOR, 'table')[1]
    links = table2.find_elements(By.TAG_NAME, 'a')
    for link in links:
        href = link.get_attribute('href')
        if href.startswith('https://mwc-llc.com/'):
            result.append(href)
    ExcelHelp.add_arr_to_col(sourceFile_dic['fileName'], 'cate_link', result)


def main():
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                          sourceFile_dic['colIndex'])
    for (index, url) in enumerate(all_manu):
        while WaitHelp.isSleep_time():
            time.sleep(60 * 5)
        if index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'index: {index}, url is: {url}')
            go_to_manu(url, index)


if __name__ == "__main__":
    driver.get(home_url)
    WaitHelp.waitfor(True, False)
    main()
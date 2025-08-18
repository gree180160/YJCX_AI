
import re
import ssl
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp, MySqlHelp_recommanded
import time
import random

ssl._create_default_https_context = ssl._create_unverified_context
driver = uc.Chrome(headless=False)  # 非无头模式更不容易被检测

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TRenesasIsolators.xlsx'),
                  'sourceSheet': 'ppn2',
                  'colIndex': 1,
                  'startIndex': 11,
                  'endIndex': 14}
task_name = 'TRenesasIsolators'

default_url = 'https://www.arrow.com/zh-cn'


# 获取当前页面的数据, 情况1：结果列表， 情况2：详情 ，情况3：
def get_page_data(ppn, manu):
    result = [ppn, manu, '', '', '', '',  '', '', task_name]
    # 列表： https://www.arrow.com/zh-cn/products/search?q=IGCM06F60GA&r=true
    # 详情： https://www.arrow.com/zh-cn/products/igcm06f60gaxkma1/infineon-technologies-ag
    if driver.current_url.__contains__('products'):
        try:
            first_ppn_a = driver.find_element(By.ID, 'item1').find_element(By.TAG_NAME, 'td').find_element(By.CSS_SELECTOR,
                                                                                                           'a.SearchResults-productLink')
            first_ppn = first_ppn_a.find_element(By.TAG_NAME, 'span').text
            if True or first_ppn.__contains__(ppn) or ppn.__contains__(first_ppn):
                first_ppn_a.click()  # 点击进入详情
                WaitHelp.waitfor(True, False)
        except:
            print(f'{ppn} get info error')
    noresult = driver.find_elements(By.CSS_SELECTOR, 'div.no-match')
    if noresult.__len__() == 0:
        # st_part, st_manu, a_ppn, a_manu, stock, leadTime, price, batch, task_name
        try:
            sum = driver.find_element(By.CSS_SELECTOR, 'h1.Product-Summary-Name')
            a_ppn = sum.find_elements(By.TAG_NAME, 'span')[0].text
            a_manu = sum.find_elements(By.TAG_NAME, 'span')[1].text
            ul = driver.find_element(By.ID, 'ariaContainer0')
            try:
                leftColumn = ul.find_elements(By.TAG_NAME, 'div')[0]
                batch = leftColumn.find_elements(By.TAG_NAME, 'dd')[1].text
                leadTime = leftColumn.find_elements(By.TAG_NAME, 'dd')[2].text
            except:
                batch = leadTime = ''
            try:
                buy_options = ul.find_element('div.BuyingOptions-content.ng-star-inserted')
                title = buy_options.find_element(By.CSS_SELECTOR, 'h2.BuyingOptions-title.ng-star-inserted').text
                if title.__len__() > 0:
                    stock = re.search(r'\d+', title).group()  # 提取第一个连续数字
                else:
                    stock = ''
                price = buy_options.find_element(By.CSS_SELECTOR, 'span.BuyingOptions-total-price.ng-star-inserted').text
                # rightColumn = ul.find_elements(By.TAG_NAME, 'div')[1]
                # stock = rightColumn.find_element(By.CSS_SELECTOR, 'li.ng-star-inserted').find_element(By.TAG_NAME,
                #                                                                                       'strong').text
                # price = driver.find_element(By.CSS_SELECTOR, 'span.BuyingOptions-total-price.ng-star-inserted').text
            except:
                stock = price = ''
            result = [ppn, manu, a_ppn, a_manu, stock, leadTime, price, batch, task_name]
        except Exception as e:
            print(f'get element error {e}')
    else:
        print('no result')
    MySqlHelp_recommanded.DBRecommandChip().arrow_info_write([result])


def go_to_ppn(ppn, manu):
    inputs = driver.find_elements(By.ID, 'pdp-search-box')
    if inputs.__len__() == 0:
        input = driver.find_element(By.CSS_SELECTOR, 'input.js-search-input.Search-bar-select-input')
    else:
        input = inputs [0]
    input.clear()
    input.send_keys(ppn)
    time.sleep(5.0)
    searchBtn = driver.find_element(By.CSS_SELECTOR, 'button.Embedded-search-button')
    searchBtn.click()
    WaitHelp.waitfor(True, False)
    get_page_data(ppn, manu)


def main():
    all_cates = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'], 2)
    for (index, ppn) in enumerate(all_cates):
        if ppn.__contains__('?'):
            continue
        elif index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {index}  cate_name is: {ppn}')
            manu = all_manu[index]
            go_to_ppn(ppn, manu)


if __name__ == "__main__":
    driver.get(default_url)
    time.sleep(60)
    scroll_height = 125.0 + random.uniform(1, 30)
    driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_height)
    time.sleep(5.0)
    driver.get('https://www.arrow.com/zh-cn/categories/sensors')
    time.sleep(50.0)
    main()

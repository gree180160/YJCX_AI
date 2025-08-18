# renesas , infenion,
# STM32F407VET6TR,
default_url = 'https://www.futureelectronics.com/'


# 易洛蒙
import ssl
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp, MySqlHelp_recommanded
import time
import undetected_chromedriver as uc

ssl._create_default_https_context = ssl._create_unverified_context
driver_option = webdriver.ChromeOptions()
driver = uc.Chrome(use_subprocess=True, options=driver_option)
driver.set_page_load_timeout(480)

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TRenesasIsolators.xlsx'),
                  'sourceSheet': 'ppn2',
                  'colIndex': 1,
                  'startIndex': 2,
                  'endIndex': 14}
task_name = 'TRenesasIsolators'


# 获取当前页面的数据
def get_page_data(ppn, manu):
    result = [ppn, manu, '', '', '', '',  '', '', task_name]
    noresult = driver.find_elements(By.CSS_SELECTOR, 'div.no-match')
    if noresult.__len__() == 0:
        # st_part, st_manu, f_ppn, f_manu, OnOrder, stock, leadTime, unitPrice, taskName
        # 列表
        code_list = driver.find_elements(By.CSS_SELECTOR, 'a.product__list--code')
        if code_list.__len__() > 0:
            for temp in code_list:
                if temp.text.__contains__(ppn) or ppn.__contains__(temp.text):
                    try:
                        temp.click() # 进入详情
                    except Exception as e:
                        print(f'click detail error {e}')
                    WaitHelp.waitfor(True, False)
                    break
        try:
            left = driver.find_element(By.ID, 'product-section-dt')
            f_ppn = left.find_element(By.CSS_SELECTOR, 'span.product-title-id').text
            table = left.find_element(By.TAG_NAME, 'table')
            f_manu = table.find_elements(By.TAG_NAME, 'tr')[2].find_elements(By.TAG_NAME, 'td')[-1].text

            right = driver.find_element(By.ID, 'pricing-section-tb')
            OnOrder = right.find_element(By.CSS_SELECTOR, 'div.fe-col-12.on-order').find_element(By.CSS_SELECTOR,
                                                                                                 'div.fe-col-4').text
            stock = right.find_element(By.CSS_SELECTOR, 'div.fe-row.factory-stock').find_element(By.CSS_SELECTOR,
                                                                                                 'div.fe-col-4').text
            leadTime = right.find_element(By.CSS_SELECTOR, 'div.fe-row.factory-lead').find_element(By.CSS_SELECTOR,
                                                                                                   'div.fe-col-4').text
            unitPrice = right.find_element(By.CSS_SELECTOR, 'div.quantity-list-item').find_elements(By.CSS_SELECTOR,
                                                                                                    'div.fe-col-4.value')[
                -1].text
            result = [ppn, manu, f_ppn, f_manu, OnOrder, stock, leadTime, unitPrice, task_name]
        except Exception as e:
            print(f'get element error {e}')
    else:
        print('no result')
    MySqlHelp_recommanded.DBRecommandChip().future_info_write([result])


def go_to_ppn(ppn, manu):
    input = driver.find_element(By.ID, 'js-site-search-input')
    input.clear()
    input.send_keys(ppn)
    searchBtn = driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-link')
    searchBtn.click()
    WaitHelp.waitfor(True, False)
    get_page_data(ppn, manu)


def main():
    all_cates = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'], 2)
    for (index, ppn) in enumerate(all_cates):
        while WaitHelp.isSleep_time():
            time.sleep(60 * 5)
        if ppn.__contains__('?'):
            continue
        elif index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {index}  cate_name is: {ppn}')
            manu = all_manu[index]
            go_to_ppn(ppn, manu)


if __name__ == "__main__":
    driver.get(default_url)
    time.sleep(60)
    main()

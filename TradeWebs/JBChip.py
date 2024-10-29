# 易洛蒙
import math
import ssl
from WRTools import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp
import time
import undetected_chromedriver as uc

ssl._create_default_https_context = ssl._create_unverified_context


driver_option = webdriver.ChromeOptions()
driver = uc.Chrome(use_subprocess=True, options=driver_option)
driver.set_page_load_timeout(480)
default_url = 'https://www.jbchip.com/discountGoods'


result_save_file = PathHelp.get_file_path('TradeWebs', 'JBChip.xlsx')
log_file = PathHelp.get_file_path('TradeWebs', 'log.txt')
current_page = 1
total_page = 0


# 获取当前页面的数据
def get_page_data():
    result = []
    print(f' current page is :{current_page} total page is :{total_page}')
    tdody = driver.find_element(By.CSS_SELECTOR, 'div.p_list')
    product_models = tdody.find_elements(By.CSS_SELECTOR, 'div.p_item')
    for model in product_models:
        ppnInfo = []
        try:
            # ppn, manu,des, stock, date_line, moq, mpq, maq, batch, price
            ppn = model.find_element(By.CSS_SELECTOR, 'div.detail.partNo').find_element(By.TAG_NAME, 'a').text
            manu = model.find_element(By.CSS_SELECTOR, 'div.detail.model').find_elements(By.TAG_NAME, 'span')[1].text
            des = model.find_element(By.CSS_SELECTOR, 'div.detail.desc').find_elements(By.TAG_NAME, 'span')[1].text
            stock = model.find_element(By.CSS_SELECTOR, 'div.fourth_col').find_elements(By.TAG_NAME, 'span')[0].text
            moq = model.find_element(By.CSS_SELECTOR, 'div.fourth_col').find_element(By.TAG_NAME, 'input').get_attribute('placeholder').replace('≥ ', '')

            attrs = model.find_elements(By.XPATH, './/div[@class="detail"]')[0].find_elements(By.XPATH, './/div')
            batch = attrs[0].find_elements(By.TAG_NAME, 'span')[1].text
            mpq = attrs[2].find_elements(By.TAG_NAME, 'span')[1].text
            maq = attrs[6].find_elements(By.TAG_NAME, 'span')[1].text
            date_line = attrs[1].find_elements(By.TAG_NAME, 'span')[1].text + ';' + attrs[3].find_elements(By.TAG_NAME, 'span')[1].text

            price_info = model.find_element(By.CSS_SELECTOR, 'div.stepPrice')
            price_list = price_info.find_elements(By.XPATH, './div')
            price_str = ''
            for (index, price_item) in enumerate(price_list):
                if index > 0:
                    price_str += ('[' + price_item.find_elements(By.TAG_NAME, 'div')[0].text + price_item.find_elements(By.TAG_NAME, 'div')[1].text + ']')
            ppnInfo = [ppn, manu, batch, des, mpq, moq, maq, stock, price_str, date_line]
        except Exception as e:
            print(f'get_page_data error : {e}')
        result.append(ppnInfo)
    # 保存数据到CSV
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'jbchip', result)


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
        pages_area = driver.find_element(By.CSS_SELECTOR, 'ul.el-pager')
        pages_str = pages_area.find_elements(By.CSS_SELECTOR, 'li.number')[-1].text
        total_page = int(pages_str)
    except:
        print('get total_page error')
        total_page = 0
        driver.get(default_url)
        time.sleep(10.0)


def go_nextPage():
    global current_page
    next_page_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-next')
    next_page_button.click()
    WaitHelp.waitfor_account_import(True, False)
    current_page += 1


def main():
    go_to_manu()


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(True, False)
    main()

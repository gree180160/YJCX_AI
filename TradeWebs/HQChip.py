# 华秋
# https://www.hqchip.com/app/1723
# https://www.hqchip.com/app/1543
# https://www.hqchip.com/app/2049
# https://www.hqchip.com/app/2050
# https://www.hqchip.com/app/356
# https://www.hqchip.com/app/357
# https://www.hqchip.com/app/844
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

default_url = 'https://www.hqchip.com/'


result_save_file = PathHelp.get_file_path('TradeWebs', 'HQChip.xlsx')
log_file = PathHelp.get_file_path('TradeWebs', 'log.txt')
current_page = 1
total_page = 0


# 获取当前页面的数据
def get_page_data():
    print(f'total page {total_page} , current_page {current_page}')
    result = []
    product_models = driver.find_elements(By.CSS_SELECTOR, 'div.tr')
    for model in product_models:
        try:
            # ppn, manu, stock, date_line, minNum, addNum, packageNum, price_num, price
            col2 = model.find_element(By.CSS_SELECTOR, 'div.col2')
            ppn = col2.find_elements(By.TAG_NAME,'span')[0].text
            manu = col2.find_elements(By.TAG_NAME, 'li')[1].find_element(By.TAG_NAME,'a').text

            col4 = model.find_element(By.CSS_SELECTOR, 'div.col4')
            stock = col4.find_elements(By.TAG_NAME, 'em')[0].text
            date_line = col4.find_elements(By.TAG_NAME, 'span')[-1].text

            col3 = model.find_element(By.CSS_SELECTOR, 'div.col3')
            price_tr = col3.find_elements(By.TAG_NAME, 'tr')[-1]
            price_num = price_tr.find_elements(By.TAG_NAME, 'td')[0].text
            dicounts = price_tr.find_elements(By.TAG_NAME, 'del')
            if dicounts.__len__() > 0:
                price = price_tr.find_elements(By.TAG_NAME, 'td')[-1].text
            else:
                price = price_tr.find_elements(By.TAG_NAME, 'td')[1].text

            try:
                col5 = model.find_element(By.CSS_SELECTOR, 'div.col5')
                num_li = col5.find_elements(By.TAG_NAME, 'li')
                if num_li.__len__() > 1:
                    num_text = num_li[0].text
                    num_parts = num_text.split(' ')
                    minNum = num_parts[0].split('：')[1]
                    addNum = num_parts[1].split('：')[1]
                    pkg_text = col5.find_elements(By.TAG_NAME, 'li')[1].text
                    pkg_parts = pkg_text.split('/')
                    packageNum = pkg_parts[1].replace('」', '')
                else:
                    minNum = addNum = packageNum = ''
            except Exception as e:
                print(f'number error : {e}')
                minNum = addNum = packageNum = ''
            row = [ppn, manu, stock, date_line, minNum, addNum, packageNum, price_num, price]
        except Exception as e:
            print(f'get_page_data : {e}')
            row = []
        result.append(row)
    # 保存数据到excel
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'hqchip', result)


def go_to_manu(url):
    print(url)
    driver.get(url)
    WaitHelp.waitfor_account_import(True, False)
    exit_item()
    setPageCount()
    time.sleep(5.0)
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
        total_page = int(driver.find_elements(By.CSS_SELECTOR, 'li.number')[-1].text)
    except:
        print('get total_page error')
        total_page = 0
        driver.get(default_url)
        time.sleep(10.0)


def go_nextPage():
    global current_page
    next_page_button = driver.find_element(By.CSS_SELECTOR, 'div.btn-next')
    # 获取按钮的位置
    location = next_page_button.location
    button_height = next_page_button.size['height']
    # 计算需要滑动的距离，使按钮显示在浏览器窗口中心
    window_height = driver.execute_script("return window.innerHeight")
    scroll_distance = location['y'] - (window_height / 2) + (button_height / 2)
    # 滚动页面
    driver.execute_script(f"window.scrollTo(0, {scroll_distance});")
    # 等待一段时间以查看效果
    time.sleep(5)
    next_page_button.click()
    WaitHelp.waitfor_account_import(True, False)
    current_page += 1


def main():
    kind_urls = [
        # '1723',
        # '1543',
        '2049',
        '2050',
        '356',
        '357',
        '844'
    ]
    for temp_url in kind_urls:
        url = 'https://www.hqchip.com/app/' + temp_url
        go_to_manu(url)


def setPageCount():
    select_area = driver.find_element(By.CSS_SELECTOR, 'div.select-box')
    # 获取按钮的位置
    location = select_area.location
    button_height = select_area.size['height']

    # 计算需要滑动的距离，使按钮显示在浏览器窗口中心
    window_height = driver.execute_script("return window.innerHeight")
    scroll_distance = location['y'] - (window_height / 2) + (button_height / 2)
    # 滚动页面
    driver.execute_script(f"window.scrollTo(0, {scroll_distance});")
    # 等待一段时间以查看效果
    time.sleep(5)
    # driver.execute_script('arguments[0].scrollIntoView(true)', select_area)
    select_area.click()
    time.sleep(2.0)
    last_item = driver.find_elements(By.CSS_SELECTOR, 'div.select-dropdown-item')[-1]
    last_item.click()


def exit_item():
    exit = driver.find_element(By.CSS_SELECTOR, 'div.ext-item').find_element(By.TAG_NAME, 'svg')
    exit.click()
    time.sleep(5.0)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(False, False)
    main()

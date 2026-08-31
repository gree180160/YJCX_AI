# clarke&service electronic solution
import ssl
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp, ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time


ssl._create_default_https_context = ssl._create_unverified_context
try:
    driver = ChromeDriverManager.getWebDriver(0)
except Exception as e:
    print(e)

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TUSIElectronics.xlsx'),
                  'sourceSheet': 'source',
                  'colIndex': 1,
                  'startIndex': 1,
                  'endIndex': 10}
task_name = 'TUSIElectronics'
home_url = 'https://usielectronics.com/'
default_url = 'https://usielectronics.com/search/+/page/'

current_page = 68
total_page = 81


# 获取当前页面的数据
def get_page_data():
    # [model, manufacturer, stock, status, des]
    table_container = driver.find_element(By.CSS_SELECTOR, 'div.results')
    product_list = table_container.find_elements(By.TAG_NAME, 'tr')
    page_data = []
    for product in product_list:
        model = manufacturer = stock = status = des = ''
        try:
            td_list = product.find_elements(By.TAG_NAME, 'td')
            if td_list.__len__() >=5:
                model = td_list[0].text
                manufacturer = td_list[1].text
                stock = td_list[3].text
                status = td_list[4].text
                des = td_list[2].text
            page_data.append([model, manufacturer, stock, status, des])
        except Exception as e:
            print(e)
    ExcelHelp.add_arr_to_sheet(sourceFile_dic['fileName'], 'result', page_data)
    time.sleep(3.0)


def go_to_manu():
    global current_page, total_page
    total_page = 81
    current_page = 68
    while current_page <= total_page:
        new_url = f"{default_url}{current_page}/"
        driver.get(new_url)
        WaitHelp.waitfor(True, False)
        current_page += 1
        get_page_data()


def main():
    go_to_manu()


if __name__ == "__main__":
    driver.get(home_url)
    WaitHelp.waitfor(True, False)
    main()
import time
import random

from WRTools import ChromeDriverManager, ExcelHelp, PathHelp
from selenium.webdriver.common.by import By
from WRTools import EmailHelper
from datetime import datetime, timedelta


import ssl
ssl._create_default_https_context = ssl._create_unverified_context
try:
    driver = ChromeDriverManager.getWebDriver(0)
except Exception as e:
    print(e)

default_url = "https://apps.vicorpower.com/TestSheetReprint/testSheetList.do"
model_number = "BCM48BF080T240A00"
serial_prefix1 = "A0"
serial_prefix3 = '000' #'000'


def dateArr():
    # 定义起始和结束日期
    start_date = datetime(2024, 4, 20)
    end_date = datetime(2024, 6, 10)
    # 初始化日期数组
    date_array = []
    # 生成日期数组
    current_date = start_date
    while current_date <= end_date:
        # 格式化日期为 yymmdd
        formatted_date = current_date.strftime('%y%m%d')
        date_array.append(int(formatted_date))  # 转换为整数并添加到数组
        # 增加一天
        current_date += timedelta(days=1)
        # 输出结果
    return date_array


def scrape_form_data():
    # for (date_index, date) in enumerate(dateArr()):
    #     result = []
    #     for n in range(10):
    #         for x in range(10):
    #             for y in range(10):
    #                 for z in range(10):
    #                     for w in range(10):
    #                         serial_number = serial_prefix1 + str(date) + serial_prefix3 + str(n) + str(x) + str(y) + str(z) + str(w)
    #                         result.append(serial_number)
    #     ExcelHelp.add_arr_to_col(PathHelp.get_file_path(None, 'TVicorNumber.xlsx'), str(date), result)
    #     time.sleep(5.5)

    serial_number_arr = ExcelHelp.read_col_content(PathHelp.get_file_path(None, 'TVicorNumber.xlsx'), str(dateArr()[0]), col_index=1)
    for (temp_ser_index, temp_ser) in enumerate(serial_number_arr):
        if temp_ser_index % 7 == 0:
            form_items = driver.find_elements(By.CSS_SELECTOR, 'div.col-sm-7')
            model_n_input = form_items[0].find_element(By.TAG_NAME, 'input')
            serial_n_input = form_items[1].find_element(By.TAG_NAME, 'input')
            submit_btn = driver.find_elements(By.CSS_SELECTOR, 'button.btn.btn-sm')[0]
            model_n_input.clear()
            model_n_input.send_keys(model_number)
            time.sleep(2.0)
            serial_number = temp_ser
            serial_n_input.clear()
            serial_n_input.send_keys(serial_number)
            time.sleep(3.0)
            submit_btn.click()
            time.sleep(50 + random.randint(5, 30))
            print(f'index is:{temp_ser_index} serial is : {temp_ser}')
            if driver.find_elements(By.ID, 'list-form').__len__() > 0:
                result_str = f"Serial Number: {driver.find_elements(By.CSS_SELECTOR, 'td.text-left')[0].text}, Model Number: {driver.find_elements(By.CSS_SELECTOR, 'td.text-left')[1].text}"
                print(result_str)
                EmailHelper.mail_IC_Stock(result_str)


# 测试函数
if __name__ == "__main__":
    # 打开给定的网址
    driver.get('https://apps.vicorpower.com/TestSheetReprint')
    time.sleep(100.0)
    scrape_form_data()
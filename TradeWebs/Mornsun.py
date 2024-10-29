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

default_url = 'https://www.mornsun.cn/html/products/1/products.html'


result_save_file = PathHelp.get_file_path('TradeWebs', 'Mornsun.xlsx')
log_file = PathHelp.get_file_path('TradeWebs', 'log.txt')
current_page = 1
total_page = 0

#
# # 获取当前页面的数据
# def get_page_data():
#     result = []
#     product_models = driver.find_elements(By.CSS_SELECTOR, 'div.goods_item')
#     for model in product_models:
#         try:
#             # ppn, manu, stock, date_line, minnum, factory_date, minpakage, batch, price_num, price
#             ppn_info = model.find_element(By.CSS_SELECTOR, 'div.goods_no').find_elements(By.TAG_NAME, 'p')
#             ppn = ppn_info[0].text.replace('型号： ', '')
#             manu = ppn_info[1].text.replace('品牌： ', '')
#             stock_info = model.find_element(By.CSS_SELECTOR, 'div.goods_stock').find_elements(By.TAG_NAME, 'p')
#             stock = stock_info[0].text.replace('库存： ', '')
#             date_line = stock_info[1].text.replace('交期 ', '')
#             time_info = model.find_element(By.CSS_SELECTOR, 'div.goods_date').find_elements(By.TAG_NAME, 'p')
#             minnum = time_info[0].text.replace('起订量： ', '')
#             factory_date = time_info[1].text.replace('原厂交货时间：', '')
#             minpakage = time_info[2].text.replace('原厂最小包装： ： ', '')
#             batch = time_info[3].text.replace('产品批次： ', '')
#             try:
#                 price_info = model.find_element(By.CSS_SELECTOR, 'div.goods_price').find_elements(By.TAG_NAME, 'p')
#                 price_num = price_info[-1].find_elements(By.TAG_NAME, 'span')[0].text
#                 price = price_info[-1].find_elements(By.TAG_NAME, 'span')[1].text.replace('￥', '')
#                 result.append([ppn, manu, stock, date_line, minnum, factory_date, minpakage, batch, price_num, price])
#             except:
#                 price_num = '无'
#                 price = '无'
#                 result.append([ppn, manu, stock, date_line, minnum, factory_date, minpakage, batch, price_num, price])
#         except Exception as e:
#             print(f"Error processing element: {e}")
#     # 保存数据到CSV
#     if result.__len__() > 0:
#         ExcelHelp.add_arr_to_sheet(result_save_file, 'integ', result)
#
#
# def go_to_manu():
#     time.sleep(2.0)
#     WaitHelp.waitfor_account_import(True, False)
#     setTotal_page()
#     while current_page <= total_page:
#         get_page_data()
#         if current_page == total_page:
#             break;
#         else:
#             go_nextPage()
#
#
# def setTotal_page():
#     global total_page
#     try:
#         total_page = int(driver.find_elements(By.CSS_SELECTOR, 'a.layui-laypage-last')[-1].text)
#     except:
#         print('get total_page error')
#         total_page = 0
#         driver.get(default_url)
#         time.sleep(10.0)
#
#
# def go_nextPage():
#     global current_page
#     next_page_button = driver.find_element(By.CSS_SELECTOR, 'a.layui-laypage-next')
#     next_page_button.click()
#     WaitHelp.waitfor_account_import(True, False)
#     current_page += 1


def main():
    level1s = ExcelHelp.read_sheet_content_by_name(result_save_file, 'level2')
    for temp_url_info in level1s:
        temp_url = temp_url_info[0]
        des = temp_url_info[1]
        print(temp_url)
        result = []
        if len(str(temp_url)) > 0:
            driver.get(temp_url)
            WaitHelp.waitfor(True, False)
            table = driver.find_element(By.CSS_SELECTOR, 'table.table_con')
            lis = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.CSS_SELECTOR, 'tr.show_list')
            result = []
            for temp in lis:
                link = temp.find_element(By.TAG_NAME, 'a')
                link_text = driver.execute_script("return arguments[0].innerText;", link)
                manu = 'mornsun'
                row = [link_text, manu, des]
                result.append(row)
        ExcelHelp.add_arr_to_sheet(result_save_file, 'ppn', result)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(False, False)
    main()

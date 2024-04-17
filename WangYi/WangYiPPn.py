import base64
import ssl
import sys
from urllib import parse
from urllib.parse import urlparse
from WRTools import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, LogHelper, PathHelp, WaitHelp
from Manager import TaskManager, URLManager
import re
#page 116
ssl._create_default_https_context = ssl._create_unverified_context

driver_option = webdriver.ChromeOptions()
driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(480)

default_url = 'https://www.wyselect.com/shop/index'

sourceFile_dic = {'fileName': PathHelp.get_file_path("WangYi", 'WangYiTask2024-03.xlsx'),
                  'sourceSheet': 'manu',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 1}
result_save_file = PathHelp.get_file_path("WangYi", 'WangYiTask2024-03.xlsx')

log_file = PathHelp.get_file_path('WangYi', 'WYLog.txt')

total_page = 1
current_page = 1

# 跳转到下一个指定的型号
def go_to_cate(pn_index, pn, c_page):
    try:
        # 'https://www.wyselect.com/shop/itemList?store_sort=%20asc&page=1&brand_id=9'
        url = f'https://www.wyselect.com/shop/itemList?&brand_id=%209%20&store_sort=%20asc&page={c_page}'
        url.replace(' ', '')
        driver.get(url)
        WaitHelp.waitfor(True, False)
        set_page()
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{pn} go_to_cate except: {e}')
        if str(e.msg).__contains__('Timed out'):
            driver.reconnect()
            sys.exit()


def set_page():
    global total_page, current_page
    page_area = driver.find_elements(By.CSS_SELECTOR, "div.pagination.pag-normal.flex-center.wrap")
    if page_area.__len__() > 0:
        page_total = page_area[-1].find_element(By.TAG_NAME, "span")
        total_page = int(re.sub('[^0-9]', '', page_total.text))
        try:
            current_url = driver.current_url
            o = urlparse(current_url)
            # 将请求参数部分转化为 字典格式
            params = parse.parse_qsl(o.query)
            current_page = int(params[2][1])
        except:
            print('get current page error')
            current_page = 1
    else:
        total_page = 0


def go_to_next_page(pn_index, pn):
    try:
        url = f'https://www.wyselect.com/shop/itemList?&brand_id=%209%20&store_sort=%20asc&page={current_page + 1}'
        url.replace(' ', '')
        driver.get(url)
        WaitHelp.waitfor(True, False)
        set_page()
        analy_html(pn_index, pn)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{pn} go_to_cate except: {e}')
        if str(e.msg).__contains__('Timed out'):
            driver.reconnect()
            sys.exit()


# 解析某个型号的页面信息，如果有更多，直接点击，然后只选择start ， 遇到第一个不是star 的就返回
def analy_html(pn_index, pn):
    valid_supplier_arr = []
    try:
        ppn_list = driver.find_elements(By.CSS_SELECTOR, 'div.shop-item.flex-between')
        for ppntr in ppn_list:
            try:
                ppn = ppntr.find_element(By.CSS_SELECTOR, 'a.shop-name.ellip').text
            except:
                ppn = '--'
            try:
                supplier = ppntr.find_element(By.CSS_SELECTOR, 'div.shop-store.flex-start-center').text
            except:
                supplier = '--'
            try:
                price = ppntr.find_element(By.CSS_SELECTOR, 'div.shop-price.flex-end.show-flex').text
            except:
                price = '--'
            try:
                stock_area = ppntr.find_element(By.CSS_SELECTOR, 'div.flex-start.column')
                stock = stock_area.find_element(By.CSS_SELECTOR, 'div.flex-end.width-100').text
            except:
                stock = '--'
            record = [ppn, supplier, price, stock]
            if ppn != '--':
                valid_supplier_arr.append(record)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{pn} 页面 解析异常：{e} ')
    ExcelHelp.add_arr_to_sheet(
        file_name=result_save_file,
        sheet_name='WangYi_ppn',
        dim_arr=valid_supplier_arr)
    valid_supplier_arr.clear()
    if current_page < total_page:
        go_to_next_page(pn_index, pn)



def main():
    # all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
    #                                        sheet_name=sourceFile_dic['sourceSheet'],
    #                                        col_index=sourceFile_dic['colIndex'])
    all_cates = ['vicor']
    for (pn_index, pn) in enumerate(all_cates):
        if pn is None or pn.__contains__('?'):
            continue
        elif pn_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'pn_index is: {pn_index}  pn is: {pn}')
            go_to_cate(pn_index, pn, 1)
            analy_html(pn_index, pn)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(False, False)
    main()

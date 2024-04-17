from WRTools import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import LogHelper, PathHelp, WaitHelp, ExcelHelp
import os
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

url_file = PathHelp.get_file_path('ADI', 'ADI_URLS&PNS.xlsx')
log_file = '//ADI/ADI_pn_log.txt'
default_url = 'https://www.analog.com/cn/index.html'

driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(1000)


# 根据excel 中的列表获取html内容
def request_urls():
    # links = ExcelHelp.read_col_content(url_file, sheet_name='error_url', col_index=1)
    links = ['https://www.analog.com/cn/parametricsearch/11106#/d=s7|s25|s3|s5',
'https://www.analog.com/cn/parametricsearch/10766#/d=s7|s25|s3|s5',
'https://www.analog.com/cn/parametricsearch/11086#/d=s7|s25|s3|s5',
'https://www.analog.com/cn/parametricsearch/11230#/d=s7|s25|s3|s5',
'https://www.analog.com/cn/parametricsearch/11819#/d=s7|s25|s3|s5']
    for (index, url) in enumerate(links):
        print(f'index is :{index} url is : {url}')
        try:
            driver.get(url)
            if index > 0 and index % 15 == 0:
                WaitHelp.waitfor(True, isDebug=False)
                WaitHelp.waitfor(True, isDebug=False)
            else:
                WaitHelp.waitfor(True, isDebug=False)
        except Exception as e:
            LogHelper.write_log(log_file, f'{url} request get exception: {e}')
            return
        analy_webdriver(wdriver=driver, url=url)


# 从html页面获取pn，inventory， price， package， status
def analy_webdriver(wdriver, url):
    try:
        table = wdriver.find_element(by=By.CSS_SELECTOR, value='main.table')
        left_part = table.find_element(by=By.CSS_SELECTOR, value='section.parts')
        pns_cols = left_part.find_elements(by=By.CSS_SELECTOR, value='article.controller')
        right_part = table.find_element(by=By.CSS_SELECTOR, value='section.details')
        details = right_part.find_elements(by=By.CSS_SELECTOR, value='article.pst-row.minimized')
        pns_info = []
        for (index, pn_row) in enumerate(pns_cols):
            try:
                product = pn_row.find_element(by=By.CSS_SELECTOR, value='div.product')
                pn_name = product.find_element(by=By.TAG_NAME, value='a').text
            except:
                pn_name = '--'
            pn_detail = details[index]
            try:
                pst = pn_detail.find_element(by=By.CSS_SELECTOR, value='div.checkbox.parameter')
                inventory_value = pwww.find_element(by=By.TAG_NAME, value='a').text
            except:
                inventory_value = '--'
            try:
                price_value = pn_detail.find_elements(by=By.CSS_SELECTOR, value='div.range.parameter')[0].text
            except:
                price_value = '--'
            try:
                package_value = pn_detail.find_elements(by=By.CSS_SELECTOR, value='div.checkbox.parameter')[1].text
            except:
                package_value = '--'
            try:
                status_value = pn_detail.find_elements(by=By.CSS_SELECTOR, value='div.checkbox.parameter')[2].text
            except:
                status_value = '--'
            info = [pn_name, inventory_value, price_value, package_value, status_value]
            pns_info.append(info)
        ExcelHelp.add_arr_to_sheet(file_name=url_file, sheet_name='opnInfo_all', dim_arr=pns_info)
    except Exception as e:
        LogHelper.write_log(log_file, f'{url} analy_webdriver exception: {e}')


def main():
    request_urls()


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(True, False)
    main()
    print('aa')



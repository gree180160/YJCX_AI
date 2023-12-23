import ssl
import sys
from urllib import parse
from urllib.parse import urlparse
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, LogHelper, PathHelp, WaitHelp
from Manager import AccManage
import requests
from pathlib import Path
import re
#page 116
ssl._create_default_https_context = ssl._create_unverified_context

driver_option = webdriver.ChromeOptions()
driver = uc.Chrome(use_subprocess=True, driver_executable_path=AccManage.chromedriver_path)
driver.set_page_load_timeout(480)

default_url = 'https://www.szlcsc.com/'

sourceFile_dic = {'fileName': "/Users/liuhe/Desktop/卖什么/hxl.xlsx",
                  'sourceSheet': 'TIBrandS1',
                  'colIndex': 1,
                  'startIndex': 246,
                  'endIndex': 317}
# result_save_file = PathHelp.get_file_path("LiChuang", 'Task.xlsx')

log_file = PathHelp.get_file_path('LiChuang', 'lichuangLog.txt')


# 跳转到下一个指定的型号
def go_to_cate(pn_index, pn, c_page):
    try:
        input_area = driver.find_element(By.ID, 'search-input')
        input_area.clear()
        input_area.send_keys(pn)
        search_button = driver.find_element(By.CSS_SELECTOR, 'input.sch-bd03')
        search_button.click()
        WaitHelp.waitfor_account_import(True, False)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{pn} go_to_cate except: {e}')
        if str(e.msg).__contains__('Timed out'):
            driver.reconnect()
            sys.exit()


# 解析某个型号的页面信息，如果有更多，直接点击，然后只选择start ， 遇到第一个不是star 的就返回
def analy_html(pn_index, pn):
    try:
        # 找到网页上的所有图片元素
        aim_tr = driver.find_element(By.CSS_SELECTOR, 'tr.no-tj-tr.add-cart-tr')
        images = aim_tr.find_elements(By.TAG_NAME, 'img')
        if images.__len__() > 0:
            aim_image = images[-1]
            img_url = aim_image.get_attribute('src')
            img_format = get_image_extension_from_url(img_url)
            img_name = pn + img_format #img_url.split('/')[-1]
            img_name = img_name.replace('/', '%2F')
            driver.get(img_url)
            original_img_url = driver.current_url
            img_data = requests.get(original_img_url).content
            with open(img_name, 'wb') as f:
                f.write(img_data)
            driver.back()
        else:
            LogHelper.write_log(log_file_name=log_file, content=f'{pn} has no pic ')
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{pn} 页面 解析异常：{e} ')


# 获取图片格式
def get_image_extension_from_url(url):
    parsed_url = urlparse(url)
    path = Path(parsed_url.path)
    image_extension = path.suffix
    return image_extension


def main():
    all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
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

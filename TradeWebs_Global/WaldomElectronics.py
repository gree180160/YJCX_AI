# waldom
import ssl
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp, ChromeDriverManager
import time
from urllib.parse import quote_plus
import math


ssl._create_default_https_context = ssl._create_unverified_context
try:
    driver = ChromeDriverManager.getWebDriver(0)
except Exception as e:
    print(e)

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'Twaldom.xlsx'),
                  'sourceSheet': 'manu',
                  'colIndex': 1,
                  'startIndex': 2,
                  'endIndex': 3}
task_name = 'Twaldom'
default_url = 'https://www.waldom.com/en/suppliers/'
current_page = 1
total_page = 1


# 获取当前页面的数据
def get_page_data(manu, count):
    result = []
    print(f'current_page is {current_page}  total_page is {total_page}')
    noresult = driver.find_elements(By.ID, 'MainOptions')
    if noresult.__len__() == 0:
        code_list = driver.find_elements(By.CSS_SELECTOR, 'div.row.row-result')
        if code_list.__len__() > 0:
            for temp in code_list:
                try:
                    try:
                        ppn = temp.find_elements(By.TAG_NAME, 'h3')[0].text
                    except:
                        ppn = ppn.encode('utf-8', errors='ignore').decode('utf-8')
                      # 忽略无法编码的字符
                    try:
                        manu_des = temp.find_element(By.CSS_SELECTOR, 'a.result-brand').text
                    except:
                        manu_des = manu.encode('utf-8', errors='ignore').decode('utf-8')
                    result.append([ppn, manu_des, current_page])
                except Exception as e:
                    print(f'get element error {e}')
    else:
        print('no result')
    try:
        ExcelHelp.add_arr_to_sheet(sourceFile_dic['fileName'], 'source', result)
    except Exception as e:
        print(f'add arr to sheet error {e}')
        time.sleep(5.0)
        ExcelHelp.add_arr_to_sheet(sourceFile_dic['fileName'], 'source', result)


def go_to_manu(manu, count):
    global current_page, total_page
    if 'MOLEX' in manu:
        current_page = 288
        total_page = 3384
    else:
        current_page = 1
        total_page = 1
    while int(count) > 0 and int(current_page) <= int(total_page):
        search_content = quote_plus(manu.strip())
        new_url = f'https://www.waldom.com/en/keywordsearch?text={search_content}&greenstock=true&pagenum={current_page}'
        driver.get(new_url)
        WaitHelp.waitfor(True, False)
        setterTotalPage(int(count))
        get_page_data(manu, count)
        current_page += 1


def setterTotalPage(count):
    global total_page
    try:
        greenStock_des = driver.find_elements(By.CSS_SELECTOR, 'label.form-check-label')[-1].text
        print(greenStock_des)
        greenStock_count = greenStock_des.split("(")[-1]
        greenStock_count = greenStock_count.replace(")", "")
        total_page = math.ceil(int(greenStock_count) / 10)
    except:
        total_page = 1


def main():
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    all_count = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'], 2)
    for (index, ppn) in enumerate(all_manu):
        while WaitHelp.isSleep_time():
            time.sleep(60 * 5)
        if index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'manu_index is: {index}  manu_name is: {ppn}')
            count = all_count[index]
            go_to_manu(ppn, count)


if __name__ == "__main__":
    driver.get(default_url)
    time.sleep(60)
    main()
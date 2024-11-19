import ssl
import time
from WRTools import ChromeDriverManager
from selenium.webdriver.common.by import By

import Manager.URLManager
from WRTools import LogHelper, ExcelHelp, WaitHelp, EmailHelper, PathHelp

ssl._create_default_https_context = ssl._create_unverified_context

driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(1000)
# logic
default_url = 'https://octopart.com/'

sourceFile_dic = {'fileName': PathHelp.get_file_path('Octopart_category', 'octopart.xlsx'),
                  'sourceSheet': 'manu',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 1}
result_save_file = PathHelp.get_file_path('Octopart_category', 'octopart.xlsx')
log_file = PathHelp.get_file_path('Octopart_category', 'octopart_key_cate_log.txt')

try:
    driver = ChromeDriverManager.getWebDriver(1)
except Exception as e:
    print(e)

total_page = 1
current_page = 1
# 出现安全验证的次数，连续三次则关闭webdriver
security_times = 0


# 验证是否处于验证IP 页面
def is_security_check() -> bool:
    global security_times
    result = False
    try:
        alert = driver.find_element(by=By.CSS_SELECTOR, value='div.inner.narrow')
        if alert and len(alert) > 0:
            result = True
            security_times += 1
            EmailHelper.mail_ip_error("mac")
            time.sleep(60)
    except:
        result = False
        security_times = 0
    if security_times > 3:
        driver.close()
    return result


# 获取总页数
def set_totalpage():
    global total_page
    try:
        ul = driver.find_elements(by=By.CSS_SELECTOR, value='ul.m-0.inline-block.list-none')[-1]
        li_last = ul.find_elements(by=By.CSS_SELECTOR, value='li.inline-block')[-1]
        total_page = int(li_last.find_element(by=By.TAG_NAME, value='a').text)
    except:
        total_page = 1


# 获取总页数
def set_current_page():
    global current_page
    try:
        nav = driver.find_element(by=By.CSS_SELECTOR, value='nav.justify-center')
        span = nav.find_element(By.CSS_SELECTOR, value='span.tw-btn.text-white.no-underline')
        current_page = int(span.text)
    except:
        current_page = 1


# 确定根据key 是否有匹配的结果，避开建议性的结果
def has_content() -> bool:
    result = True
    try:
        no_result = driver.find_elements(by=By.CSS_SELECTOR, value='div.bg-slate-800.px-5.py-[13px].text-lg.text-white')
        if no_result and len(no_result) > 0:
            result = False
    except:
        result = True
    return result


# 跳转到下一个指定的型号 page , 的那一页
def go_manu(key, url):
    try:
        driver.get(url)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{key} go_manu except: {e}')
        if str(e.msg).__contains__('Timed out'):
            driver.reconnect()


def go_next_page(key_name):
    global current_page
    try:
        nav3 = driver.find_elements(By.TAG_NAME, 'nav')[2]
        next_button = nav3.find_elements(by=By.TAG_NAME, value='a')[-1]
        next_button.click()
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{key_name} go_manu except: {e}')
    current_page += 1


def get_category(key_index, manu):
    global current_page, total_page
    current_page = 1
    total_page = 1
    while True:
        print(f'key_index is: {key_index} page is: {current_page} totalpage is : {total_page}')
        try:
            url = Manager.URLManager.octopart_get_page_url(key_name='', page=current_page, manu=manu)
            print(f'url is: {url}')
            go_manu(url=url)
            if current_page > 1 and current_page%15 == 0:
                time.sleep(500)
            else:
                WaitHelp.waitfor_octopart(is_load_page=True, isDebug=False)
        except Exception as e:
            LogHelper.write_log(log_file, f'{manu} request get exception: {e}')
            return
        if is_security_check(driver):
            LogHelper.write_log(log_file_name=log_file, content=f'{manu} ip security check')
            break
        if not has_content(driver=driver):
            break
        set_totalpage()
        set_current_page()
        analyth_html(manu)
        time.sleep(2)
        if current_page >= total_page:
            break
        else:
            go_next_page(manu)


# 解析html，获取cate，manu
def analyth_html(manu):
    pn = manu
    ppn_list = []
    try:
        all_cates_table = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="prices-view-part"]')
        for row in all_cates_table:
            header = row.find_element(By.CSS_SELECTOR, 'div[data-testid="part-header"]')
            ppn = header.find_element(By.CSS_SELECTOR, 'div[data-testid="serp-part-header-mpn"]').text
            manu = header.find_elements(By.CSS_SELECTOR, 'div.whitespace-nowrap.text-md')[0].text
            des = header.find_element(By.CSS_SELECTOR, 'div.max-w-[444px].text-sm.leading-4').text
            try:
                price = header.find_elements(By.CSS_SELECTOR, 'div.whitespace-nowrap.text-md')[1].text
            except:
                price = ''
            row_info = [ppn, manu, des, price]
            ppn_list.append(row_info)
    except Exception as e:
        LogHelper.write_log(log_file, f'{manu} analyth_html error {e}')
    if ppn_list.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'oc_ppn', row_info)


def main():
    all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    for (cate_index, cate_name) in enumerate(all_cates):
        if cate_name is None or cate_name.__contains__('?'):
            continue
        elif cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            manu = Manager.URLManager.Octopart_manu.NoManu
            cate_name = str(cate_name).strip()
            get_category(key_index=cate_index, key_name=cate_name, manu=manu)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(True, False)
    main()

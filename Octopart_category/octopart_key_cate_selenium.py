import ssl
import time
import undetected_chromedriver as uc
import re
from selenium.webdriver.common.by import By

import Manager.URLManager
from WRTools import LogHelper, ExcelHelp, WaitHelp, EmailHelper, PathHelp

ssl._create_default_https_context = ssl._create_unverified_context

# driver_option = webdriver.ChromeOptions()
# driver_option.add_argument("–incognito")  #隐身模式
# 等待初始HTML文档完全加载和解析，
# driver_option.page_load_strategy = 'eager'
driver = uc.Chrome(use_subprocess=True)
# logic
default_url = 'https://octopart.com/'

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TOnsemi.xlsx'),
                  'sourceSheet': 'opn',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 125}
result_save_file = PathHelp.get_file_path('TRenesasAll_25H', 'octopart_price.xlsx')

log_file = PathHelp.get_file_path(super_path='Octopart_category', file_name='octopart_key_cate_log.txt')

total_page = 1
current_page = 1
# 出现安全验证的次数，连续三次则关闭webdriver
security_times = 0


# 验证是否处于验证IP 页面
def is_security_check(driver) -> bool:
    global security_times
    result = False
    try:
        alert = driver.find_element(by=By.CSS_SELECTOR, value='div.inner.narrow')
        if alert and len(alert) > 0:
            result = True
            security_times += 1
            EmailHelper.mail_ip_error("mac")
            # QGHelp.maintainWhiteList()  #todo remove qg
            time.sleep(60)
    except:
        result = False
        security_times = 0
    if security_times > 3:
        driver.close()
    return result


# 获取总页数
def set_totalpage(driver):
    global total_page
    try:
        ul = driver.find_element(by=By.CSS_SELECTOR, value='ul.jsx-4126298714.jumps')
        li_last = ul.find_elements(by=By.CSS_SELECTOR, value='li.jsx-4126298714')[-1]
        a = li_last.find_element(by=By.CSS_SELECTOR, value='a')
        total_page = int(a.text)
    except:
        total_page = 1


# 确定根据key 是否有匹配的结果，避开建议性的结果
def has_content(driver) -> bool:
    result = True
    try:
        no_result = driver.find_elements(by=By.CSS_SELECTOR, value='div.jsx-1140710980.no-results-found')
        if no_result and len(no_result) > 0:
            result = False
    except:
        result = True
    return result


# 跳转到下一个指定的型号 page , 的那一页
def go_to_cate(key, url):
    try:
        if driver.current_url.startswith('https://octopart.com/search?q='):
            if driver.current_url == url:
                return
            driver.get(url)
        else:
            driver.get(url)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{key} go_to_cate except: {e}')


def go_next_page(key_name):
    global current_page
    try:
        next_button = driver.find_element(by=By.CSS_SELECTOR, value='a.jsx-1876408219.next')
        next_button.click()
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{key_name} go_to_cate except: {e}')
    current_page += 1


def get_category(key_index, key_name, manu):
    global current_page, total_page
    current_page = 1
    total_page = 1
    while current_page <= total_page:
        print(f'key_index is: {key_index} key_name is: {key_name} page is: {current_page} totalpage is : {total_page}')
        try:
            # driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            #     "userAgent": f"{UserAgentHelper.getRandowUA_Mac()}",
            #     "platform": "macOS"})
            url = Manager.URLManager.octopart_get_page_url(key_name=key_name, page=current_page, manu=manu)
            url = url.replace('view-source:', '')
            print(f'url is: {url}')
            go_to_cate(key=key_name, url=url)
            if current_page > 1 and current_page%15 == 0:
                time.sleep(240)
            else:
                WaitHelp.waitfor_octopart(is_load_page=True, isDebug=False)
        except Exception as e:
            current_page += 1
            LogHelper.write_log(log_file, f'{key_name} request get exception: {e}')
            return
        if is_security_check(driver):
            current_page += 1
            LogHelper.write_log(log_file_name=log_file, content=f'{key_name} ip security check')
            break
        if not has_content(driver=driver):
            current_page += 1
            break
        set_totalpage(driver)
        analyth_html(key_name=key_name)
        time.sleep(2)
        current_page += 1


# 解析html，获取cate，manu
def analyth_html(key_name):
    try:
        table = driver.find_element(by=By.CSS_SELECTOR, value='div.jsx-2172888034.prices-view')
        cate_first = table.find_elements(by=By.CSS_SELECTOR, value='div.jsx-2172888034')
        cate_left = table.find_elements(by=By.CSS_SELECTOR, value='div.jsx-2400378105.part')
        cates_all = cate_first + cate_left
        info_list = []
        for temp_cate in cates_all:
            header = temp_cate.find_element(by=By.CSS_SELECTOR, value='div.jsx-3355510592.header')
            try:
                manu = header.find_element(by=By.CSS_SELECTOR, value='div.jsx-312275976.jsx-2018853745.manufacturer-name-and-possible-tooltip').text
            except:
                manu = None
            try:
                cate_name = header.find_element(by=By.CSS_SELECTOR, value='div.jsx-312275976.jsx-2018853745.mpn').text
            except:
                cate_name = None
            if cate_name and manu:
                if check_htmlPPN_valid(html_ppn=cate_name, opn=key_name):
                    info_list.append([cate_name, manu, key_name, total_page])
        if len(info_list) > 0:
            ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name='ppn', dim_arr=info_list)
    except Exception as e:
        LogHelper.write_log(log_file, f'{key_name} analyth_html exception: {e}')


# 验证获取的ppn 是否与opn 相关
def check_htmlPPN_valid(html_ppn, opn):
    opn = opn.replace(" ", "")
    html_ppn = html_ppn.replace(" ", "")
    # 去掉结尾的+，因为pn ,结尾有无+都是一个型号
    if opn.endswith('+'):
        pn = opn[0:-1]
    if html_ppn.endswith('+'):
        html_pn = html_ppn[0:-1]
    result = bool(re.search(opn, html_ppn, re.IGNORECASE))
    return result


def main():
    all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    for (cate_index, cate_name) in enumerate(all_cates):
        if cate_name is None or cate_name.__contains__('?'):
            continue
        elif cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            manu = Manager.URLManager.Octopart_manu.Onsemi
            get_category(key_index=cate_index, key_name=cate_name, manu=manu)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(True, False)
    main()

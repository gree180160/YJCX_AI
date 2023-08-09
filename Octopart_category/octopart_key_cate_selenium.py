import ssl
import time
import undetected_chromedriver as uc
import re
from selenium.webdriver.common.by import By
from selenium import webdriver

import Manager.URLManager
from WRTools import LogHelper, ExcelHelp, WaitHelp, EmailHelper, PathHelp

ssl._create_default_https_context = ssl._create_unverified_context

# driver_option = webdriver.ChromeOptions()
# driver_option.add_argument("–incognito")  #隐身模式
# 等待初始HTML文档完全加载和解析，
# driver_option.page_load_strategy = 'eager'
# fire_options = webdriver.FirefoxOptions()
# fire_options.add_argument('--headless')
# fire_options.add_argument('blink-settings=imagesEnabled=false')
# driver = webdriver.Firefox(options=fire_options)
driver = uc.Chrome(use_subprocess=True)
driver.set_page_load_timeout(1000)
# logic
default_url = 'https://octopart.com/'

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TNXP.xlsx'),
                  'sourceSheet': 'unfinished_url',
                  'colIndex': 1,
                  'startIndex': 517,
                  'endIndex': 600}
result_save_file = PathHelp.get_file_path(None, 'TNXP.xlsx')

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
def set_totalpage():
    global total_page
    try:
        ul = driver.find_element(by=By.CSS_SELECTOR, value='ul.jsx-4126298714.jumps')
        li_last = ul.find_elements(by=By.CSS_SELECTOR, value='li.jsx-4126298714')[-1]
        a = li_last.find_element(by=By.CSS_SELECTOR, value='a')
        total_page = int(a.text)
    except:
        total_page = 1


# 获取总页数
def set_current_page():
    global current_page
    try:
        li = driver.find_element(by=By.CSS_SELECTOR, value='li.jsx-4126298714.is-active')
        span = li.find_element(By.TAG_NAME, value='span')
        current_page = int(span.text)
    except:
        current_page = 1


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
        driver.get(url)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{key} go_to_cate except: {e}')
        if str(e.msg).__contains__('Timed out'):
            driver.reconnect()


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
    while True:
        print(f'key_index is: {key_index} key_name is: {key_name} page is: {current_page} totalpage is : {total_page}')
        try:
            url = Manager.URLManager.octopart_get_page_url(key_name=key_name, page=current_page, manu=manu)
            print(f'url is: {url}')
            go_to_cate(key=key_name, url=url)
            if current_page > 1 and current_page%15 == 0:
                time.sleep(500)
            else:
                WaitHelp.waitfor_octopart(is_load_page=True, isDebug=False)
        except Exception as e:
            LogHelper.write_log(log_file, f'{key_name} request get exception: {e}')
            return
        if is_security_check(driver):
            LogHelper.write_log(log_file_name=log_file, content=f'{key_name} ip security check')
            break
        if not has_content(driver=driver):
            break
        set_totalpage()
        set_current_page()
        analyth_html(pn=key_name)
        time.sleep(2)
        if current_page >= total_page:
            break
        else:
            go_next_page(key_name)


# 解析html，获取cate，manu
def analyth_html(pn):
    ppn_list = []
    try:
        all_cates_table = driver.find_elements(By.CSS_SELECTOR, 'div.jsx-2906236790.prices-view')
        if all_cates_table.__len__() > 0:
            left_rows = all_cates_table[0].find_elements(By.CSS_SELECTOR, 'div.jsx-4014881838.part')
            showed_rows = left_rows
        # 默认直接显示的row
        for temp_cate_row in showed_rows:
            try:
                ppn = get_cate_name(cate_area=temp_cate_row, opn=pn)
                manu = get_manufacture_name(cate_area=temp_cate_row, opn=pn)
                if check_htmlPPN_valid(html_ppn=ppn, opn=pn):
                    info = [ppn, manu, str(current_page), pn]
                    ppn_list.append(info)
            except Exception as e:
                LogHelper.write_log(log_file_name=log_file, content=f'{pn} 当个cate 解析异常：{e} ')
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{pn} 页面 解析异常：{e} ')
    ExcelHelp.add_arr_to_sheet(
        file_name=result_save_file,
        sheet_name='octopart_ppn',
        dim_arr=ppn_list)


# 获取cate
def get_cate_name(cate_area, opn) -> str:
    cate_name = ''
    try:
        header = cate_area.find_elements(By.CSS_SELECTOR, 'div.jsx-2471764431.header')[0]
        cate_name = header.find_elements(By.CSS_SELECTOR, 'div.jsx-312275976.jsx-1485186546')[2].text
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{opn} cannot check keyname: {e}')
    return cate_name


# 获取cate
def get_cate_name(cate_area, opn) -> str:
    cate_name = ''
    try:
        cate_name = cate_area.find_element(By.CSS_SELECTOR, 'div.jsx-312275976.jsx-1485186546.mpn').text
        # cate_name = cate_area.find_element(By.TAG_NAME, 'mark').text
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{opn} cannot check keyname: {e}')
    return cate_name


# 获取manu
def get_manufacture_name(cate_area, opn) -> str:
    manu_name = ''
    try:
        header = cate_area.find_element(By.CSS_SELECTOR, 'div.jsx-2471764431.header')
        manu_name = header.find_elements(By.CSS_SELECTOR, 'div.jsx-312275976.jsx-1485186546.manufacturer-name-and-possible-tooltip')[0].text
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{opn} cannot check manufacture: {e}')
    return manu_name


# 验证获取的ppn 是否与opn 相关
def check_htmlPPN_valid(html_ppn, opn):
    opn = str(opn).strip()
    html_ppn = str(html_ppn).strip()
    # 去掉结尾的+，因为pn ,结尾有无+都是一个型号
    if opn.endswith('+'):
        opn = opn[0:-1]
    if html_ppn.endswith('+'):
        html_ppn = html_ppn[0:-1]
    result = bool(re.search(opn, html_ppn, re.IGNORECASE))
    if not result:
        result = str(html_ppn).find(opn, 0, len(opn))
    return result


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

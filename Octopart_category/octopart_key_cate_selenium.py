import base64
import random
import ssl
import time
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import UserAgentHelper, LogHelper, ExcelHelp, WaitHelp, EmailHelper, PathHelp

ssl._create_default_https_context = ssl._create_unverified_context
"""
driver_option = webdriver.ChromeOptions()
# 青果proxy
proxyAddr = "http://tunnel5.qg.net:18716"
driver_option.add_argument('--proxy-server=%(server)s' % {"server": proxyAddr})
# driver_option.add_argument("–incognito")  #隐身模式
# 等待初始HTML文档完全加载和解析，
# driver_option.page_load_strategy = 'eager'
driver = uc.Chrome(use_subprocess=True, options=driver_option)
# logic

"""
default_url = 'https://octopart.com/'

keyword_source_file = PathHelp.get_file_path(super_path=None, file_name='TMMS_NRV.xlsx')
log_file = PathHelp.get_file_path(super_path='Octopart_category', file_name='octopart_key_cate_log.txt')

totol_page = 1
current_page = 1
# 出现安全验证的次数，连续三次则关闭webdriver
security_times = 0


#  通用的octopart url 获取
def get_url(key_name, page, alpha, manu_ids) -> str:
    manu_param = '&manufacturer_id=' + manu_ids.replace(';', '&manufacturer_id=')
    page_param = '' if page == 1 else '&start=' + str(page*10 - 10)
    url = f'view-source:https://octopart.com/search?q={key_name}{alpha}&currency=USD&specs=0{manu_param}{page_param}'
    return url


# infenion
def get_url_infenion(key_name, page) -> str:
    #url = f'view-source:https://octopart.com/search?q={key_name}&currency=USD&specs=0'
    url = get_url(key_name=key_name, alpha='', page=page, manu_ids='453;202;706;12547;196')
    return url


# https://octopart.com/search?q=82C54&currency=USD&specs=0&start=20
def get_url_renasas(key_name, page) -> str:
    page_param = '' if page == 1 else '&start=' + str(page * 10 - 10)
    url = f'view-source:https://octopart.com/search?q={key_name}&currency=USD&specs=0{page_param}'
    return url


# nxp
def get_url_nxp(opn, page) -> str:
    url = get_url(key_name=opn, alpha='', page=page, manu_ids='561;296;145')
    return url


# 批量获取octopart url
def get_octopart_urls():
    pn_file = PathHelp.get_file_path(super_path="TMagSensor", file_name='TMagneticSensor.xlsx')
    opns = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='opn', col_index=1)
    result = []
    for (index, temp_opn) in enumerate(opns):
        manu = '453;202;706;12547;196'
        url = get_url(key_name=temp_opn, alpha='', page=1, manu_ids=manu)
        result.append([url])
    ExcelHelp.add_arr_to_sheet(file_name=pn_file, sheet_name='octopart_url', dim_arr=result)


'''
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
    global totol_page
    try:
        ul = driver.find_element(by=By.CSS_SELECTOR, value='ul.jsx-4126298714.jumps')
        li_last = ul.find_elements(by=By.CSS_SELECTOR, value='li.jsx-4126298714')[-1]
        a = li_last.find_element(by=By.CSS_SELECTOR, value='a')
        totol_page = int(a.text)
    except:
        totol_page = 1


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


# 跳转到下一个指定的型号,alpha, page , 的那一页
def go_to_cate(key_and_alpha, url):
    try:
        if driver.current_url.startswith('https://octopart.com/search?q='):
            if driver.current_url == url:
                return
            driver.get(url)
        else:
            driver.get(url)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{key_and_alpha} go_to_cate except: {e}')


def go_next_page(key_name, alpha):
    global current_page
    if not check_valid_key(key_name):
        current_page = totol_page
        return
    try:
        next_button = driver.find_element(by=By.CSS_SELECTOR, value='a.jsx-1876408219.next')
        next_button.click()
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{key_name+alpha} go_to_cate except: {e}')
    current_page += 1
'''


#     判断key是否有必要查询
# def check_valid_key(key_name):
#     return key_name != last_unvalid_key

'''
def get_category(key_index, key_name, manu_ids, alpha):
    global current_page, totol_page
    current_page = 1
    totol_page = 1
    while current_page <= totol_page:
        print(f'key_index is: {key_index} key_name is: {key_name} alpha is: {alpha} page is: {current_page} totalpage is : {totol_page}')
        try:
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": f"{UserAgentHelper.getRandowUA_windows()}",
                "platform": "Windows"})
            go_to_cate(key_and_alpha=key_name+alpha, url=get_url(key_name=key_name, manu_ids=manu_ids, alpha=alpha, page=current_page))
            if current_page > 1 and current_page%15 == 0:
                time.sleep(500)
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
        analyth_html(key_name=key_name, alpha=alpha)
        time.sleep(2)
        current_page += 1


# 解析html，获取cate，manu
def analyth_html(key_name, alpha):
    try:
        table = driver.find_element(by=By.CSS_SELECTOR, value='div.jsx-2172888034.prices-view')
        cate_first = table.find_elements(by=By.CSS_SELECTOR, value='div.jsx-2172888034')
        cate_left = table.find_elements(by=By.CSS_SELECTOR, value='div.jsx-2400378105.part')
        cates_all = cate_first + cate_left
        info_list = []
        for temp_cate in cates_all:
            header = temp_cate.find_element(by=By.CSS_SELECTOR, value='div.jsx-3355510592.header')
            try:
                manu = header.find_element(by=By.CSS_SELECTOR, value='div.jsx-312275976.jsx-2649123136.manufacturer-name-and-possible-tooltip').text
            except:
                manu = None
            try:
                cate_name = header.find_element(by=By.CSS_SELECTOR, value='div.jsx-312275976.jsx-2649123136.mpn').text
            except:
                cate_name = None
            if cate_name and manu:
                if cate_name.startswith(key_name):
                    info_list.append([cate_name, manu, key_name+alpha, current_page])
        if len(info_list) > 0:
            ExcelHelp.add_arr_to_sheet(file_name=f'{key_name}.xlsx', sheet_name='all', dim_arr=info_list)
    except Exception as e:
        LogHelper.write_log(log_file, f'{key_name+alpha} analyth_html exception: {e}')


def main():
    add_alphabet_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    key_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='all', col_index=1)
    manuid_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='all', col_index=3)
    for (key_index, key_name) in enumerate(key_list):
        if key_index%6 == 0 or key_index%6 == 1:
            for alpha in add_alphabet_list:
                get_category(key_index=key_index, key_name="TPS1", manu_ids = "370" , alpha="")
                # get_category(key_index=key_index, key_name=key_name, manu_ids = str(manuid_list[key_index]) , alpha=alpha)

'''

def keyword_getURL_page0():
    add_alphabet_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                         'T', 'U',
                         'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    key_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='all', col_index=1)
    manuid_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='all', col_index=3)
    url_list = []
    for (key_index, key_name) in enumerate(key_list):
        for alpha in add_alphabet_list:
            url = get_url(key_name=key_name, page=current_page, alpha=alpha, manu_ids=str(manuid_list[key_index]))
            url_list.append([url])
            # get_category(key_index=key_index, key_name=key_name, manu_ids = str(manuid_list[key_index]) , alpha=alpha)
    ExcelHelp.add_arr_to_sheet(file_name=keyword_source_file, sheet_name='url_all', dim_arr=url_list)


def infenion_getURL_page0():
    key_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='ppn', col_index=1)
    url_list = []
    for (key_index, key_name) in enumerate(key_list):
        url = get_url_infenion(key_name=key_name, page=1)
        url_list.append([url])
    ExcelHelp.add_arr_to_sheet(file_name=keyword_source_file, sheet_name='octopart_url', dim_arr=url_list)

# adi
def adi_getURL_page0():
    key_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='opn', col_index=1)
    url_list = []
    for (key_index, key_name) in enumerate(key_list):
        url = get_url(key_name=key_name, page=1, alpha='', manu_ids='26;244;12048;2274')
        url_list.append([url])
    ExcelHelp.add_arr_to_sheet(file_name=keyword_source_file, sheet_name='octopart_url', dim_arr=url_list)


def adi_get_total_page_more():
    pn_file = PathHelp.get_file_path(super_path=None, file_name='TADI.xlsx')
    pninfo_list = ExcelHelp.read_sheet_content_by_name(file_name=pn_file, sheet_name='page0_pn')
    last_search_param = ''
    for pnInfo in pninfo_list:
        pninfo_url_list = []
        try:
            if pnInfo is None:
                continue
            key_name = str(pnInfo[2]) + str(pnInfo[3])
            if key_name is None:
                continue
            current_search_param = key_name
            if current_search_param == last_search_param:
                continue
            else:
                last_search_param = current_search_param
            total_p = int(pnInfo[4])
            current_p = 2
            if total_p > 1:
                while current_p <= total_p:
                    url = get_url(key_name=key_name, page=current_p, alpha='', manu_ids='26;244;12048;2274')
                    pninfo_url_list.append([url])
                    current_p += 1
        except:
            print(pnInfo + "exception")
        ExcelHelp.add_arr_to_sheet(file_name=pn_file, sheet_name='url_pagemore', dim_arr=pninfo_url_list)
    print('over')



def MMS_NRV_getURL_page0():
    key_list = ExcelHelp.read_col_content(file_name=keyword_source_file, sheet_name='ppn', col_index=1)
    url_list = []
    for (key_index, key_name) in enumerate(key_list):
        url = get_url(key_name=key_name, page=1, alpha='', manu_ids='278')
        url_list.append([url])
    ExcelHelp.add_arr_to_sheet(file_name=keyword_source_file, sheet_name='octopart_url', dim_arr=url_list)


# 根据keyname page 0 的数据获取total page ，然后获取page 0 之后的页面的url并保存
def get_total_page_more(sourcefile: str, page0_sheet: str, munu_str: str):
    pn_file = sourcefile
    pninfo_list = ExcelHelp.read_sheet_content_by_name(file_name=pn_file, sheet_name=page0_sheet)
    last_search_param = ''
    for pnInfo in pninfo_list:
        pninfo_url_list = []
        try:
            if pnInfo is None:
                continue
            key_name = str(pnInfo[2]) + str(pnInfo[3])
            if key_name is None:
                continue
            current_search_param = key_name
            if current_search_param == last_search_param:
                continue
            else:
                last_search_param = current_search_param
            total_p = int(pnInfo[4])
            current_p = 2
            if total_p > 1:
                while current_p <= total_p:
                    url = get_url(key_name=key_name, page=current_p, alpha='', manu_ids=munu_str)
                    pninfo_url_list.append([url])
                    current_p += 1
        except:
            print(pnInfo + "exception")
        ExcelHelp.add_arr_to_sheet(file_name=pn_file, sheet_name='url_pagemore', dim_arr=pninfo_url_list)
    print('over')


if __name__ == "__main__":
    # UserAgentHelper.driver_update_UA(webdriver=driver)
    # driver.get(default_url)
    # WaitHelp.waitfor_octopart(True, False)
    # main()
    #MMS_NRV_getURL_page0()
    # get_total_page_more(sourcefile=PathHelp.get_file_path(super_path=None, file_name='TADI.xlsx'), page0_sheet='page0_pn', munu_str='26;244;12048;2274')
    get_octopart_urls()
# 对于贸易商数量超过5家的，跑一下正能量里面的价格，取3个月内的最高值，没有价格则忽略
# 35021-1160 获取云价格
import base64
import random
import ssl
import time

from WRTools import ChromeDriverManager
from selenium.webdriver.common.by import By
from WRTools import LogHelper, PathHelp, ExcelHelp, WaitHelp, MySqlHelp_recommanded
from Manager import AccManage
import bom_price_info
import re

ssl._create_default_https_context = ssl._create_unverified_context
driver = ChromeDriverManager.getWebDriver(0)    # todo chromedriverPath
driver.set_page_load_timeout(120)
# logic

accouts_arr = [[AccManage.Bom3['c'], AccManage.Bom3['n'], AccManage.Bom3['p']]]

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TVibrationMeter.xlsx'),
                  'sourceSheet': 'ppn2',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 2}
task_name = 'TVibrationMeter'

default_url = 'https://www.bom.ai/'
log_file = PathHelp.get_file_path('Bom_price', 'bom_price_log.txt')


# 登陆action
def login_action(aim_url):
    time.sleep(2.0)
    login_url = 'https://mm.bom.ai/#/loginbom'
    driver.get(login_url)
    time.sleep(5.0)
    try:
        login_are = driver.find_element(By.CSS_SELECTOR, 'div.Bom_loging_left')
        account_li = login_are.find_elements(By.TAG_NAME, 'li')[1]
        account_li.click()
        time.sleep(2.0)
        accout_current = accouts_arr
        compay = driver.find_element(By.CSS_SELECTOR, 'input.Bom_loging_input')[0]
        compay.clear()
        compay.send_keys(accout_current[0])
        username = driver.find_element(By.CSS_SELECTOR, 'input.Bom_loging_input')[0]
        username.clear()
        username.send_keys(accout_current[1])
        password = driver.find_element(By.CSS_SELECTOR, 'input.Bom_loging_input')[0]
        password.clear()
        password.send_keys(accout_current[2])
        time.sleep(1)
        driver.find_element(by=By.CSS_SELECTOR, value='input.Bom_loging_login').click()
        time.sleep(2.0)
    except:
        print("登陆操作失败")
    time.sleep(15.0)
    if driver.current_url.__contains__('HomeMain'): #登陆后，回到控制台页面
        print("login_success")
    if aim_url.__len__() > 0: #查询过程中的登陆
        driver.get(aim_url)
    else: #第一次的登陆
        driver.get('https://www.bom.ai/ic/==QURVQzg0MkJDUFo2Mi01.html')
    time.sleep(30.0)


# 判断是否需要登陆，如果需要就登陆
def current_need_login() -> bool:
    if driver.current_url.startswith('https://www.bom.ai/ic'):
        try:
            login_links = driver.find_elements(by=By.CLASS_NAME, value='bom_power_a.bom_layer_login')
            if len(login_links) > 0:
                login_links[0].click()
                login_action(default_url)
        except Exception as e:
            LogHelper.write_log(log_file_name=log_file, content=f'login check exception：{e}')
            return False
    else:
        return False


# 跳转到下一个指定的型号
def go_to_cate(cate_index, cate_name):
    try:
        if driver.current_url.startswith('https://www.bom.ai/ic'):
            if cate_name.encode().isalnum():
                param = cate_name
            else:
                param = str(base64.b64encode(cate_name.encode('utf-8')), 'utf-8')
                param = '==' + param
            driver.get(f'https://www.bom.ai/ic/{param}.html')
        else:
            driver.get(default_url)
            go_to_cate(cate_index, cate_name)
    except:
            login_action(f'https://www.bom.ai/ic/{cate_name}.html')


# 获取所有云价格记录总数
def get_total_supplier():
    result = 0
    links = driver.find_elements(By.CSS_SELECTOR, 'a.bomID_extStock_More')
    if links.__len__() > 0:
        result_str = links[0].text
        result_str = re.sub('[^0-9]', '', result_str)
        result = int(result_str)
    return result


# 解析某个型号的页面信息，先看未折叠的前三行，判断是否需要展开，展开，解析，再判断，再展开，再解析。。。。
def analy_html(cate_index, ppn, manu):
    total_count = get_total_supplier()
    showed_supplier = show_suppliers()
    # 是否需要继续展开。 出现第一条非本周数据后不再展开
    need_more = need_click_more(showed_supplier, cate_index, ppn, manu)
    # 默认直接现实的row
    valid_supplier_arr = []
    # total_count 总数在只有一页时不显示
    total_count = max(total_count, showed_supplier.__len__())
    if total_count > 0 or showed_supplier.__len__() > 0:
        while showed_supplier.__len__() <= total_count and need_more:
            clickResult = click_more_supplier()
            if clickResult:
                WaitHelp.waitfor(True, False)
                showed_supplier = show_suppliers()
                need_more = (need_click_more(showed_supplier, cate_index, ppn, manu))
            else:
                need_more = False
        for aside in showed_supplier:
            bom_price_ele = get_supplier_info(aside=aside, cate_index=cate_index, ppn=ppn, manu=manu)
            # 无论是否有效都记录
            if bom_price_ele and str(bom_price_ele.supplier).__len__() > 0 and bom_price_ele.is_valid_supplier():
                valid_supplier_arr.append(bom_price_ele.descritpion_arr() + [task_name])
        MySqlHelp_recommanded.DBRecommandChip().bom_price_write(valid_supplier_arr)
        valid_supplier_arr.clear()
    else:
        # MySqlHelp_recommanded.DBRecommandChip().bom_price_write([[ppn, '??', '??', "??"]])
        print(f'{cate_index}th {ppn} has no record')


#获取所有的supplier
def show_suppliers():
    show_suppliers = driver.find_elements(By.CSS_SELECTOR, 'aside.stock-view.bom_cloud_num02.mainext')
    return show_suppliers


# 更具showed_supplier 的最后一条是否有效，判断是否需要继续more
def need_click_more(li_arr, cate_index, ppn, manu):
    result = False
    if li_arr.__len__() > 0:
        last_value = li_arr[-1]
        bom_price_ele = get_supplier_info(last_value, cate_index, ppn, manu)
        if bom_price_ele and bom_price_ele.is_valid_supplier():
            result = True
    return result


# 点击获取更多supplier 信息的a
def click_more_supplier():
    links = driver.find_elements(By.CSS_SELECTOR, 'a.bomID_extStock_More')
    if links.__len__() > 0:
        try:
            links[0].click()
            return True
        except Exception as e:
            LogHelper.write_log(log_file, f'click more error {e}')
            return False


# 将页面row的内容 转化成Bom_price_info
# aside: contain row info
def get_supplier_info(aside, cate_index, ppn, manu) -> bom_price_info.Bom_price_info:
    try:
        section_arr = aside.find_elements(by=By.TAG_NAME, value='section')
        supplier_section = section_arr[1]
        try:
            supplier_name = supplier_section.find_element(by=By.TAG_NAME, value='a').text
        except:
            supplier_name = '--'
        cate_name_section = section_arr[2]
        try:
            cate_name = cate_name_section.find_element(by=By.TAG_NAME, value='a').text
            # 无需做ppn 和 bom 获取的cate_name 的匹配验证
        except:
            cate_name = '--'
        pakage_section = section_arr[4]
        try:
            pakage_name = pakage_section.find_element(by=By.TAG_NAME, value='p').text
        except:
            pakage_name = '--'
        year_section = section_arr[5]
        try:
            year_str = year_section.find_element(by=By.TAG_NAME, value='p').text
        except:
            year_str = '--'
        price_section = section_arr[6]
        try:
            price_str = price_section.text
        except:
            price_str = '--'
        release_time_section = section_arr[7]
        try:
            release_time = release_time_section.find_element(by=By.TAG_NAME, value='p').text
        except:
            release_time = '--'
        stock_num_section = section_arr[8]
        try:
            stock_num = stock_num_section.find_element(by=By.TAG_NAME, value='p').text
        except:
            stock_num = '--'
        bom_price_ele = bom_price_info.Bom_price_info(cate=cate_name, manu=manu, supplier=supplier_name,
                                                      package=pakage_name, lot=year_str, quoted_price=price_str,
                                                      release_time=release_time, stock_num=stock_num)
        return bom_price_ele
    except Exception as e:
        LogHelper.write_log(PathHelp.get_file_path('Bom_price', 'bom_price_log.txt'), f'cate is: {ppn} index is:{cate_index} , error is : {e}')
        return None


def main():
    all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    all_manus =  ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex']+1)
    for (ppn_index, ppn) in enumerate(all_cates):
        if ppn is None or ppn.__contains__('?'):
            continue
        elif ppn_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {ppn_index}  cate_name is: {ppn}')
            go_to_cate(ppn_index, str(ppn))
            if ppn_index > 0 and ppn_index % 15 == 0:
                time.sleep(480)
            else:
                WaitHelp.waitfor(True, False)
            current_need_login()
            analy_html(cate_index=ppn_index, ppn=str(ppn), manu=all_manus[ppn_index])


def closeAD():
    try:
        closeButton = driver.find_elements(By.CSS_SELECTOR, 'i.znlbfont-close_ic')[-1]
        closeButton.click()
        time.sleep(2.0)
    except:
        print('closeAD error')


if __name__ == "__main__":
    driver.get(default_url)
    login_action("")
    WaitHelp.waitfor(True, False)
    closeAD()
    main()

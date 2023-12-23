import time

from WRTools import ExcelHelp, WaitHelp, PathHelp, MySqlHelp_recommanded, EmailHelper, LogHelper
from selenium.webdriver.common.by import By
import random
import undetected_chromedriver as uc
import ssl
import os
from Manager import AccManage, TaskManager, URLManager
import base64

log_file = PathHelp.get_file_path('IC_search', 'IC_search_Image_log.txt')
ssl._create_default_https_context = ssl._create_unverified_context

total_page = 1
current_page = 1
accouts_arr = [[AccManage.IC_hot['n'], AccManage.IC_hot['p']]]

if AccManage.chromedriver_path.__len__() > 0:
    driver = uc.Chrome(use_subprocess=True, driver_executable_path=AccManage.chromedriver_path) #todo chromedriverPath
else:
    driver = uc.Chrome(use_subprocess=True)
driver.set_window_size(height=800, width=1200)
current_cate_has_date = True

def login_action(aim_url):
    current_url = driver.current_url
    if current_url.__contains__("https://member.ic.net.cn/login.php"):
        WaitHelp.waitfor_ICHot(False, False)
        # begin login
        accout_current = random.choice(accouts_arr)
        driver.find_element(by=By.ID, value='username').clear()
        driver.find_element(by=By.ID, value='username').send_keys(accout_current[0])
        driver.find_element(by=By.ID, value='password').clear()
        driver.find_element(by=By.ID, value='password').send_keys(accout_current[1])
        WaitHelp.waitfor_ICHot(False, False)
        driver.find_element(by=By.ID, value='btn_login').click()
        WaitHelp.waitfor_ICHot(True, False)
    if driver.current_url.startswith('https://member.ic.net'):  # 首次登录
        driver.get(aim_url)
    elif driver.current_url.startswith('https://www.ic.net.cn/search'):  # 查询过程中出现登录
        driver.get(aim_url)


def has_hotData() -> bool:
    nodatas_areas = driver.find_elements(By.CSS_SELECTOR, 'div.nodatas')
    if nodatas_areas.__len__() > 0:
        return False
    return True


# 获取单个型号热度信息
# cate_name：型号
# isWeek：【周/月】搜索指数
def getSearchInfo(cate_name,manu, isWeek):
    global current_cate_has_date
    search_url = URLManager.IC_hot_url(cate_name)
    if isWeek:
        driver.get(search_url)
        WaitHelp.waitfor_ICHot(True, False)
    if isNeedLogin(search_url):
        login_action(search_url)
    else:
        while isCheckCode():
            WaitHelp.waitfor_ICHot(True, False)
            EmailHelper.mail_IC_Hot(AccManage.Device_ID)
        if has_hotData():
            anlyth_page(search_url, cate_name, manu, isWeek)
        else:
            print(f'{cate_name}: no hot data')


def anlyth_page(aim_url, cate_name, manu, isWeek):
    try:
        table = driver.find_elements(by=By.CLASS_NAME, value='details_main_tabel')[0]
        tbody = table.find_element(by=By.TAG_NAME, value='tbody')
        tr_arr = tbody.find_elements(by=By.TAG_NAME, value='tr')
        last_row = tr_arr[-1]
        fold = last_row.find_element(By.CSS_SELECTOR, 'span.switchBtn')
        if fold.text.__contains__('展开'):
            fold.click()
            time.sleep(2.0)
        heat_value_arr = []
        for temp_row in tr_arr:
            tds = temp_row.find_elements(By.TAG_NAME, 'td')
            if tds.__len__() > 2:
                td = tds[2]
                max_value = td.text
                heat_value_arr.append(max_value)
        deal_sql_data(cate_name, manu, isWeek, heat_value_arr)
    except Exception as e:
        LogHelper.write_log(log_file, f'IC_search error. {aim_url} {e}')


def deal_sql_data(ppn, manu, isWeek, rec_arr):
    image_hot_data = [ppn, manu] + rec_arr + [TaskManager.Taskmanger.task_name]
    if isWeek:
        MySqlHelp_recommanded.DBRecommandChip().IC_hot_w_write([image_hot_data])
    else:
        MySqlHelp_recommanded.DBRecommandChip().IC_hot_m_write([image_hot_data])


def isNeedLogin(aim_url):
    try:
        tips_main_areas = driver.find_elements(By.CSS_SELECTOR, 'div.tips_main')
        if tips_main_areas.__len__() > 0:
           result = tips_main_areas[0].is_displayed()
           return result
    except Exception as e:
        print('no need to login')
        return False


def isCheckCode():
    verification_area = driver.find_elements(By.ID, "captcha")
    if verification_area.__len__() > 0:
        result = True
    else:
        result = False
    return result


# 获取IC 创芯指数概述
def getIC_des(ppn ,manu):
    info = []
    try:
        sjtext = driver.find_element(By.CSS_SELECTOR, 'p.sjText')
        redTs = sjtext.find_elements(By.CSS_SELECTOR, 'span.redT')
        todaySearch = redTs[0].text
        todaySearch_person = redTs[1].text
        yesterdaySearch = redTs[2].text
        yesterdaySearch_person = redTs[3].text

        bzText = driver.find_element(By.CSS_SELECTOR, 'div.bzText')
        orangTs = bzText.find_elements(By.CSS_SELECTOR, 'span.orangeT')
        reference_price = orangTs[0].text
        week_search = orangTs[1].text
        market_hot = orangTs[2].text
        risk = orangTs[3].text
        mainLand_stock = orangTs[4].text
        international_stock = orangTs[5].text
        info = [ppn, manu, todaySearch, todaySearch_person, yesterdaySearch, yesterdaySearch_person, reference_price, week_search, market_hot, risk, mainLand_stock, international_stock, TaskManager.Taskmanger().task_name]
    except:
        info = [ppn, manu, '-',  '-',  '-',  '-',  '-', '-',  '-',  '-'  '-',  '-', TaskManager.Taskmanger().task_name]
    result = [info]
    MySqlHelp_recommanded.DBRecommandChip().ic_des_write(result)


# 查询列表中所有需要查询的型号的搜索指数
def main():
    pn_file = PathHelp.get_file_path(None, f'{TaskManager.Taskmanger().task_name}.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=1)
    manu_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=2)
    for (index, ppn) in enumerate(ppn_list):
        if index in range(0, TaskManager.Taskmanger().end_index): #mac 100   #  if index in range(201, TaskManager.Taskmanger().end_index): #mac 100
            print(f'cate_index is: {index}  cate_name is: {ppn}')
            manu = manu_list[index]
            getSearchInfo(ppn, manu, True)
            time.sleep(10.0)
            if has_hotData():  # 有周数据，请求月数据
                getIC_des(ppn, manu)
                time.sleep(5.0)
                try:
                    title_links = driver.find_elements(By.CSS_SELECTOR, 'a.tit')
                    title_links[1].click()
                except:
                    title_links = driver.find_elements(By.CSS_SELECTOR, 'a.tit')
                    print(f'click month error. title_links.count is :{title_links.__len__()}')
                time.sleep(10.0)
                getSearchInfo(ppn, manu, False)


if __name__ == "__main__":
    driver.get("https://member.ic.net.cn/login.php")
    login_action("https://member.ic.net.cn/member/member_index.php")
    WaitHelp.waitfor_ICHot(True, False)
    main()

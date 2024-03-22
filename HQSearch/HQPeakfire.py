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
accouts_arr = [AccManage.HQ_hot['n'], AccManage.HQ_hot['p']]

login_url = "https://passport.hqew.com/login"

if AccManage.chromedriver_path.__len__() > 0:
    driver = uc.Chrome(use_subprocess=True, driver_executable_path=AccManage.chromedriver_path) #todo chromedriverPath
else:
    driver = uc.Chrome(use_subprocess=True)
driver.set_window_size(height=800, width=1200)
current_cate_has_date = True


def login_action(aim_url):
    current_url = driver.current_url
    if current_url.__contains__(login_url):
        WaitHelp.waitfor_ICHot(False, False)
        # begin login
        accout_current = random.choice(accouts_arr)
        driver.find_element(by=By.ID, value='J_loginName').clear()
        driver.find_element(by=By.ID, value='J_loginName').send_keys(accout_current[0])
        driver.find_element(by=By.ID, value='J_loginPsw').clear()
        driver.find_element(by=By.ID, value='J_loginPsw').send_keys(accout_current[1])
        WaitHelp.waitfor_ICHot(False, False)
        driver.find_element(by=By.ID, value='J_btnLogin').click()
        WaitHelp.waitfor_ICHot(True, False)
    if driver.current_url.startswith('https://ibsv3.hqew.com'):  # 首次登录
        driver.get(aim_url)
    elif driver.current_url.startswith('https://fh.hqew.com/detail'):  # 查询过程中出现登录
        driver.get(aim_url)


def has_hotData() -> bool:
    nodatas_areas = driver.find_elements(By.CSS_SELECTOR, 'div.no-data')
    if nodatas_areas.__len__() > 0:
        return False
    return True


# 获取单个型号热度信息
# cate_name：型号
# isWeek：【周/月】搜索指数
def getSearchInfo(cate_name,manu, isWeek):
    weekInfos = driver.find_elements(By.ID, 'template_0')
    if weekInfos.__len__() > 0:
        try:
            weekInfo = weekInfos[0]
            week_baseInfo = weekInfo.find_element(By.CSS_SELECTOR, 'ul.sum-bd')
            items = week_baseInfo.find_elements(By.CSS_SELECTOR, 'li.sum-item')
            try:
                data0 = items[0].find_element(By.CSS_SELECTOR, 'div.sum-data')

            except:
                print('week base info error')

            heat =
        except:
            print('week info error')



    heat
    stock
    price
    supplier



def anlyth_page(aim_url, cate_name, manu, isWeek):



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
                try:
                    timeLabs = driver.find_element(By.CSS_SELECTOR, 'div.time-tabs')
                    timeLabs.find_elements(By.TAG_NAME, 'a')[1].click()
                except:
                    timeLabs = driver.find_element(By.CSS_SELECTOR, 'div.time-tabs')
                    links =  timeLabs.find_elements(By.TAG_NAME, 'a')
                    print(f'click month error. title_links.count is :{links.__len__()}')
                time.sleep(10.0)
                getSearchInfo(ppn, manu, False)


if __name__ == "__main__":
    driver.get("https://member.ic.net.cn/login.php")
    login_action("https://member.ic.net.cn/member/member_index.php")
    WaitHelp.waitfor_ICHot(True, False)
    main()

from WRTools import ExcelHelp, WaitHelp, PathHelp, MySqlHelp_recommanded, DDDDOCR, ImageHelp, EmailHelper
from selenium.webdriver.common.by import By
import random
import undetected_chromedriver as uc
import ssl
import shutil
import os
from Manager import AccManage, TaskManager, URLManager
import base64


ssl._create_default_https_context = ssl._create_unverified_context

total_page = 1
current_page = 1
accouts_arr = [[AccManage.IC_stock['n'], AccManage.IC_stock['p']]]
no_data_url = 'https://icpi.ic.net.cn/'

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


def has_hotData():
    if driver.current_url == no_data_url:
        result = False
    else:
        result = True
    return result


# 获取单个型号热度信息
# cate_name：型号
# isWeek：【周/月】搜索指数
def getSearchInfo(cate_name,manu, isWeek):
    global current_cate_has_date
    search_url = URLManager.IC_hot_url(cate_name, isWeek)
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
        table = driver.find_element(by=By.CLASS_NAME, value='details_main_tabel')
        tbody = table.find_element(by=By.TAG_NAME, value='tbody')
        tr_arr = tbody.find_elements(by=By.TAG_NAME, value='tr')  # 只取前12
        heat_value_arr = []
        for temp_row in tr_arr:
            td = temp_row.find_elements(By.TAG_NAME, 'td')[2]
            canvas = td.find_element(By.TAG_NAME, 'canvas')
            # 将canvas内容保存为.png图片
            canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
            #0
            ImageHelp.canvasToImage_color(canvas_base64, PathHelp.get_file_path('IC_Search', 'canvas0.png'), (255, 204, 0))
            reco_value0 = DDDDOCR.reco(source_image=PathHelp.get_file_path('IC_Search', 'canvas0.png'))
            #white
            ImageHelp.canvasToImage_color(canvas_base64, PathHelp.get_file_path('IC_Search', 'canvas1.png'), (255, 204, 153))
            reco_value1 = DDDDOCR.reco(source_image=PathHelp.get_file_path('IC_Search', 'canvas1.png'))
            #yellow
            ImageHelp.canvasToImage_color(canvas_base64, PathHelp.get_file_path('IC_Search', 'canvas2.png'), (102, 255, 255))
            reco_value2 = DDDDOCR.reco(source_image=PathHelp.get_file_path('IC_Search', 'canvas2.png'))
            #blue
            ImageHelp.canvasToImage_color(canvas_base64, PathHelp.get_file_path('IC_Search', 'canvas3.png'), (0, 255, 153))
            reco_value3 = DDDDOCR.reco(source_image=PathHelp.get_file_path('IC_Search', 'canvas3.png'))
            max_value = max(reco_value0, reco_value1, reco_value2, reco_value3)
            heat_value_arr.append(max_value)
        deal_sql_data(cate_name, manu, isWeek, heat_value_arr)
    except Exception as e:
        print(f"{aim_url} anlyth_page")


def deal_sql_data(ppn, manu, isWeek, rec_arr):
    image_hot_data = [ppn, manu] + rec_arr
    if isWeek:
        MySqlHelp_recommanded.IC_hot_w_write([image_hot_data])
    else:
        MySqlHelp_recommanded.IC_hot_m_write([image_hot_data])


# copy image and rename
def savaImage(new_image_name):
    path = '//IC_Search'
    new_path = '/Users/liuhe/Desktop/TestLogImage'
    item = 'temp.png'
    src = os.path.join(os.path.abspath(path), item)
    dst = os.path.join(os.path.abspath(new_path), new_image_name)
    # 复制图像
    shutil.copy(src, dst)


def isNeedLogin(aim_url):
    try:
        tips_main_areas = driver.find_elements(By.CSS_SELECTOR, 'div.tips_main')
        if tips_main_areas.__len__() > 0:
           result = tips_main_areas[0].is_displayed()
           return result
            # login_a = tips_main_areas[0].find_element(By.CSS_SELECTOR, 'a.tips_login')
            # login_a.click()
            # WaitHelp.waitfor_ICHot(True, False)
            # login_action(aim_url=aim_url)
    except Exception as e:
        print('no need to login')
        return False


def isCheckCode():
    verification_area = driver.find_elements(By.ID, "verification")
    if verification_area.__len__() > 0:
        result = True
    else:
        result = False
    return result


# 查询列表中所有需要查询的型号的搜索指数
def main():
    pn_file = PathHelp.get_file_path(None, f'{TaskManager.Task_IC_hot_C_manger.task_name}.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=1)
    manu_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=2)
    for (index, ppn) in enumerate(ppn_list):
        if index in range(TaskManager.Task_IC_hot_C_manger().start_index, TaskManager.Task_IC_hot_C_manger.end_index):
            print(f'cate_index is: {index}  cate_name is: {ppn}')
            manu = manu_list[index]
            getSearchInfo(ppn, manu, True)
            if has_hotData(): #有周数据，请求月数据
                getSearchInfo(ppn, manu, False)


if __name__ == "__main__":
    driver.get("https://member.ic.net.cn/login.php")
    login_action("https://member.ic.net.cn/member/member_index.php")
    WaitHelp.waitfor_ICHot(True, False)
    main()

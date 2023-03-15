# 使用火狐浏览器打开IC指数页面，用火狐截屏，然后保存图片，然后修改图片名称，最后识别图片中的数据，根据图片名称，保存到指定到ppn 下面
import time

from PIL import Image, ImageGrab
import random
from WRTools import ExcelHelp, PathHelp, WaitHelp, UserInput, ChracterReconition
from selenium import webdriver
import base64
from selenium.webdriver.common.by import By
import ssl
import os
from Manager import AccountMange,URLManager


ssl._create_default_https_context = ssl._create_unverified_context
total_page = 1
current_page = 1
accouts_arr = [[AccountMange.IC_hot['n'], AccountMange.IC_hot['p']]]
# driver_option = webdriver.ChromeOptions()
# driver_option.add_argument(f'--proxy-server=http://{IPHelper.getRandowCityIP()}')
fire_options = webdriver.FirefoxOptions()
fire_options.add_argument('--headless')
fire_options.add_argument('blink-settings=imagesEnabled=false')
driver = webdriver.Firefox(options=fire_options)
# driver.set_window_size(height=800, width=1200)
current_cate_has_date = True

sourceFile_dic = {'fileName': PathHelp.get_file_path('TSpeedReneseas', 'Task.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 2}
result_save_file = PathHelp.get_file_path('TSpeedReneseas', 'findchip_stock.xlsx')
login_url = "https://member.ic.net.cn/login.php"
no_data_url = 'https://icpi.ic.net.cn/'


# login
def login_action(aim_url):
    current_url = driver.current_url
    if current_url == login_url:
        WaitHelp.waitfor_account_import(False, False)
        # begin login
        accout_current = random.choice(accouts_arr)
        driver.find_element(by=By.ID, value='username').clear()
        driver.find_element(by=By.ID, value='username').send_keys(accout_current[0])
        driver.find_element(by=By.ID, value='password').clear()
        driver.find_element(by=By.ID, value='password').send_keys(accout_current[1])
        WaitHelp.waitfor_account_import(False, False)
        driver.find_element(by=By.ID, value='btn_login').click()
        WaitHelp.waitfor_account_import(True, False)
        if driver.current_url.startswith('https://www.ic.net.cn/member/'): # 首次登录
            driver.get(aim_url)
        elif driver.current_url.startswith('https://icpi.ic.net.cn/icpi/detail'): # 查询过程中出现登录
            driver.get(aim_url)
        WaitHelp.waitfor_octopart(False, False)


# 获取单个型号热度信息
# cate_name：型号
# isWeek：【周/月】搜索指数
def search_hotInfo(cate_name, cate_index, isWeek):
    search_url = URLManager.IC_hot_url(cate_name, isWeek)
    driver.get(search_url)
    WaitHelp.waitfor_account_import(True, False)
    if driver.current_url == no_data_url:
        return  # 如果周没有数据，月搜索指数不查询
    elif driver.current_url == login_url:
        login_action(search_url)
    saveImageAndRename(ppn_index=cate_index, isWeek=isWeek)
    time.sleep(2.0)
    save_hot_record(ppn=cate_name,ppn_index=cate_index, isWeek=isWeek, save_file=sourceFile_dic['fileName'])
    if isWeek:
        search_hotInfo(cate_name,cate_index=cate_index, isWeek=False)


# 保存截图+关闭页面+修改保存图的名称
def saveImageAndRename(ppn_index, is_week):
    # 保存完把焦点切换到火狐
    UserInput.screenShot_saveAndClose()
    # rename
    fold_path = PathHelp.get_IC_hot_image_fold()
    file_list = os.listdir(fold_path)
    if file_list and file_list.__len__() > 0:
        aim_file_path = fold_path + '/' + file_list[-1]
        new_name = imageName_new = str(ppn_index) + ('_W' if is_week else '_M') + '.png'
        os.rename(aim_file_path, fold_path + '/' + imageName_new)


# 根据ppn 和is_week 计算截图名称，根据名称，获取图片中的数据, 并保存
def save_hot_record(ppn, ppn_index, is_week, save_file):
    image_file_path = PathHelp.get_IC_hot_image_fold() + '/' + str(ppn_index) + ('_W' if is_week else '_M') + '.png'
    if is_week:
        image_hot_data = ChracterReconition.SplitPic_month(image_file_path)
        image_hot_data.insert(0, ppn)
        ExcelHelp.add_arr_to_sheet(file_name=save_file, sheet_name='IC_hot_month', dim_arr=[image_hot_data])
    else:
        image_hot_data = ChracterReconition.SplitPic_week(image_file_path)
        image_hot_data.insert(0, ppn)
        ExcelHelp.add_arr_to_sheet(file_name=save_file, sheet_name='IC_hot_week', dim_arr=[image_hot_data])


# 查询列表中所有需要查询的型号的搜索指数
def main():
    global current_cate_has_date
    ppns = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    for (ppn_index, ppn_name) in enumerate(ppns):
        print(f'index is: {ppn_index}  index is: {ppn_name}')
        search_hotInfo(cate_name=ppn_name, cate_index=ppn_index, isWeek=True)


# print('识别到的中文')
if __name__ == "__main__":
    driver.get(login_url)
    login_action("https://member.ic.net.cn/member/member_index.php")
    main()




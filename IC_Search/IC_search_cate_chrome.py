from PIL import Image, ImageGrab
from pytesseract import *
from WRTools import UserAgentHelper, ExcelHelp, PathHelp, WaitHelp, IPHelper
from selenium import webdriver
import base64
from selenium.webdriver.common.by import By
import time
import random
import undetected_chromedriver as uc
import ssl
from io import BytesIO
import cv2
import re
import shutil
import os


ssl._create_default_https_context = ssl._create_unverified_context

total_page = 1
current_page = 1
accouts_arr = [["17712288872", "yjcx8872"]]
driver_option = webdriver.ChromeOptions()
#  等待初始HTML文档完全加载和解析，
driver_option.page_load_strategy = 'eager'
# 无痕浏览
driver_option.add_argument("–incognito")
driver_option.add_argument(f'--proxy-server=http://{IPHelper.getRandowCityIP()}')
driver_option.add_argument(f'user-agent="{UserAgentHelper.getRandowUA()}"')
prefs = {"profile.managed_default_content_settings.images": 2}
driver_option.add_experimental_option('prefs', prefs)
driver = uc.Chrome(use_subprocess=True)
driver.set_window_size(height=800, width=1200)
current_cate_has_date = True


def login_action(aim_url):
    current_url = driver.current_url
    if current_url == "https://member.ic.net.cn/login.php":
        waitfor(False)
        # begin login
        accout_current = random.choice(accouts_arr)
        driver.find_element(by=By.ID, value='username').clear()
        driver.find_element(by=By.ID, value='username').send_keys(accout_current[0])
        waitfor(False)
        driver.find_element(by=By.ID, value='password').clear()
        driver.find_element(by=By.ID, value='password').send_keys(accout_current[1])
        waitfor(False)
        driver.find_element(by=By.ID, value='btn_login').click()
        waitfor(True)
        time.sleep(10)
    if not driver.current_url.startswith('https://www.ic.net.cn/member/'):
        driver.get(aim_url)
    waitfor(False)


# 等待时间，load new page -> 5s; else 2s
def waitfor(is_load_page):
    # load new page
    if is_load_page:
        time.sleep(30 + random.randint(1, 5))
        driver.refresh()
    # user action
    else:
        time.sleep(15 + random.randint(1, 4))


# 获取单个型号热度信息
# cate_name：型号
# isWeek：【周/月】搜索指数
def getSearchInfo(cate_name, isWeek):
    global current_cate_has_date
    # todo 不替换url，在搜索框里输入内容
    if isWeek:
        search_url = f'https://icpi.ic.net.cn/icpi/detail.php?key={cate_name}'
    else:
        search_url = f'https://icpi.ic.net.cn/icpi/detail_month.php?key={cate_name}'
    driver.get(search_url)
    waitfor(False)
    time.sleep(200 + random.randint(5, 60))
    if not driver.current_url.__contains__(cate_name):
        if isWeek:
            current_cate_has_date = False  # 如果周没有数据，月搜索指数不查询
        return
    login_action(search_url)
    try:
        table = driver.find_element(by=By.CLASS_NAME, value='details_main_tabel')
        tbody = table.find_element(by=By.TAG_NAME, value='tbody')
        tr_arr = tbody.find_elements(by=By.TAG_NAME, value='tr')  # 只取前12
        heat_value_arr = []
        if len(tr_arr) >= 12:
            tr_arr = tr_arr[0:12]
            row_element = tr_arr[-1]
            #  热度
            row_children = row_element.find_elements(by=By.TAG_NAME, value='td')
            heat_value_arr = get_heat_value_arr(row_children[2])
        elif len(tr_arr) >= 2:
            tr_arr = tr_arr[1:]
        else:
            tr_arr = []
        search_value_arr = []
        for (index, tr_value) in enumerate(tr_arr):
            try:
                #  time_value
                td_arr = tr_value.find_elements(by=By.TAG_NAME, value='td')
                if len(td_arr) >= 2:
                    time_value = td_arr[1].text
                    if len(heat_value_arr) > index:
                        heat_value = heat_value_arr[index]
                    else:
                        heat_value = '--'
                else:
                    time_value = '--'
                    heat_value = '--'
            except:
                heat_value = getReduValue('temp.png')
            search_value_arr.append([time_value, heat_value])
        saveSearchInfo(search_value_arr, isWeek=isWeek, cate_name=cate_name)
        image_name_tail = "_week" if isWeek else "_month"
        savaImage(cate_name + image_name_tail + ".png")
        search_value_arr.clear()
    except:
        print(f"{cate_name}no data")


# 将element(列表结果的第12行)底部与浏览器窗口底部对齐，然后开始截屏，并开始1-12裁剪，返回识别的结果数组
def get_heat_value_arr(element):
    driver.execute_script("arguments[0].scrollIntoView(false);", element)
    time.sleep(0.5)
    location = element.location
    size = element.size
    left = location['x']
    right = location['x'] + size['width']
    screen_shoot = driver.get_screenshot_as_png()
    im = Image.open(BytesIO(screen_shoot))
    screen_height = im.height
    im = im.crop((left, screen_height - size['height']*12, right, screen_height))  # defines crop points
    im.save('temp.png')  # saves new cropped image
    heat_value_arr = getReduValue('temp.png')
    return heat_value_arr


# 获取图片文字,return hot value arr
def getReduValue(image_name):
    img = cv2.imread(image_name)
    threshold = 180  # to be determined
    _, img_binarized = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    pil_img = Image.fromarray(img_binarized)
    try:
        result_str = pytesseract.image_to_string(pil_img, lang='eng', config="--psm 6 digits")
        result_str = result_str.replace('.', '')
        result_str = re.sub('\n+', '\n', result_str)
    except:
        result_str = "--"
    result_arr = result_str.split('\n')
    return result_arr


# copy image and rename
def savaImage(new_image_name):
    path = '//IC_Search'
    new_path = '/Users/liuhe/Desktop/TestLogImage'
    item = 'temp.png'
    src = os.path.join(os.path.abspath(path), item)
    dst = os.path.join(os.path.abspath(new_path), new_image_name)
    # 复制图像
    shutil.copy(src, dst)


# 保存型号的搜索信息[[2022.07, 165][2022.08, 250]]
def saveSearchInfo(info_arr, isWeek, cate_name):
    file_name = "/Users/liuhe/PycharmProjects/YJCX_AI/IC_Search/T0815_week.xlsx" if isWeek else "/Users/liuhe/PycharmProjects/YJCX_AI/IC_Search/T0815_month.xlsx"
    sheet_name_base64str = str(base64.b64encode(cate_name.encode('utf-8')), 'utf-8')
    ExcelHelp.add_arr_to_sheet(file_name=file_name, sheet_name=sheet_name_base64str,
                                          dim_arr=info_arr)


# 查询列表中所有需要查询的型号的搜索指数
def main():
    global current_cate_has_date
    cate_ids = ExcelHelp.read_col_content('//IC_Search/T0815.xlsx',
                                                     'left', 1)
    for (cate_index, cate_name) in enumerate(cate_ids):
        current_cate_has_date = True
        print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
        getSearchInfo(cate_name, True)
        if current_cate_has_date:
            getSearchInfo(cate_name, False)


def saveLongScreenShot():
    br = webdriver.PhantomJS()
    br.maximize_window()
    br.get("https://www.cnblogs.com/Jack-cx/p/9383990.html")
    br.save_screenshot("app1.png")


# print('识别到的中文')
if __name__ == "__main__":
    driver.get("https://member.ic.net.cn/login.php")
    saveLongScreenShot()
    #login_action("https://member.ic.net.cn/member/member_index.php")
    #main()
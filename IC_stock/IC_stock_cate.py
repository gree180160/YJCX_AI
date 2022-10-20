#  记录E01 提供的型号，在IC 中的库存信息
import base64
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import random
import undetected_chromedriver as uc
import ssl
from IC_stock import IC_stock_excel_read, IC_Stock_excel_write
from IC_stock.IC_Stock_Info import IC_Stock_Info
import WRTools.IPHelper
import WRTools.UserAgentHelper

ssl._create_default_https_context = ssl._create_unverified_context


total_page = 1
current_page = 1
accouts_arr = [["13776467165", "yjcx0718"]]
driver_option = webdriver.ChromeOptions()
driver_option.add_argument(f'--proxy-server=http://{WRTools.IPHelper.getRandowIP()}')
driver_option.add_argument("–incognito")
#  等待初始HTML文档完全加载和解析，
driver_option.page_load_strategy = 'eager'
driver_option.add_argument(f'user-agent="{WRTools.UserAgentHelper.getRandowUA()}"')
prefs = {"profile.managed_default_content_settings.images": 2}
driver_option.add_experimental_option('prefs', prefs)
driver = uc.Chrome(use_subprocess=True)
driver.set_page_load_timeout(10)


def get_total_page():
    global total_page
    global current_page
    total_page = 1
    try:
        li_arr = driver.find_element(by=By.CLASS_NAME, value="pagepicker").find_elements(by=By.TAG_NAME, value='li')
        if total_page is not None and len(li_arr) > 0:
            total_page = int(li_arr[len(li_arr) - 1].text)
    except:
        li_arr = []
        total_page = 1
    current_page = 1


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
    waitfor(True)


# 等待时间，load new page -> 5s; else 2s
def waitfor(is_load_page):
    # load new page
    if is_load_page:
        time.sleep(10 + random.randint(1, 5))
    else:
        time.sleep(5 + random.randint(1, 4))


#   二维数组，page 列表， table 列表
def get_stock(cate_index, cate_name):
    global current_page
    search_url = f"https://www.ic.net.cn/search/{cate_name}.html"
    driver.get(search_url)
    login_action(search_url)
    # 延时几秒确保页面加载完毕
    waitfor(False)
    # page_content = driver.page_source
    # print("page content is：", page_content)
    get_total_page()
    print(f"cate is:{cate_name} currentPage is: {current_page} totalpage is:{total_page}")
    #  2-loop page arr
    need_load_nextPage = True
    while current_page <= total_page and need_load_nextPage:
        try:
            li_arr = driver.find_element(by=By.ID, value='resultList').find_elements(by=By.TAG_NAME, value='li')
        except:
            li_arr = []
        need_save_ic_arr = []
        #  3-loop table arr
        for templi in li_arr:
            # print("li is:", templi.__str__())
            try:
                supplier = templi.find_element(by=By.CLASS_NAME, value='result_goCompany').text
            except:
                supplier = "--"
            try:
                isICCP = (templi.find_element(by=By.CLASS_NAME, value='iccp') is not None)
            except:
                isICCP = False
            try:
                isSSCP = (templi.find_element(by=By.CLASS_NAME, value='sscp') is not None)
            except:
                isSSCP = False
            try:
                model = templi.find_element(by=By.CLASS_NAME, value='product_number').text
            except:
                model = '--'
            try:
                isSpotRanking = (templi.find_element(by=By.CLASS_NAME, value='icon_xianHuo') is not None)
            except:
                isSpotRanking = False
            try:
                isHotSell = (templi.find_element(by=By.CLASS_NAME, value='icon_reMai') is not None)
            except:
                isHotSell = False
            try:
                manufacturer = templi.find_element(by=By.CLASS_NAME, value='result_factory').text
            except:
                manufacturer = '--'
            try:
                stock_num_arr = templi.find_elements(by=By.TAG_NAME, value='div')
                stock_num = '0'
                for ele in stock_num_arr:
                    name_value = ele.get_attribute("class")
                    display_value = ele.is_displayed()
                    if name_value.startswith('result_totalNumber') and display_value:
                        stock_num = ele.text
            except:
                stock_num = '0'
            search_date = time.strftime('%Y-%m-%d', time.localtime())
            ic_Stock_Info = IC_Stock_Info(supplier=supplier, isICCP=isICCP, isSSCP=isSSCP, model=model,
                                          isSpotRanking=isSpotRanking, isHotSell=isHotSell,
                                          manufacturer=manufacturer, stock_num=stock_num, search_date=search_date)
            if ic_Stock_Info.shouldSave():
                saveContent_arr = ic_Stock_Info.descritpion_arr()
                need_save_ic_arr.append(saveContent_arr)
        # save per page
        sheet_name_base64str = str(base64.b64encode(cate_name.encode('utf-8')), 'utf-8')
        IC_Stock_excel_write.add_arr_to_sheet(file_name='/Users/liuhe/PycharmProjects/SeleniumDemo/IC_stock/IC_stock_cate_0815.xlsx', sheet_name=sheet_name_base64str,
                                              dim_arr=need_save_ic_arr)
        if current_page >= 2 or len(need_save_ic_arr) <= 1:
            need_load_nextPage = False
        need_save_ic_arr.clear()
        # 翻页
        old_url = driver.current_url
        if current_page < total_page:
            js = f"javascript:pageTo({current_page + 1})"
            try:
                driver.execute_script(js)
            except:
                login_action(search_url)
            waitfor(True)
            waitTime = 0  # wait reload time
            while driver.current_url == old_url and waitTime <= 5:
                waitfor(False)
                waitTime += 1
                print("long page:", driver.current_url)
        current_page += 1


def main():
    all_cates = IC_stock_excel_read.get_cate_name_arr('/Users/liuhe/PycharmProjects/SeleniumDemo/IC_Search/T0815.xlsx',
                                                      'left', 1)
    cate_ids = all_cates[1:100]
    for (cate_index, cate_name) in enumerate(cate_ids):
        get_stock(cate_index, cate_name)


def test_eager():
    driver.get('https://octopart.com/search?q=LM317DCY&currency=USD&specs=0')


if __name__ == "__main__":
    driver.get("https://member.ic.net.cn/login.php")
    login_action("https://member.ic.net.cn/member/member_index.php")
    main()


#  记录Task 提供的型号，在IC 中的库存信息
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
import undetected_chromedriver as uc
# import ssl
from IC_stock.IC_Stock_Info import IC_Stock_Info
from Manager import AccountMange
from WRTools import IPHelper, UserAgentHelper, ExcelHelp, WaitHelp, PathHelp

# ssl._create_default_https_context = ssl._create_unverified_context

sourceFile_dic = {'fileName': PathHelp.get_file_path("TInfenion_30H", 'TInfenion_30H.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 100}   #

result_file = PathHelp.get_file_path(super_path="TInfenion_30H", file_name='IC_stock.xlsx')

total_page = 1

current_page = 1
VerificationCodePage = 0
# accouts_arr = [["18571227953", "Yjcx123"]]
accouts_arr = [[AccountMange.IC_stock['n'], AccountMange.IC_stock['p']]]
# driver_option = webdriver.ChromeOptions()
# driver_option.add_argument(f'--proxy-server=http://{IPHelper.getRandowCityIP()}')
# driver_option.add_argument("–incognito")
# #  等待初始HTML文档完全加载和解析，
# driver_option.page_load_strategy = 'eager'
# driver_option.add_argument(f'user-agent="{UserAgentHelper.getRandowUA_Mac()}"')
# prefs = {"profile.managed_default_content_settings.images": 2}
# driver_option.add_experimental_option('prefs', prefs)
try:
    driver = uc.Chrome(use_subprocess=True)
    driver.set_page_load_timeout(1000)
except Exception as e:
    print(e)


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
        elif driver.current_url.startswith('https://www.ic.net.cn/search'): # 查询过程中出现登录
            driver.get(aim_url)
        WaitHelp.waitfor_octopart(False, False)


# 转换cate 中的特殊字符
def get_url(cate: str) -> str:
    cate_str = str(cate)
    cate_str = cate_str.replace('/', '%2F')
    cate_str = cate_str.replace('#', '%23')
    cate_str = cate_str.replace('+', '%2B')
    cate_str = cate_str.replace(',', '%2C')
    return f"https://www.ic.net.cn/search/{cate_str}.html"


#   二维数组，page 列表， table 列表
def get_stock(cate_index, cate_name):
    global current_page
    search_url = get_url(cate_name)
    driver.get(search_url)
    login_action(search_url)
    # 延时几秒确保页面加载完毕
    WaitHelp.waitfor_account_import(False, False)
    checkVerificationCodePage()
    # page_content = driver.page_source
    # print("page content is：", page_content)
    get_total_page()
    print(f"index is: {cate_index} cate is:{cate_name} currentPage is: {current_page} totalpage is:{total_page}")
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
        ExcelHelp.add_arr_to_sheet(file_name=result_file, sheet_name=sheet_name_base64str,
                                   dim_arr=need_save_ic_arr)
        # 包含>=3个无效的stock信息就不翻页了
        if current_page >= 2 or len(need_save_ic_arr) <= 46:
            need_load_nextPage = False
        need_save_ic_arr.clear()
        # 翻页
        if need_load_nextPage:
            old_url = driver.current_url
            if current_page < total_page:
                js = f"javascript:pageTo({current_page + 1})"
                try:
                    driver.execute_script(js)
                except:
                    login_action(search_url)
                WaitHelp.waitfor_account_import(True, False)
                waitTime = 0  # wait reload time
                while driver.current_url == old_url and waitTime <= 5:
                    WaitHelp.waitfor_account_import(False, False)
                    waitTime += 1
                    print("long page:", driver.current_url)
            current_page += 1


# 验证当前页面是否正在等待用户验证，连续三次请求出现验证码页面，则关闭页面
def checkVerificationCodePage():
    global VerificationCodePage
    if driver.current_url == 'https://www.ic.net.cn/searchPnCode.php':
        VerificationCodePage += 1
    else:
        VerificationCodePage = 0
    if VerificationCodePage >= 3:
        driver.close()


def main():
    all_cates = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    for (cate_index, cate_name) in enumerate(all_cates):
        if cate_name.__contains__('?'):
            continue
        elif cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            get_stock(cate_index, cate_name)


if __name__ == "__main__":
    driver.get("https://member.ic.net.cn/login.php")
    login_action("https://member.ic.net.cn/member/member_index.php")
    main()


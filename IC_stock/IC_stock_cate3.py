
#  记录Task 提供的型号，在IC 中的库存信息
import time
from selenium.webdriver.common.by import By
import random
from WRTools import ChromeDriverManager
import ssl
from IC_stock.IC_Stock_Info import IC_Stock_Info
from Manager import AccManage, URLManager
from WRTools import ExcelHelp, WaitHelp, PathHelp, EmailHelper, MySqlHelp_recommanded


ssl._create_default_https_context = ssl._create_unverified_context


sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TInfenionMos.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 136,
                  'endIndex': 140}
task_name = 'TInfenionMos'


accouts_arr = [AccManage.IC_stock_3['n'], AccManage.IC_stock_3['p']]
turn_page = False # 是否需要翻页
try:
    driver = ChromeDriverManager.getWebDriver(3)
except Exception as e:
    print(e)

total_page = 1
current_page = 1
VerificationCodePage = 0
finishedPPN = 0

def get_total_page():
    global total_page
    global current_page
    total_page = 1
    try:
        li_arr = driver.find_element(by=By.CLASS_NAME, value="pagepicker").find_elements(by=By.TAG_NAME, value='li')
        if total_page is not None and len(li_arr) > 0:
            total_page = int(li_arr[len(li_arr) - 1].text)
    except:
        total_page = 1
    current_page = 1


def login_action(aim_url):
    current_url = driver.current_url
    if current_url == "https://member.ic.net.cn/login.php":
        WaitHelp.waitfor_account_import(False, False)
        # begin login
        accout_current = accouts_arr
        driver.find_element(by=By.ID, value='username').clear()
        driver.find_element(by=By.ID, value='username').send_keys(accout_current[0])
        driver.find_element(by=By.ID, value='password').clear()
        driver.find_element(by=By.ID, value='password').send_keys(accout_current[1])
        WaitHelp.waitfor_account_import(False, False)
        driver.find_element(by=By.ID, value='btn_login').click()
        WaitHelp.waitfor_ICHot(True, False)
    if driver.current_url.startswith('https://member.ic.net'):  # 首次登录
        driver.get(aim_url)
    elif driver.current_url.startswith('https://www.ic.net.cn/search'):  # 查询过程中出现登录
        driver.get(aim_url)


#   二维数组，page 列表， table 列表
def get_stock(cate_index, cate_name, st_manu):
    global current_page
    search_url = URLManager.IC_stock_url(cate_name, False)
    login_action(search_url)
    # 延时几秒确保页面加载完毕
    WaitHelp.waitfor_ICHot(True, False)
    showingCheckCode = checkVerificationCodePage(cate_name)
    while showingCheckCode:
        WaitHelp.waitfor(True, False)
        showingCheckCode = checkVerificationCodePage(cate_name)
    get_total_page()
    print(f"index is: {cate_index} cate is:{cate_name} currentPage is: {current_page} totalpage is:{total_page}")
    #  2-loop page arr
    need_load_nextPage = True
    while current_page <= total_page and need_load_nextPage:
        try:
            li_arr = driver.find_element(by=By.ID, value='resultList').find_elements(by=By.CSS_SELECTOR, value='li.stair_tr')
        except:
            li_arr = []
        need_save_ic_arr = []
        #  3-loop table arr
        for templi in li_arr:
            if not templi.is_displayed():
                continue
            # print("li is:", templi.__str__())
            try:
                suppliers = templi.find_elements(by=By.CSS_SELECTOR, value='a.result_goCompany')
                for temp_suppler in suppliers:
                    if temp_suppler.text.__len__() > 0:
                        supplier = temp_suppler.text
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
                isYouXian = (templi.find_element(by=By.CLASS_NAME, value='icon_youXian') is not None)
            except:
                isYouXian = False
            try:
                manufacturer = templi.find_element(by=By.CLASS_NAME, value='result_factory').text
            except:
                manufacturer = '--'
            try:
                batch = str(templi.find_element(by=By.CLASS_NAME, value='result_batchNumber').text)
            except:
                batch = ''
            try:
                pakaging = templi.find_element(by=By.CLASS_NAME, value='result_pakaging').text  #result_pakaging
            except:
                pakaging = ''
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
            #`ppn`, `st_manu`, `supplier_manu`, `supplier`, `isICCP`, `isSSCP`, `iSRanking`, `isHotSell`, `isYouXian`, `batch`, `pakaging`, `stock_num`
            ic_Stock_Info = IC_Stock_Info(supplier=supplier,
                                          isICCP=isICCP,
                                          isSSCP=isSSCP,
                                          model=cate_name,
                                          st_manu=st_manu,
                                          isSpotRanking=isSpotRanking,
                                          isHotSell=isHotSell,
                                          isYouXian=isYouXian,
                                          batch=batch,
                                          pakaging=pakaging,
                                          supplier_ppn=model,
                                          supplier_manu=manufacturer,
                                          stock_num=stock_num)
            if ic_Stock_Info.shouldSave():
                saveContent_arr = ic_Stock_Info.descritpion_arr() + [task_name]
                need_save_ic_arr.append(saveContent_arr)
        if need_save_ic_arr.__len__() > 0:
            # print(need_save_ic_arr)
            MySqlHelp_recommanded.DBRecommandChip().ic_stock(need_save_ic_arr)
        # 包含>=3个无效的stock信息就不翻页了
        if not(turn_page and current_page <2 and need_save_ic_arr.__len__ > 46):
            need_load_nextPage = False
        if need_load_nextPage:
            if current_page < total_page:
                go_to_nex_page(cate_name)


def go_to_nex_page(cate_name):
    global current_page
    new_url = URLManager.IC_stock_url(cate_name, False, current_page + 1)
    driver.get(new_url)
    WaitHelp.waitfor_ICHot(True, False)
    waitTime = 0  # wait reload time
    while driver.current_url != new_url and waitTime <= 5:
        waitTime += 1
        print(f"url is:{new_url} load error:")
        driver.get(new_url)
        WaitHelp.waitfor(True, False)
    current_page += 1



# 验证当前页面是否正在等待用户验证，连续三次请求出现验证码页面，则关闭页面
def checkVerificationCodePage(ppn) -> bool:
    global VerificationCodePage
    if driver.current_url == 'https://www.ic.net.cn/searchPnCode.php?l=ins':
        VerificationCodePage += 1
        print(f'{ppn} check code')
        EmailHelper.mail_IC_Stock(AccManage.Device_ID)
        result = True
    else:
        VerificationCodePage = 0
        result = False
    if VerificationCodePage >= 30:
        driver.close()
    return result


def changeAccount():
    global finishedPPN
    if finishedPPN > 0:
        if finishedPPN % 66 == 0:
            driver.close()
            time.sleep(1.0)
            ChromeDriverManager.getWebDriver(2)
            time.sleep(1.0)
            driver.get('https://www.ic.net.cn/')
            time.sleep(2.0)
            login_action("https://member.ic.net.cn/member/member_index.php")
    finishedPPN += 1


def main():
    all_cates = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'], 2)
    for (cate_index, cate_name) in enumerate(all_cates):
        while WaitHelp.isSleep_time():
                time.sleep(60*5)
        if cate_name.__contains__('?'):
            continue
        elif cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
            if cate_index % 7 == 0:
                time.sleep(60*5)
            # changeAccount()
            get_stock(cate_index, cate_name, all_manu[cate_index])


if __name__ == "__main__":
    driver.get('https://www.ic.net.cn/')
    time.sleep(2.0)
    driver.get("https://member.ic.net.cn/login.php")
    time.sleep(1.5)
    login_action("https://member.ic.net.cn/member/member_index.php")
    main()

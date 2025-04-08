
#  记录Task 提供的型号，在IC 中的库存信息
import time
from selenium.webdriver.common.by import By
from WRTools import ChromeDriverManager
import ssl
from IC_stock.IC_Stock_Info import IC_Stock_Info
from Manager import AccManage, URLManager
from WRTools import ExcelHelp, WaitHelp, PathHelp, EmailHelper, MySqlHelp_monitor
import random


ssl._create_default_https_context = ssl._create_unverified_context

sourceFile_dic = {'fileName': PathHelp.get_file_path("Monitor", 'TFL_ICStock.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 6,
                  'endIndex': 12}

accouts_arr = [[AccManage.IC_stock_2['n'], AccManage.IC_stock_2['p']]]
try:
    driver = ChromeDriverManager.getWebDriver(0)
except Exception as e:
    print(e)

total_page = 1
current_page = 1
VerificationCodePage = 0
ignore_list = ['967067-1', 'HFW4A1201K00', 'PI3301-00-LGIZ']


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
        accout_current = accouts_arr[0]
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
    search_url = URLManager.IC_stock_url(cate_name, precise=True)
    login_action(search_url)
    # 延时几秒确保页面加载完毕
    WaitHelp.waitfor_ICHot(True, False)
    showingCheckCode = checkVerificationCodePage(cate_name)
    while showingCheckCode:
        WaitHelp.waitfor(True, False)
        showingCheckCode = checkVerificationCodePage(cate_name)
    get_total_page()
    stored_supplier = []  # 该型号已经添加过的供应商
    print(f"index is: {cate_index} cate is:{cate_name} currentPage is: {current_page} totalpage is:{total_page}")
    #  2-loop page arr
    need_load_nextPage = True
    need_save_ic_arr = []
    while current_page <= total_page and need_load_nextPage:
        try:
            li_arr = driver.find_element(by=By.ID, value='resultList').find_elements(by=By.CSS_SELECTOR, value='li.stair_tr')
        except:
            li_arr = []
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
            #'ppn', 'st_manu', 'supplier_manu', 'supplier', 'isICCP', 'isSSCP', 'iSRanking', 'isHotSell', 'isYouXian', 'batch', 'pakaging', 'stock_num'
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
                saveContent_arr = ic_Stock_Info.descritpion_arr_fl()
                if not stored_supplier.__contains__(supplier):
                    need_save_ic_arr.append(saveContent_arr)
                    stored_supplier.append(supplier)
        gotoNextPage(cate_name)
    return need_save_ic_arr


def gotoNextPage(cate_name):
    global current_page, total_page
    if current_page < total_page:
        new_url = URLManager.IC_stock_url(cate_name, True, current_page+1)
        driver.get(new_url)
        WaitHelp.waitfor_ICHot(True, False)
        waitTime = 0  # wait reload time
        while driver.current_url != new_url and waitTime <= 5:
            waitTime += 1
            print(f"url is:{new_url} load error:")
            print(f"current url is :{driver.current_url}")
            driver.get(new_url)
            WaitHelp.waitfor(True, False)
    current_page += 1


def stock_change_alert(ppn_list):
    print('todo') # //TODO wr


# 验证当前页面是否正在等待用户验证，连续三次请求出现验证码页面，则关闭页面
def checkVerificationCodePage(ppn) -> bool:
    global VerificationCodePage
    if driver.current_url.__contains__("searchPnCode"):
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


def main():
    db_manager = MySqlHelp_monitor.MonitorDatabaseManager()
    # 创建连接
    all_cates = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'], 2)
    try:
        for (cate_index, cate_name) in enumerate(all_cates):
            while WaitHelp.isSleep_time():
                    time.sleep(60*5)
            if cate_name.__contains__('?'):
                continue
            elif ignore_list.__contains__(cate_name):  # 已卖完，或者供应商太多无需关注
                continue
            elif cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
                print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
                need_save_ic_arr = get_stock(cate_index, cate_name, all_manu[cate_index])
                try:
                    db_manager.create_connection()
                    db_manager.insert_monitor_ics(need_save_ic_arr)
                finally:
                    db_manager.close_connection()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    driver.get('https://www.ic.net.cn/')
    time.sleep(2.5 + random.uniform(1, 10))
    driver.get("https://member.ic.net.cn/login.php")
    time.sleep(2.5 + random.uniform(1, 10))
    login_action("https://member.ic.net.cn/member/member_index.php")
    main()


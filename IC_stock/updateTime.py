
#  记录Task 提供的型号，在IC 中的库存信息
import time
from selenium.webdriver.common.by import By
import random
from WRTools import ChromeDriverManager
import ssl
from IC_stock.IC_Stock_Info import IC_Stock_Info
from Manager import AccManage, URLManager
from WRTools import ExcelHelp, WaitHelp, PathHelp, EmailHelper


ssl._create_default_https_context = ssl._create_unverified_context

sourceFile_dic = {'fileName': PathHelp.get_file_path("IC_stock", 'TFL_ICUpdate.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 2}
task_name = 'TFL_ICUpdate'

accouts_arr = [[AccManage.IC_hot['n'], AccManage.IC_hot['p']]]
try:
    driver = ChromeDriverManager.getWebDriver(1)
except Exception as e:
    print(e)

total_page = 1
current_page = 1
VerificationCodePage = 0


def get_total_page():
    global total_page
    global current_page
    total_page = 1
    # try:
    #     li_arr = driver.find_element(by=By.CLASS_NAME, value="pagepicker").find_elements(by=By.TAG_NAME, value='li')
    #     if total_page is not None and len(li_arr) > 0:
    #         total_page = int(li_arr[len(li_arr) - 1].text)
    # except:
    #     total_page = 1
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
    time.sleep(5*60)
    showingCheckCode = checkVerificationCodePage(cate_name)
    while showingCheckCode:
        WaitHelp.waitfor(True, False)
        showingCheckCode = checkVerificationCodePage(cate_name)
    get_total_page()
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
                isSpotRanking = (templi.find_element(by=By.CLASS_NAME, value='icon_xianHuo') is not None)
            except:
                isSpotRanking = False
            if isSpotRanking:
                need_save_ic_arr.append(supplier)
        gotoNextPage(cate_name)
    if need_save_ic_arr.__len__() > 0:
        writeRecord(need_save_ic_arr, cate_name)
        need_save_ic_arr.clear()


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
            driver.get(new_url)
            WaitHelp.waitfor(True, False)
    current_page += 1


def writeRecord(need_save_arr, ppn):
    file_name = sourceFile_dic['fileName']
    sheet = ppn[0:5]
    result = need_save_arr
    title = time.strftime("%H:%M", time.localtime())
    result.insert(0, title)
    ExcelHelp.add_arr_to_sheet(file_name, sheet, [result])
    time.sleep(1.0)


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


def main():
    all_cates = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'], 2)
    while True:
        for (cate_index, cate_name) in enumerate(all_cates):
            while WaitHelp.isSleep_time():
                time.sleep(60 * 5)
            if cate_name.__contains__('?'):
                continue
            elif cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
                print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
                get_stock(cate_index, cate_name, all_manu[cate_index])


if __name__ == "__main__":
    driver.get('https://www.ic.net.cn/')
    time.sleep(2.0)
    driver.get("https://member.ic.net.cn/login.php")
    time.sleep(1.5)
    login_action("https://member.ic.net.cn/member/member_index.php")
    main()

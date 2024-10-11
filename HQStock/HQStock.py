import time

from WRTools import ExcelHelp, WaitHelp, PathHelp, MySqlHelp_recommanded, ChromeDriverManager, EmailHelper
from selenium.webdriver.common.by import By
import ssl
from Manager import AccManage, URLManager

log_file = PathHelp.get_file_path('HQSearch', 'HQPeakfireLog.txt')
ssl._create_default_https_context = ssl._create_unverified_context

sourceFile_dic = {'fileName': PathHelp.get_file_path('TradeWebs', 'ICShop.xlsx'),
                  'sourceSheet': 'ppn2',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 30}
task_name = 'ICShops'

accouts_arr = [AccManage.HQ_hot_1['n'], AccManage.HQ_hot_1['p']]
VerificationCodePage = 0
login_url = "https://passport.hqew.com/login"

driver = ChromeDriverManager.getWebDriver(1)
driver.set_window_size(height=800, width=1200)
current_cate_has_date = True


def login_action(aim_url):
    driver.get(login_url)
    if aim_url.__contains__(login_url):
        WaitHelp.waitfor_ICHot(False, False)
        # begin login
        driver.find_element(by=By.ID, value='J_loginName').clear()
        driver.find_element(by=By.ID, value='J_loginName').send_keys(accouts_arr[0])
        driver.find_element(by=By.ID, value='J_loginPsw').clear()
        driver.find_element(by=By.ID, value='J_loginPsw').send_keys(accouts_arr[1])
        WaitHelp.waitfor_ICHot(False, False)
        driver.find_element(By.ID, value='J_checkpripolicy_account').click() # 协议
        time.sleep(2.0)
        driver.find_element(by=By.ID, value='J_btnLogin').click()
        WaitHelp.waitfor(True, False)


# 验证当前页面是否正在等待用户验证，连续三次请求出现验证码页面，则关闭页面
def checkVerificationCodePage(ppn) -> bool:
    global VerificationCodePage
    if driver.current_url.__contains__('https://passport.hqew.com/robottocheck'):
        VerificationCodePage += 1
        print(f'{ppn} check code')
        EmailHelper.mail_HQ_hot(AccManage.Device_ID)
        result = True
    else:
        VerificationCodePage = 0
        result = False
    if VerificationCodePage >= 20:
        driver.close()
    return result


# def has_hotData() -> bool:
#     nodatas_areas = driver.find_elements(By.CSS_SELECTOR, 'div.no-data')
#     if nodatas_areas.__len__() > 0:
#         return False
#     return True


# 获取单个型号库存info
def getSearchInfo(cate_name, manu, isWeek):
    result = []
    tables = driver.find_elements(By.CSS_SELECTOR, 'table.list-table')
    if tables.__len__() > 0:
        info_table = tables[1]
        tr_arr = info_table.find_elements(By.TAG_NAME, 'tr')
        for (index, tr_info) in enumerate(tr_arr):
            yzpms = tr_info.find_elements(By.CSS_SELECTOR, 'a.icon-yzpm')
            yzs = tr_info.find_elements(By.CSS_SELECTOR, 'a.i-yuan')
            if yzpms.__len__() > 0 or yzs.__len__() > 0:
                row_info = get_saveInfo(cate_name, manu, tr_info)
                if row_info.__len__() > 0:
                    result.append(row_info)
    return result


# ppn, std_manu, supplier, sup_manu, batch, stock, packing, param, place, instruction, publish_date, task_name
def get_saveInfo(ppn, manu, tr):
    try:
        supplier_name = tr.find_element(By.CSS_SELECTOR, 'a.company.company-cinfo-click').text
    except:
        supplier_name = ''
    try:
        sup_manu = tr.find_element(By.CSS_SELECTOR, 'td.td-brand').text
    except:
        sup_manu = ''
    try:
        batch = tr.find_element(By.CSS_SELECTOR, 'td.td-pproductDate').text
    except:
        batch = ''
    try:
        stock_tr = tr.find_element(By.CSS_SELECTOR, 'td.td-stockNum')
        stock = stock_tr.find_element(By.TAG_NAME, 'p').text
    except:
        stock = ''
    try:
        packing = tr.find_element(By.CSS_SELECTOR, 'td.td-ppackage').text
    except:
        packing = ''
    try:
        param = tr.find_element(By.CSS_SELECTOR, 'td.td-param').text
    except:
        param = ''
    try:
        place = tr.find_element(By.CSS_SELECTOR, 'td.td-storeLocation').text
    except:
        place = ''
    try:
        instruction = tr.find_element(By.CSS_SELECTOR, 'td.td-premark').text
    except:
        instruction = ''
    try:
        publish_date = tr.find_elements(By.TAG_NAME, 'td')[-2].text
    except:
        publish_date = ''
    result = [ppn, manu, supplier_name, sup_manu, batch, stock, packing, param, place, instruction, publish_date, task_name]
    return result


# 查询列表中所有需要查询的型号的搜索指数
def main():
    all_cates = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'], 2)
    for (index, ppn) in enumerate(all_cates):
        if ppn.__contains__('?'):
            continue
        elif index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {index}  cate_name is: {ppn}')
            manu = all_manu[index]
            driver.get(URLManager.HQ_stock_url(ppn))
            if index > 0 and index % 13 == 0:
                time.sleep(10*60)
            else:
                WaitHelp.waitfor(True, False)
            showingCheckCode = checkVerificationCodePage(ppn)
            while showingCheckCode:
                WaitHelp.waitfor(True, False)
                showingCheckCode = checkVerificationCodePage(ppn)
            supplier_info_arr = getSearchInfo(ppn, manu, True)
            if supplier_info_arr.__len__() > 0:
                MySqlHelp_recommanded.DBRecommandChip().hq_stock_write(supplier_info_arr)
            else:
                print(f"{ppn} without data")


if __name__ == "__main__":
    driver.get("https://www.hqew.com/")
    login_action(login_url)
    main()


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

sourceFile_dic = {'fileName': PathHelp.get_file_path("IC_stock", 'TFL_ICStock.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 10}
task_name = 'TFL_ICStock'

accouts_arr = [[AccManage.IC_FLStock['n'], AccManage.IC_FLStock['p']]]
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
    stored_supplier = []
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
    if need_save_ic_arr.__len__() > 0:
        writeRecord(need_save_ic_arr, cate_name, st_manu)
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
            print(f"current url is :{driver.current_url}")
            driver.get(new_url)
            WaitHelp.waitfor(True, False)
    current_page += 1


def writeRecord(need_save_arr, ppn, st_manu):
    file_name = sourceFile_dic['fileName']
    sheet = ppn[0:5]
    try:
        history = ExcelHelp.read_sheet_content_by_name(file_name, sheet)
    except:
        history = []
    result = []
    # (ppn, st_manu, supplier_manu, supplier, stock_num)
    if history.__len__() > 0:
        his_stock_record = history[1].__len__() - 5 #5条项本信息
        title_row = history[0] + [time.strftime('%Y-%m-%d', time.localtime())]
    else:
        # (ppn, st_manu, supplier_manu, supplier, stock_num)
        title_row = ['ppn', 'st_manu', 'supplier_manu', 'supplier'] + [time.strftime('%Y-%m-%d', time.localtime())]
        his_stock_record = 0
    result.append(title_row)
    history_sup_names = ExcelHelp.read_col_content(file_name, sheet, 4)
    now_sup_names = []
    for now_supplier in need_save_arr:
        now_sup_name = now_supplier[3]
        now_sup_names.append(now_sup_name)
        if now_sup_name in history_sup_names: #以前有货，现在还有货
            index = history_sup_names.index(now_sup_name)
            new_row = history[index] + [now_supplier[-1]]
        else: #以前没货，现在有货
            new_row = now_supplier[:-1] + ['0'] * his_stock_record + now_supplier[-1:]
        result.append(new_row)
    #以前有货，现在没货
    for (index, temp_his) in enumerate(history):
        if index > 0:
            if not now_sup_names.__contains__(temp_his[3]):
                new_row = temp_his + ["0"]
                result.append(new_row)
    ExcelHelp.delete_sheet_content(file_name, sheet)
    time.sleep(1.0)
    ExcelHelp.add_arr_to_sheet(file_name, sheet, result)


def stock_change_alert(ppn_list):
    file_name = sourceFile_dic['fileName']
    history = []
    ignore_list = ["MPXM2202AS", "TPS22810DRVR"]
    for temp_ppn in ppn_list:
        if ignore_list.__contains__(temp_ppn):     # 已卖完，或者供应商太多无需关注
            continue
        sheet_content = ExcelHelp.read_sheet_content_by_name(file_name, temp_ppn[0:5])
        history += sheet_content
    alert_info = []
    if history[0].__len__() > 3:
        for temp_record in history:
            try:
                last_stock = int(temp_record[-2])
            except:
                last_stock = 0
            try:
                new_stock = int(temp_record[-1])
            except:
                new_stock = 0
            if last_stock != new_stock:
                one_info = [temp_record[0], temp_record[3], temp_record[-2], temp_record[-1]]
                alert_info.append(one_info)
    if alert_info.__len__() > 0:
        result = '<table >'
        for index, temp_row in enumerate(alert_info):
            row_str = '<tr style="background-color: lightgray;">' if index % 2 == 0 else '<tr>'
            for temp_cell in temp_row:
               row_str += f'<td style="padding: 8px; border-right: 1px solid;">{temp_cell}</td>'
            row_str += '</tr>'
            result += row_str
        result += '</table>'
        alert_str = result # '<br>'.join([', '.join(sublist) for sublist in alert_info])
        EmailHelper.stock_chang_alert(file_name, str(alert_str))


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
    all_cates = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'], 2)
    for (cate_index, cate_name) in enumerate(all_cates):
        # while WaitHelp.isSleep_time():
        #         time.sleep(60*5)
        if cate_name.__contains__('?'):
            continue
        elif cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
            get_stock(cate_index, cate_name, all_manu[cate_index])
    stock_change_alert(all_cates)


if __name__ == "__main__":
    driver.get('https://www.ic.net.cn/')
    time.sleep(2.0)
    driver.get("https://member.ic.net.cn/login.php")
    time.sleep(1.5)
    login_action("https://member.ic.net.cn/member/member_index.php")
    main()


#  记录Task 提供的型号，在IC 中的库存信息
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import random
from WRTools import ChromeDriverManager
import ssl
from Manager import AccManage, URLManager
from WRTools import ExcelHelp, WaitHelp, PathHelp, EmailHelper, MySqlHelp_monitor


ssl._create_default_https_context = ssl._create_unverified_context


sourceFile_dic = {'fileName': PathHelp.get_file_path('Monitor', 'IC_supplier_list.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 7,
                  'endIndex': 9}
task_name = ''

accouts_arr = [AccManage.IC_stock_3['n'], AccManage.IC_stock_3['p']]
try:
    driver = ChromeDriverManager.getWebDriver(1)
except Exception as e:
    print(e)

VerificationCodePage = 0


def login_action(aim_url):
    current_url = driver.current_url
    if current_url == "https://member.ic.net.cn/login.php":
        WaitHelp.waitfor_account_import(False, False)
        # begin login
        accout_current = accouts_arr
        driver.find_element(by=By.ID, value='username').clear()
        driver.find_element(by=By.ID, value='username').send_keys(accout_current[0])
        time.sleep(5.0)
        driver.find_element(by=By.ID, value='password').clear()
        driver.find_element(by=By.ID, value='password').send_keys(accout_current[1])
        time.sleep(5.0)
        time.sleep(7.5 + random.uniform(1, 5))
        driver.find_element(by=By.ID, value='btn_login').click()
        time.sleep(9.5 + random.uniform(1, 5))
    else:
        driver.get(aim_url)


#   二维数组，page 列表， table 列表
def get_supplier_info(cate_index, cate_name):
    search_url = URLManager.IC_stock_url(cate_name, False)
    driver.get(search_url)
    # 延时几秒确保页面加载完毕
    WaitHelp.waitfor_ICHot(True, False)
    showingCheckCode = checkVerificationCodePage(cate_name)
    while showingCheckCode:
        WaitHelp.waitfor(True, False)
        showingCheckCode = checkVerificationCodePage(cate_name)
    if True:
        try:
            li_arr = driver.find_element(by=By.ID, value='resultList').find_elements(by=By.CSS_SELECTOR, value='li.stair_tr')
        except:
            li_arr = []
        page_info = []
        #  3-loop table arr
        for (index, templi) in enumerate(li_arr):
            # 使用 JavaScript 滚动到该元素
            driver.execute_script("arguments[0].scrollIntoView();", templi)
            if index > 2:
                name = age = address = hot = qq = tel = phone = ''
                company_name_index = 0
                try:
                    name_list = templi.find_elements(By.CSS_SELECTOR, 'a.result_goCompany')
                    for (supplier_index, temp_suppler) in enumerate(name_list):
                        if temp_suppler.text.__len__() > 0:
                            company_name_index = supplier_index
                            name = temp_suppler.text
                except:
                    print('get name error')
                    continue
                try:
                    # 创建一个ActionChains对象
                    action = ActionChains(driver)
                    # 模拟鼠标移动到目标元素上
                    action.move_to_element(name_list[company_name_index]).perform()
                except:
                    print('show detail error')
                    continue
                time.sleep(4.0)
                # (name, age, address, hot, qq, tel, phone)
                border_left = templi.find_element(By.CSS_SELECTOR, 'div.layer_border').find_element(By.CSS_SELECTOR, 'div.layer_left')
                try:
                    age = border_left.find_element(By.CSS_SELECTOR, 'div.layer_line1').find_elements(By.TAG_NAME, 'span')[-1].text
                    address = border_left.find_elements(By.CSS_SELECTOR, 'div.floatNo')[1].text.replace("地址：", '')
                    hot = '' # todo border_left.find_element()
                    tel = border_left.find_element(By.CSS_SELECTOR, 'div.layer_line2').text.replace("电话：", '')
                    phone = border_left.find_element(By.CSS_SELECTOR, 'div.layer_line').text.replace("手机：", '')
                except Exception as e:
                    print(f'get address error {e}')
                supplier_info = [name, age, address, hot, qq, tel, phone]
                if name.__len__() > 0:
                    page_info.append(supplier_info)
                    print(supplier_info)
        return page_info


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


def confuseAction(action):
    if action:
        a_item = action()
        try:
            a_item.click()
            time.sleep(8.5 + random.uniform(1, 10))
            # 关闭新页面（如果打开了新的窗口）
            if len(driver.window_handles) > 1:
                driver.close()
            # 返回初始页面（如果需要）
            driver.switch_to.window(driver.window_handles[0])
        except:
            print('confuse error')
    else:
        print('action is None')


def confuse_leftAD():
    try:
        ad1 = driver.find_element(By.ID, 'SD1').find_element(By.TAG_NAME, 'a')
        return ad1
    except:
        return None


def confuse_supplier_info():
    try:
        suppliers = driver.find_elements(By.CSS_SELECTOR, 'div.result_supply')
        if suppliers.__len__() > 0:
            last_link = suppliers[-1].find_elements(By.TAG_NAME, 'a')[-1]
            return last_link
    except:
        return None


def confuse_storePPN():
    try:
        store = driver.find_element(By.CSS_SELECTOR, 'li.iconfont.icon-aixin')
        return store
    except:
        return None


def confuse_helpCenter():
    try:
        topNav = driver.find_element(By.CSS_SELECTOR, 'div.topnav_content')
        help_center = topNav.find_elements(By.CSS_SELECTOR, 'div.fl')[-2]
        help_link = help_center.find_element(By.TAG_NAME, 'a')
        return help_link
    except:
        return None


def confuse_pilot():
    try:
        topNav = driver.find_element(By.CSS_SELECTOR, 'div.topnav_content')
        pilot_center = topNav.find_elements(By.CSS_SELECTOR, 'div.fl')[-4]
        pilot_link = pilot_center.find_element(By.TAG_NAME, 'a')
        return pilot_link
    except:
        return None


def confuse_home():
    try:
        pilot_link = driver.find_element(By.CSS_SELECTOR, 'a.icHome')
        return pilot_link
    except:
        return None


def main():
    db_manager = MySqlHelp_monitor.MonitorDatabaseManager()
    all_cates = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    for (cate_index, cate_name) in enumerate(all_cates):
        if cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
            need_save_ic_arr = get_supplier_info(cate_index, cate_name)
            try:
                db_manager.create_connection()
                db_manager.insert_ic_supplier_list(need_save_ic_arr)
            finally:
                db_manager.close_connection()


if __name__ == "__main__":
    driver.get('https://www.ic.net.cn/')
    time.sleep(2.5 + random.uniform(1, 5))
    driver.get("https://member.ic.net.cn/login.php")
    time.sleep(3.5 + random.uniform(1, 5))
    login_action("https://member.ic.net.cn/member/member_index.php")
    main()


#  rusprofiel 根据公司名称，匹配公司列表
import time

from selenium.webdriver.common.by import By
import random
import undetected_chromedriver as uc
import ssl
from IC_stock.IC_Stock_Info import IC_Stock_Info
from Manager import AccManage, URLManager
from WRTools import ExcelHelp, WaitHelp, PathHelp, MySqlHelp_recommanded, LogHelper


ssl._create_default_https_context = ssl._create_unverified_context

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, f'TNewBrand.xlsx'),
                  'sourceSheet': 'company',
                  'colIndex': 1,
                  'startIndex': 826,  #Акционерное Общество Золотые Луга
                  'endIndex': 1313}
# sourceFile_dic = {'fileName': PathHelp.get_file_path(None, f'TICHot_202401.xlsx'),
#                   'sourceSheet': 'buyer',
#                   'colIndex': 1,
#                   'startIndex': 138,  #Акционерное Общество Золотые Луга
#                   'endIndex': 142}

accouts_arr = [AccManage.rusprofile['n'], AccManage.rusprofile['p']]
default_url = 'https://www.rusprofile.ru/search-advanced'
log_file = PathHelp.get_file_path('RUSProfile', 'DJ_product_status_log.txt')

try:
    if AccManage.chromedriver_path.__len__() > 0:
        driver = uc.Chrome(use_subprocess=True,
                           driver_executable_path=AccManage.chromedriver_path)  # todo chromedriverPath
    else:
        driver = uc.Chrome(use_subprocess=True)
    driver.set_page_load_timeout(1000)
except Exception as e:
    print(e)


def isLogined():
    try:
        login_button = driver.find_element(By.ID, 'menu-personal-trigger')
        if login_button.text == 'Анастасия':
            return True
        return False
    except:
        return False


#登录
def login_action():
    if isLogined():
        return
    else:
        login_button = driver.find_element(By.ID, 'menu-personal-trigger')
        login_button.click()
        time.sleep(5.0)
        try:
            input_area = driver.find_element(By.CSS_SELECTOR, 'div.vModal-wrap-content')
            inputs = input_area.find_elements(By.CSS_SELECTOR, 'input.control-input')
            if inputs.__len__() >= 2:
                account = inputs[0]
                account.clear()
                account.send_keys(accouts_arr[0])
                pw = inputs[1]
                pw.clear()
                pw.send_keys(accouts_arr[1])
            sure_button = input_area.find_element(By.CSS_SELECTOR, 'button.btn.btn-blue')
            sure_button.click()
            time.sleep(3.0)
            WaitHelp.waitfor(True, False)
        except Exception as e:
            LogHelper.write_log(log_file, 'login error')


#   二维数组，page 列表， table 列表
def get_id(company_index, company_name):
    search_result = driver.find_element(By.ID, 'additional-results')
    companys = search_result.find_elements(By.CSS_SELECTOR, 'div.company-item')
    if companys.__len__() == 0:
        print(f'{company_name} : has no record')
        return
    for (loopIndex, temp_company) in enumerate(companys):
        if loopIndex >= 3:
            break
        # https://www.rusprofile.ru/id/1653418
        # https://www.rusprofile.ru/ip/318583500057542
        link = temp_company.find_element(By.TAG_NAME, 'a').get_attribute('href')
        if link.startswith('https://www.rusprofile.ru/id'): #不要ip 这种个体工商户
            parts = link.split('/')
            # 获取最后一个部分
            profile_id = parts[-1]
            temp_company.find_element(By.TAG_NAME, 'a').click()
            goto_detail(company_index, company_name, profile_id)


def goto_detail(company_index, company_name, profile_id):
    # detail_url = "https://www.rusprofile.ru/id/" + profile_id
    # driver.get(detail_url)
    new_tab_handle = driver.window_handles[1]
    # 切换到新打开的标签页面
    new_tab_driver = driver
    new_tab_driver.switch_to.window(new_tab_handle)

    WaitHelp.waitfor(True, False)
    full_name = inn = activity = rigister_date = industry_rank = adress = phone = email = website = revenue = profit = cost = ''
    try:
        full_name = new_tab_driver.find_element(By.CSS_SELECTOR, 'h2.company-name').text
        inn = new_tab_driver.find_element(By.ID, 'clip_inn').text
        try:
            activity = new_tab_driver.find_element(By.XPATH, '//*[@id="anketa"]/div[2]/div[2]/div[1]/span[2]').text
        except:
            activity = ''
        try:
            rigister_date = new_tab_driver.find_element(By.XPATH, '//*[@id="anketa"]/div[2]/div[1]/div[1]/div[2]/dl[1]/dd').text
        except:
            rigister_date = ''
        industry_rank = new_tab_driver.find_element(By.XPATH, '//*[@id="anketa"]/div[2]/div[2]/div[2]/span[2]').text
        adress = new_tab_driver.find_element(By.XPATH, '//*[@id="clip_address"]').text
        try:
            phone = new_tab_driver.find_element(By.XPATH, '//*[@id="contacts-row"]/div[1]/div/span[2]').text
        except:
            phone = ''
        try:
            email = new_tab_driver.find_element(By.XPATH, '//*[@id="contacts-row"]/div[2]/div/span[2]').text
        except:
            email = ''
        try:
            website = new_tab_driver.find_element(By.XPATH, '//*[@id="contacts-row"]/span[2]/span[2]').text
        except:
            website = ''
        #finalcial
        revenue1 = new_tab_driver.find_element(By.XPATH,
                                              '//*[@id="ab-test-wrp"]/div[2]/div[2]/div[1]/div/div[1]/div[1]/div[2]/span[1]').text
        revenue2 = new_tab_driver.find_element(By.XPATH,
                                              '//*[@id="ab-test-wrp"]/div[2]/div[2]/div[1]/div/div[1]/div[1]/div[2]/span[2]').text
        revenue = revenue1 + revenue2
        profit = new_tab_driver.find_element(By.XPATH, '//*[@id="ab-test-wrp"]/div[2]/div[2]/div[1]/div/div[1]/div[2]/div[2]').text
        cost = new_tab_driver.find_element(By.XPATH, '//*[@id="ab-test-wrp"]/div[2]/div[2]/div[1]/div/div[1]/div[3]/div[2]').text
        if email.__contains__('░░'):
            login_action()
            time.sleep(20.0)
            goto_detail(company_index, company_name, profile_id)
    except Exception as e:
        LogHelper.write_log(log_file, f'{company_name} goto_detail error {e}')
    task_name = 'newbrand_202401'
    # task_name = 'TICHot_202401'
    result = [company_name, profile_id, full_name, inn , activity , rigister_date , industry_rank , adress , phone , email , website , revenue , profit , cost , task_name]
    # ExcelHelp.add_arr_to_sheet(sourceFile_dic['fileName'], 'rusprofile', [result])
    MySqlHelp_recommanded.DBRecommandChip().rusprofile_write([result])
    # 关闭当前的页面
    new_tab_driver.close()
    # 切换回列表页面
    new_tab_driver.switch_to.window(driver.window_handles[0])


# 将company 那么作为搜索关键字，进行搜索
def send_companyName_to_filter(company_index, company_name):
    input_area = driver.find_element(By.ID, 'advanced-search-query')
    input_area.clear()
    input_area.send_keys(company_name)
    if company_index % 15 == 0 and company_index > 0:
        time.sleep(60*8)
    else:
        WaitHelp.waitfor_account_import(True, False)
    get_id(company_index, company_name)
    

def main():
    print('start search')
    all_companys = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    for (company_index, company_name) in enumerate(all_companys):
        if company_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'{company_index} -- {company_name} :')
            send_companyName_to_filter(company_index, company_name)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor(True, False)
    login_action()
    #todo set filter
    main()

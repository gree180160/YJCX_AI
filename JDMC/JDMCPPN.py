# 获取京满仓的ppn，库存
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
import undetected_chromedriver as uc
import ssl
from WRTools import IPHelper, UserAgentHelper, ExcelHelp, WaitHelp, PathHelp, LogHelper

ssl._create_default_https_context = ssl._create_unverified_context

sourceFile = PathHelp.get_file_path(None, 'TJDMC.xlsx')
logFile = PathHelp.get_file_path('JDMC', 'JDMCLog.txt')
login_url = 'https://www.vipmro.net/login'
total_page = 1
current_page = 1
accouts_arr = ['englishmaster2010', 'Oliver12345!']
driver_option = webdriver.ChromeOptions()
driver_option.add_argument(f'--proxy-server=http://{IPHelper.getRandowCityIP()}')
driver_option.add_argument("–incognito")
#  等待初始HTML文档完全加载和解析，
driver_option.page_load_strategy = 'eager'
driver_option.add_argument(f'user-agent="{UserAgentHelper.getRandowUA_Mac()}"')
prefs = {"profile.managed_default_content_settings.images": 2}
driver_option.add_experimental_option('prefs', prefs)
driver = uc.Chrome(use_subprocess=True)
driver.set_page_load_timeout(1000)


# 通过计算获得产品列表的页面url
def get_urls() -> list:
    munuids = ExcelHelp.read_col_content(file_name=sourceFile, sheet_name='manu', col_index=2)
    result = []
    for tempManu in munuids:
        if tempManu:
            url = f'https://www.vipmro.net/searchModel/c-50/{tempManu}?advantage=0'
            result.append([url])
    return result


# 通过manuID 获得manu name
def get_manuName(manu_id):
    manuids = ExcelHelp.read_col_content(file_name=sourceFile, sheet_name='manu', col_index=2)
    manuNames = ExcelHelp.read_col_content(file_name=sourceFile, sheet_name='manu', col_index=1)
    index = manuids.index(manu_id)
    return manuNames[index]

# 登陆
def loginAction(aim_url):
    current_url = driver.current_url
    # if current_url.startswith(login_url):
    #     WaitHelp.waitfor_account_import(False, False)
    #     # begin login
    #     accout_current = random.choice(accouts_arr)
    #     driver.find_element(by=By.ID, value='loginname').clear()
    #     driver.find_element(by=By.ID, value='loginname').send_keys(accout_current[0])
    #     WaitHelp.waitfor_account_import(False, False)
    #     driver.find_element(by=By.ID, value='nloginpwd').clear()
    #     driver.find_element(by=By.ID, value='nloginpwd').send_keys(accout_current[1])
    #     WaitHelp.waitfor_account_import(False, False)
    #     driver.find_element(by=By.ID, value='paipaiLoginSubmit').click()
    #     WaitHelp.waitfor_account_import(True, False)
    #     time.sleep(10)
    # if not driver.current_url.startswith('https://www.vipmro.net/searchModel/'):
    #     driver.get(aim_url)
    WaitHelp.waitfor_account_import(True, False)


# 获取总页数
def get_total_page():
    global total_page
    global current_page
    total_page = 1
    try:
        page_div = driver.find_element(by=By.CSS_SELECTOR, value="div.t-page.fr")
        right = page_div.find_element(by=By.CSS_SELECTOR, value="em.p-right15.J_page_sum")
        if right:
            total_page = int(right.text)
    except:
        total_page = 1
    current_page = 1


# go 下一页
def goToNextPage():
    global current_page
    current_url = driver.current_url
    new_url = current_url.replace(f'p-{current_page}', f'p-{current_page+1}')
    driver.get(new_url)
    WaitHelp.waitfor(True, False)
    current_page += 1


# 分析html 文件
def anly_webdriver(url_index, url_value):
    global current_page
    url_part_arr = url_value.split('/')
    manuID = url_part_arr[5]
    manuName = get_manuName(manuID)
    get_total_page()
    while current_page <= total_page:
        print(f'index is:{url_index} url is:{url_value} current_page is:{current_page} total_page is:{total_page}')
        try:
            table = driver.find_element(by=By.CSS_SELECTOR, value='div.search-line-list-wraper')
            rows = table.find_elements(by=By.CSS_SELECTOR, value='div.tab-item-box')
            page_ppn_arr = []
            for temp_row in rows:
                productInfo_arr = temp_row.find_elements(by=By.CSS_SELECTOR, value='div.item-box')
                if productInfo_arr and productInfo_arr.__len__() >= 3:
                    # PPN INFO
                    baseInfo = productInfo_arr[0]
                    goods_baseInfo = baseInfo.find_element(by=By.CSS_SELECTOR, value='div.goods-info')
                    try:
                        prodcut_des = goods_baseInfo.find_elements(by=By.CSS_SELECTOR, value='p.info-title')[0].text
                    except:
                        prodcut_des = '--'
                    info_items = goods_baseInfo.find_elements(by=By.CSS_SELECTOR, value='em.sub-title')
                    if info_items and info_items.__len__() > 0:
                        tec_info = info_items[0].text
                        ppn_all = info_items[-2].text[3:]  # 型号：MY2N-GS DC24 BY OMZ/C
                    else:
                        LogHelper.write_log(log_file_name=logFile, content=f'{url_value} base info error can find ppn')
                        tec_info = '--'
                        ppn_all = '--'
                    print(f'ppn is :{ppn_all}')
                    # price INFO
                    try:
                        price = productInfo_arr[1].find_element(by=By.CSS_SELECTOR, value='p.p-m-price').text
                    except:
                        price = '--'
                    # STOCK INFO
                    stock_info = productInfo_arr[2].find_element(by=By.CSS_SELECTOR, value='div.search-stock-box')
                    # get stock_num = 总库存/ 分库存只和
                    try:
                        stock_num_zong = 0
                        # 显示的是总库存
                        sum_info = stock_info.find_element(by=By.CSS_SELECTOR, value='p.p-block')
                        em = sum_info.find_element(by=By.CSS_SELECTOR, value='em')  # eg: 库存：12073 个
                        stock = em.text[3:-2]
                        if stock.isdigit():
                            stock_num_zong = int(stock)
                    except:  # 显示各地库存
                        stock_num_zong = 0
                    try:
                        stock_num_feng = 0
                        stock_container = stock_info.find_element(by=By.CSS_SELECTOR,
                                                                  value='div.stock-container.el-tooltip')
                        if stock_container:
                            a_arr = stock_container.find_elements(by=By.CSS_SELECTOR, value='a')
                            for temp_stock in a_arr:
                                stock_text = temp_stock.text  # eg:厂家直发仓（15365个，¥ 0.66，预计1-3天发货)
                                temp_stock_num = get_stcok_num(source_str=stock_text)
                                stock_num_feng += temp_stock_num
                    except:
                        stock_num_feng = 0
                    stock_num = stock_num_zong + stock_num_feng
                    info_arr = [ppn_all, stock_num, manuID, manuName, prodcut_des, tec_info, price]
                    page_ppn_arr.append(info_arr)
                else:
                    LogHelper.write_log(log_file_name=logFile, content=f'{url_value} row info error')
            ExcelHelp.add_arr_to_sheet(file_name=sourceFile, sheet_name='ppn', dim_arr=page_ppn_arr)
            if current_page < total_page:
                goToNextPage()
            else:
                print(f'last page over current_page is:{current_page} total_page is:{total_page}')
                break
        except Exception as e:
            LogHelper.write_log(log_file_name=logFile, content=f'find page element error {e}')


# 将stock 描述转成数字，eg:厂家直发仓（15365个，¥ 0.66，预计1-3天发货)
def get_stcok_num(source_str: str) -> int:
    result = 0
    try:
        right = source_str.index('，')
        left = source_str.index('（')
        result = source_str[left + 1:right - 1]
    except:
        result = 0
    if result.isdigit():
        result = int(result)
    else:
        result = 0
    return result


def main():
    page_urls = ExcelHelp.read_col_content(file_name=sourceFile, sheet_name='all_url', col_index=1)
    for (url_index, url_value) in enumerate(page_urls):
        if url_index in range(0, 18) and url_value:
            driver.get(url_value)
            anly_webdriver(url_index=url_index, url_value=url_value)
            WaitHelp.waitfor(True, False)


if __name__ == "__main__":
    driver.get(login_url)
    loginAction(login_url)
    main()

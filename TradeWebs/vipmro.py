# 京东工品汇

# 硬之城
import ssl
from WRTools import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp, LogHelper
import time


ssl._create_default_https_context = ssl._create_unverified_context


driver_option = webdriver.ChromeOptions()
driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(480)

default_url = 'https://www.vipmro.com/'


result_save_file = PathHelp.get_file_path('TradeWebs', 'vipmro.xlsx')
log_file = PathHelp.get_file_path('TradeWebs', 'log.txt')
current_page = 1
total_page = 0
login_url = 'https://www.vipmro.com/login?backURL=https%3A%2F%2Fwww.vipmro.com%2F'
accouts_arr = ['river12345654321', 'Calcitrapa0228']

# 获取当前页面的数据
def get_page_data(manu_id):
    print(f'cate_id is:{manu_id}  current_page is:{current_page} total_page is:{total_page}')
    try:
        table = driver.find_element(by=By.CSS_SELECTOR, value='div.list-line-body')
        rows = table.find_elements(by=By.CSS_SELECTOR, value='div.goods-line-items')
        page_ppn_arr = []
        for temp_row in rows:
            try:
                ppn_info = temp_row.find_element(By.CSS_SELECTOR, 'div.goods-info')
                ppn = \
                ppn_info.find_elements(By.CSS_SELECTOR, 'div.goods-info-detail')[-1].find_elements(By.TAG_NAME, 'span')[
                    -1].text
                manu = ppn_info.find_element(By.CSS_SELECTOR, 'a.goods-name').text.split(' ')[0]

                attr = temp_row.find_element(By.CSS_SELECTOR, 'div.goods-attr')
                if len(attr.find_elements(By.TAG_NAME, 'p')) > 0:
                    serial = attr.find_elements(By.TAG_NAME, 'p')[0].text.replace('系列：', '')
                else:
                    serial = ''
                if len(attr.find_elements(By.TAG_NAME, 'p')) > 1:
                    kind = attr.find_elements(By.TAG_NAME, 'p')[1].text.replace('产品类型：', '')
                else:
                    kind = ''
                date_line = temp_row.find_element(By.CSS_SELECTOR, 'div.goods-stock').find_element(By.TAG_NAME,
                                                                                                   'span').text
                price = temp_row.find_element(By.CSS_SELECTOR, 'div.goods-price').find_element(By.CSS_SELECTOR,
                                                                                               'div.show-price').text.replace('￥', '')
                info_arr = [ppn, manu, serial, kind, date_line, price]
                page_ppn_arr.append(info_arr)
            except Exception as e:
                print('row info error')
        ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name='202410', dim_arr=page_ppn_arr)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'find page element error {e}')


def go_to_manu(manuID):
    global current_page
    time.sleep(2.0)
    new_url = f'https://www.vipmro.com/ss/c-{manuID}?stock=1&page=1&#totalGood'
    driver.get(new_url)
    WaitHelp.waitfor_account_import(True, False)
    setTotal_page()
    current_page = 1
    while current_page <= total_page:
        scroll()
        scroll()
        get_page_data(manuID)
        if current_page == total_page:
            break;
        else:
            go_nextPage(manuID)


# 获取总页数
def setTotal_page():
    global total_page
    global current_page
    total_page = 1
    try:
        page_str = driver.find_element(by=By.CSS_SELECTOR, value="span.page-info").text.split(' / ')[1]
        if len(page_str) > 0:
            total_page = int(page_str)
    except:
        total_page = 1
    current_page = 1


# go 下一页
def go_nextPage(manuID):
    global current_page
    new_url = f'https://www.vipmro.com/ss/c-{manuID}?stock=1&page={current_page + 1}&#totalGood'
    driver.get(new_url)
    WaitHelp.waitfor(True, False)
    current_page += 1


# 滚动到列表底部
def scroll():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(8)  # 可以根据需要调整等待时间


# 登陆
def loginAction(aim_url):
    driver.get(login_url)
    WaitHelp.waitfor(True, False)
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
    # if not driver.current_url.startswith('https://www.vipmro.com/searchModel/'):
    #     driver.get(aim_url)


def main():
    cates = ExcelHelp.read_col_content(result_save_file, 'cate', 1)
    for (index, temp) in enumerate(cates):
        if index >= 26:
            print(f'index is : {index}')
            go_to_manu(temp)


if __name__ == "__main__":
    driver.get(default_url)
    time.sleep(60)
    loginAction(login_url)
    main()


# def temp():
#     file = PathHelp.get_file_path('TradeWebs', 'vipmro.xlsx')
#     source = ExcelHelp.read_sheet_content_by_name(file, '202410')
#     result = []
#     pattern = re.compile(r'[\u4e00-\u9fff]')
#     unregular = []
#     for tempPPN in source:
#         new_ppn = str(tempPPN[0])
#         if new_ppn.__contains__('插') :
#             new_ppn = new_ppn.replace(' 插 ', '_')
#         if new_ppn.__contains__('（带灯）'):
#             new_ppn = new_ppn.replace('（带灯）', '_')
#         if new_ppn.__contains__('红'):
#             new_ppn = new_ppn.replace('红', 'red')
#         if new_ppn.__contains__('绿'):
#             new_ppn = new_ppn.replace('绿', 'green')
#         if new_ppn.__contains__('黄'):
#             new_ppn = new_ppn.replace('黄', 'yellow')
#         if new_ppn.__contains__('纯白'):
#             new_ppn = new_ppn.replace('纯白', '_pureWhite')
#         if new_ppn.__contains__('纯蓝'):
#             new_ppn = new_ppn.replace('纯蓝', '_pureBlue')
#         if new_ppn.__contains__(' 断续闪烁式 '):
#             new_ppn = new_ppn.replace(' 断续闪烁式 ', '_')
#         if new_ppn.__contains__('(蜂鸣器)') :
#             new_ppn = new_ppn.replace('(蜂鸣器)', '')
#         if new_ppn.__contains__('型'):
#             new_ppn = new_ppn.replace('型', '_type')
#         if new_ppn.__contains__('工业级'):
#             new_ppn = new_ppn.replace('工业级', '')
#         if new_ppn.__contains__('新'):
#             new_ppn = new_ppn.replace('新', '')
#         if new_ppn.__contains__('黑'):
#             new_ppn = new_ppn.replace('黑', 'black')
#         if new_ppn.__contains__('玻板'):
#             new_ppn = new_ppn.replace('玻板', '')
#         if new_ppn.__contains__('玻'):
#             new_ppn = new_ppn.replace('玻', '')
#         if new_ppn.__contains__('胶板'):
#             new_ppn = new_ppn.replace('胶板', '')
#         if new_ppn.__contains__('胶'):
#             new_ppn = new_ppn.replace('胶', '')
#         if new_ppn.__contains__('(保护型)'):
#             new_ppn = new_ppn.replace('(保护型)', '')
#         if new_ppn.__contains__(' 接触式继电器'):
#             new_ppn = new_ppn.replace(' 接触式继电器', '')
#         if new_ppn.__contains__(' 直流'):
#             new_ppn = new_ppn.replace(' 直流', '')
#         if new_ppn.__contains__('灯箱'):
#             new_ppn = new_ppn.replace('灯箱', '')
#         if new_ppn.__contains__(' 交流接触器'):
#             new_ppn = new_ppn.replace(' 交流接触器', '')
#         if new_ppn.__contains__('灯箱'):
#             new_ppn = new_ppn.replace('灯箱', '')
#         if new_ppn.__contains__('(套装）'):
#             new_ppn = new_ppn.replace('(套装）', '')
#         if new_ppn.__contains__('(单机）'):
#             new_ppn = new_ppn.replace('(单机）', '')
#         if new_ppn.__contains__('（右组合）'):
#             new_ppn = new_ppn.replace('（右组合）', '')
#         if new_ppn.__contains__('胶板无机构手柄'):
#             new_ppn = new_ppn.replace('胶板无机构手柄', '')
#         if new_ppn.__contains__('玻板无机构手柄'):
#             new_ppn = new_ppn.replace('玻板无机构手柄', '')
#         if new_ppn.__contains__('无机构手柄'):
#             new_ppn = new_ppn.replace('无机构手柄', '')
#         # if new_ppn.__contains__(' '):
#         #     new_ppn = new_ppn.replace('', '_')
#         if bool(pattern.search(new_ppn)):
#             unregular.append([new_ppn] + tempPPN)
#         else:
#             result.append([new_ppn] + tempPPN)
#     ExcelHelp.add_arr_to_sheet(file, 'right2', result)
#     time.sleep(3.0)
#     ExcelHelp.add_arr_to_sheet(file, 'zh2', unregular)

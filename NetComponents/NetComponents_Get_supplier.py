# 获取京满仓的ppn，库存
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import ssl
from WRTools import IPHelper, UserAgentHelper, ExcelHelp, WaitHelp, PathHelp, LogHelper

ssl._create_default_https_context = ssl._create_unverified_context

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TNetComponent.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 20}
result_save_file = PathHelp.get_file_path('NetComponents', 'NetComponents.xlsx')
logFile = PathHelp.get_file_path('NetComponents', 'NetComponents_supplier_log.txt')

login_url = 'https://www.netcomponents.com/#login.htm?int=1'
total_page = 1
current_page = 1
accouts_arr = ['1175888', 'Mia', 'SZyjcx123']
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


# 登陆
def loginAction(aim_url):
    WaitHelp.waitfor_account_import(True, False)


# 分析html 文件
def anly_webdriver(cate_index, cate_name):
    try:
        pns = driver.find_elements(By.CLASS_NAME, value='pn')
        mfrs = driver.find_elements(By.CLASS_NAME, value='mfr')
        dcs = driver.find_elements(By.CLASS_NAME, value='dc')
        descs = driver.find_elements(By.CLASS_NAME, value='desc')
        uploads = driver.find_elements(By.CLASS_NAME, value='upl')
        qtys = driver.find_elements(By.CLASS_NAME, value='qty')
        sups = driver.find_elements(By.CLASS_NAME, value='sup')
        result = []
        for (index, ppn) in enumerate(pns):
            pn = ppn.text
            result.append([pn,
                           mfrs[index].text,
                           dcs[index].text,
                           descs[index].text,
                           uploads[index].text,
                           qtys[index].text,
                           sups[index].text])
    except Exception as e:
        LogHelper.write_log(log_file_name=logFile, content=f'cate_index {cate_index} cate_name {cate_name} find page element error {e}')
    ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name='NetComponent_sup', dim_arr=result)


def main():
    all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    for (cate_index, cate_name) in enumerate(all_cates):
        if cate_name is None or cate_name.__contains__('?'):
            continue
        elif cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
            url_value = f'https://www.netcomponents.com/results.htm?flts=1&t=f&sm=&r=1&lgc=begins&pn1={cate_name}'
            driver.get(url_value)
            WaitHelp.waitfor(True, False)
            driver.execute_script("var q=document.documentElement.scrollTop=10000")
            time.sleep(3.0)
            anly_webdriver(cate_index=cate_index, cate_name=cate_name)


if __name__ == "__main__":
    driver.get(login_url)
    loginAction(login_url)
    main()

import base64
import random
import ssl
import time

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import IPHelper, UserAgentHelper, LogHelper
import bom_price_info
from IC_stock import IC_stock_excel_read, IC_Stock_excel_write

ssl._create_default_https_context = ssl._create_unverified_context

driver_option = webdriver.ChromeOptions()
driver_option.add_argument(f'--proxy-server=http://{IPHelper.getRandowIP()}')
driver_option.add_argument("–incognito")
#  等待初始HTML文档完全加载和解析，
driver_option.page_load_strategy = 'eager'
driver_option.add_argument(f'user-agent="{UserAgentHelper.getRandowUA()}"')
prefs = {"profile.managed_default_content_settings.images": 2}
driver_option.add_experimental_option('prefs', prefs)
driver = uc.Chrome(use_subprocess=True)
driver.set_page_load_timeout(10)
# logic
accouts_arr = [["深圳市凯恩德实业有限公司", "liuyang", "Oliver121314"]]
default_url = 'https://www.bom.ai/ic/74LVX4245MTCX.html'
cate_source_file = '/Users/liuhe/PycharmProjects/SeleniumDemo/T0806.xlsx'
result_save_file = '/Users/liuhe/PycharmProjects/SeleniumDemo/Bom_price/bom_price_cate_0806.xlsx'
log_file = '/Users/liuhe/PycharmProjects/SeleniumDemo/Bom_price/bom_price_log.txt'


# 等待时间，load new page -> 5s; else 2s
def waitfor(is_load_page):
    # load new page
    if is_load_page:
        time.sleep(66 + random.randint(5, 55))
    else:
        time.sleep(20 + random.randint(2, 22))


# 登陆action
def login_action(aim_url):
    try:
        erp_entre = driver.find_element(by=By.CLASS_NAME, value='Bom_loging_title_erplogin.login_phone')
        display = erp_entre.is_displayed()
        if display:
            erp_entre.click()
            login_action(aim_url)
        else:
            # begin login
            accout_current = random.choice(accouts_arr)
            compay = driver.find_element(by=By.ID, value='companyName')
            compay.clear()
            compay.send_keys(accout_current[0])
            username = driver.find_element(by=By.ID, value='accountName')
            username.clear()
            username.send_keys(accout_current[1])
            password = driver.find_element(by=By.ID, value='smspassword')
            password.clear()
            password.send_keys(accout_current[2])
            time.sleep(3)
            driver.find_element(by=By.ID, value='smsLoginBtn').click()
        waitfor(True)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'login action exception is: {e}')


# 判断是否需要登陆，如果需要就登陆
def current_need_login() -> bool:
    if driver.current_url.startswith('https://www.bom.ai/ic'):
        try:
            login_links = driver.find_elements(by=By.CLASS_NAME, value='bom_power_a.bom_layer_login')
            if len(login_links) > 0:
                login_links[0].click()
                login_action(default_url)
        except Exception as e:
            LogHelper.write_log(log_file_name=log_file, content=f'login check exception：{e}')
            return False
    else:
        return False


# 跳转到下一个指定的型号
def go_to_cate(cate_index, cate_name):
    try:
        if driver.current_url.startswith('https://www.bom.ai/ic'):
            if cate_name.encode().isalnum():
                param = cate_name
            else:
                param = str(base64.b64encode(cate_name.encode('utf-8')), 'utf-8')
                param = '==' + param
            driver.get(f'https://www.bom.ai/ic/{param}.html')
            # input_area = driver.find_element(by=By.ID, value='kw')
            # input_area.clear()
            # input_area.send_keys(cate_name)
            # search_button = driver.find_element(by=By.ID, value='su')
            # search_button.click()
        else:
            driver.get(default_url)
            go_to_cate(cate_index, cate_name)
    except:
        login_action(f'https://www.bom.ai/ic/{cate_name}.html')


# 解析某个型号的页面信息，先看未折叠的前三行，判断是否需要展开，展开，解析，再判断，再展开，再解析。。。。
def analy_html(cate_index, cate_name):
    # 是否需要继续展开。 出现第一条非本周数据后不再展开
    need_more = True
    # 默认直接现实的row
    valid_supplier_arr = []
    try:
        yun_exg = driver.find_element(by=By.ID, value='yunexg')
        ul_arr = yun_exg.find_elements(by=By.TAG_NAME, value='ul')
        for ul in ul_arr:
            if not need_more:
                break
            aside = ul.find_element(by=By.TAG_NAME, value='aside')
            bom_price_ele = get_supplier_info(aside=aside, cate_index=cate_index, cate_name=cate_name)
            if bom_price_ele.is_valid_supplier():
                valid_supplier_arr.append(bom_price_ele.descritpion_arr())
            else:
                print(f'supplier invalid: {bom_price_ele.description_str()}')
                need_more = False
    except Exception as e:
        need_more = False
        LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} html 解析异常：{e} or nodata')
    # 折叠的row ##########################################################################################################
    while need_more:
        try:
            nav = driver.find_element(by=By.CLASS_NAME,
                                      value='bom_yun_agens.bomID_yunextts_agens.bom_quoteyunext_length')
            nav_display = nav.is_displayed()
            if nav_display:
                alink = nav.find_element(by=By.TAG_NAME, value='a')
                alink.click()
            else:
                need_more = False  # 已经展示完了
                break
            yun_extts = driver.find_element(by=By.ID, value='bomidyunextts')
            ul = yun_extts.find_elements(by=By.TAG_NAME, value='ul')[-1]  # 最后一个就是最近一次展开的内容
            aside_arr = ul.find_elements(by=By.TAG_NAME, value='aside')
            for (aside_index, aside) in enumerate(aside_arr):
                if not need_more:
                    break
                bom_price_ele = get_supplier_info(aside=aside, cate_index=cate_index, cate_name=cate_name)
                if bom_price_ele.is_valid_supplier():
                    valid_supplier_arr.append(bom_price_ele.descritpion_arr())
                else:
                    print(f'supplier invalid: {bom_price_ele.description_str()}')
                    need_more = False
        except Exception as e:
            need_more = False   #may be no load more
            LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} load more 解析异常：{e}')
    sheet_name_base64str = str(base64.b64encode(cate_name.encode('utf-8')), 'utf-8')
    IC_Stock_excel_write.add_arr_to_sheet(
        file_name=result_save_file,
        sheet_name=sheet_name_base64str,
        dim_arr=valid_supplier_arr)
    valid_supplier_arr.clear()


# 将页面row的内容 转化成Bom_price_info
# aside: contain row info
def get_supplier_info(aside, cate_index, cate_name) ->bom_price_info.Bom_price_info:
    section_arr = aside.find_elements(by=By.TAG_NAME, value='section')
    supplier_section = section_arr[1]
    try:
        supplier_name = supplier_section.find_element(by=By.TAG_NAME, value='a').text
    except:
        supplier_name = '--'
    pakage_section = section_arr[4]
    try:
        pakage_name = pakage_section.find_element(by=By.TAG_NAME, value='p').text
    except:
        pakage_name = '--'
    year_section = section_arr[5]
    try:
        year_str = year_section.find_element(by=By.TAG_NAME, value='p').text
    except:
        year_str = '--'
    price_section = section_arr[6]
    try:
        price_str = price_section.find_element(by=By.TAG_NAME, value='p').text
    except:
        price_str = '--'
    release_time_section = section_arr[7]
    try:
        release_time = release_time_section.find_element(by=By.TAG_NAME, value='p').text
    except:
        release_time = '--'
    stock_num_section = section_arr[8]
    try:
        stock_num = stock_num_section.find_element(by=By.TAG_NAME, value='p').text
    except:
        stock_num = '--'
    manu_name = IC_stock_excel_read.get_cell_content(file_name=cate_source_file, sheet_name="all", row=cate_index + 1, col=2)
    bom_price_ele = bom_price_info.Bom_price_info(cate=cate_name, manu=manu_name, supplier=supplier_name,
                                                  package=pakage_name, year=year_str, quoted_price=price_str,
                                                  release_time=release_time, stock_num=stock_num)
    return bom_price_ele


def main():
    all_cates = IC_stock_excel_read.get_cate_name_arr(file_name=cate_source_file,sheet_name='all', col_index=1)
    sub_cates = all_cates[0:800]
    for (cate_index, cate_name) in enumerate(sub_cates):
        if cate_name is None:
            continue
        else:
            print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
            go_to_cate(cate_index, cate_name)
            waitfor(True)
            current_need_login()
            analy_html(cate_index, cate_name)


if __name__ == "__main__":
    driver.get(default_url)
    current_need_login()
    time.sleep(5)
    main()
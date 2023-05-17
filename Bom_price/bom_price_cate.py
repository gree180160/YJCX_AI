import base64
import random
import ssl
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from WRTools import LogHelper, PathHelp, ExcelHelp, WaitHelp
from Manager import AccManage, TaskManager
import bom_price_info

ssl._create_default_https_context = ssl._create_unverified_context

driver = uc.Chrome(use_subprocess=True)
driver.set_page_load_timeout(120)
# logic

# accouts_arr = [["深圳市元极创新电子有限公司", "caigou01", "Yjcx123"]]
accouts_arr = [[AccManage.Bom['c'], AccManage.Bom['n'], AccManage.Bom['p']]]

sourceFile_dic = {'fileName': PathHelp.get_file_path(TaskManager.Taskmanger().task_name, 'Task.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': TaskManager.Taskmanger().start_index,
                  'endIndex': TaskManager.Taskmanger().end_index}
result_save_file = PathHelp.get_file_path(TaskManager.Taskmanger().task_name, 'bom_price.xlsx')

default_url = 'https://www.bom.ai/ic/74LVX4245MTCX.html'
log_file = PathHelp.get_file_path('Bom_price', 'bom_price_log.txt')


# 登陆action
def login_action(aim_url):
    try:
        erp_entre = driver.find_element(by=By.CLASS_NAME, value='Bom_loging_title_erplogin.login_phone')
        display = erp_entre.is_displayed()
        if display:
            WaitHelp.waitfor(False, False)
            erp_entre.click()
            WaitHelp.waitfor(False, False)
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
        WaitHelp.waitfor(True, False)
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
        else:
            driver.get(default_url)
            go_to_cate(cate_index, cate_name)
    except:
            login_action(f'https://www.bom.ai/ic/{cate_name}.html')


# 解析某个型号的页面信息，先看未折叠的前三行，判断是否需要展开，展开，解析，再判断，再展开，再解析。。。。
def analy_html(cate_index, ppn, manu):
    # 是否需要继续展开。 出现第一条非本周数据后不再展开
    need_more = True
    # 默认直接现实的row
    valid_supplier_arr = []
    try:
        # yun_exg = driver.find_element(by=By.ID, value='yunexg')
        # ul_arr = yun_exg.find_elements(by=By.TAG_NAME, value='ul')
        guwangMore()
        time.sleep(10.0)
        ur_arr = driver.find_elements(By.CSS_SELECTOR, 'ul.alt.bom_cloud_h')
        for ul in ur_arr:
            # if not need_more:
            #     break
            aside = ul.find_element(by=By.TAG_NAME, value='aside')
            bom_price_ele = get_supplier_info(aside=aside, cate_index=cate_index, ppn=ppn, manu=manu)
            if not bom_price_ele.is_valid_supplier():
                print(f'supplier invalid: {bom_price_ele.description_str()}')
                need_more = False
            valid_supplier_arr.append(bom_price_ele.descritpion_arr())
    except Exception as e:
        need_more = False
        LogHelper.write_log(log_file_name=log_file, content=f'{ppn} html 解析异常：{e} or nodata')
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
                bom_price_ele = get_supplier_info(aside=aside, cate_index=cate_index, ppn=ppn, manu=manu)
                if not bom_price_ele.is_valid_supplier():
                    print(f'supplier invalid: {bom_price_ele.description_str()}')
                    need_more = False
                valid_supplier_arr.append(bom_price_ele.descritpion_arr())
        except Exception as e:
            need_more = False  # may be no load more
            LogHelper.write_log(log_file_name=log_file, content=f'{ppn} load more 解析异常：{e}')
    ExcelHelp.add_arr_to_sheet(
    file_name=result_save_file,
    sheet_name='bom_price',
    dim_arr=valid_supplier_arr)
    valid_supplier_arr.clear()


def guwangMore():
    try:
        guwangmore_nav = driver.find_element(By.CSS_SELECTOR, 'nav.bom_yun_agens.bomID_yun_agens.guanwangMore')
        a = guwangmore_nav.find_element(By.TAG_NAME, 'a')
        a.click()
    except:
        print('click gu wang more error')


# 将页面row的内容 转化成Bom_price_info
# aside: contain row info
def get_supplier_info(aside, cate_index, ppn, manu) -> bom_price_info.Bom_price_info:
    section_arr = aside.find_elements(by=By.TAG_NAME, value='section')
    supplier_section = section_arr[1]
    try:
        supplier_name = supplier_section.find_element(by=By.TAG_NAME, value='a').text
    except:
        supplier_name = '--'
    cate_name_section = section_arr[2]
    try:
        cate_name = cate_name_section.find_element(by=By.TAG_NAME, value='a').text
        # 无需做ppn 和 bom 获取的cate_name 的匹配验证
    except:
        cate_name = '--'
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
    bom_price_ele = bom_price_info.Bom_price_info(cate=cate_name, manu=manu, supplier=supplier_name,
                                                  package=pakage_name, year=year_str, quoted_price=price_str,
                                                  release_time=release_time, stock_num=stock_num)
    return bom_price_ele


def main():
    all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    all_manus =  ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex']+1)
    for (ppn_index, ppn) in enumerate(all_cates):
        if ppn is None or ppn.__contains__('?'):
            continue
        elif ppn_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {ppn_index}  cate_name is: {ppn}')
            go_to_cate(ppn_index, str(ppn))
            if ppn_index > 0 and ppn_index % 15 == 0:
                time.sleep(480)
            else:
                WaitHelp.waitfor(True, False)
            current_need_login()
            analy_html(cate_index=ppn_index, ppn=str(ppn), manu=all_manus[ppn_index])


if __name__ == "__main__":
    driver.get(default_url)
    current_need_login()
    WaitHelp.waitfor(False, True)
    main()

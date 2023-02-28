import base64
import random
import ssl
import time

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import IPHelper, UserAgentHelper, LogHelper, PathHelp, WaitHelp
import octopart_price_info
from IC_stock import IC_stock_excel_read, IC_Stock_excel_write
import re

ssl._create_default_https_context = ssl._create_unverified_context

driver_option = webdriver.ChromeOptions()
# driver_option.add_argument(f'--proxy-server=http://{IPHelper.getRandowIP_country()}')
# driver_option.add_argument("–incognito")
#  等待初始HTML文档完全加载和解析，
driver_option.page_load_strategy = 'eager'
proxyAddr = "tunnel3.qg.net:15404" #代理IP地址和端口号
driver_option.add_argument('--proxy-server=%(server)s' % {"server": proxyAddr})
driver = uc.Chrome(use_subprocess=True, options=driver_option)
driver.set_page_load_timeout(100)
# logic
default_url = 'https://octopart.com/what-is-octopart'
cate_source_file = PathHelp.get_file_path(None, 'TInfineonAgencyInventory.xlsx')
result_save_file = PathHelp.get_file_path('Octopart_price', 'octopart_price_cate_InfineionAgency.xlsx')
log_file = PathHelp.get_file_path('Octopart_price', 'ocopar_price_log.txt')


# 跳转到下一个指定的型号
def go_to_cate(cate_index, cate_name):
    try:
        if driver.current_url.startswith('https://octopart.com/search?q='):
            if driver.current_url == f"https://octopart.com/search?q={cate_name}&currency=USD&specs=0":
                return
            input_area = driver.find_element(by=By.TAG_NAME, value='input')
            input_area.clear()
            input_area.send_keys(cate_name)
            input_box = driver.find_element(by=By.CLASS_NAME, value='jsx-4214615671.search-box')
            search_button = input_box.find_element(by=By.TAG_NAME, value='button')
            search_button.click()
        else:
            driver.get(f"https://octopart.com/search?q={cate_name}&currency=USD&specs=0")
            go_to_cate(cate_index, cate_name)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} go_to_cate except: {e}')


# 解析某个型号的页面信息，如果有更多，直接点击，然后只选择start ， 遇到第一个不是star 的就返回
def analy_html(cate_index, cate_name):
    # 是否需要继续展开。 出现第一条非start数据后不再展开
    try:
        all_cates = driver.find_element(by=By.CLASS_NAME, value='jsx-922694994.results')
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} all_cates exception:{e}')
        return
    try:
        first_cate = all_cates.find_element(by=By.CLASS_NAME, value='jsx-2172888034')  # jsx-2400378105 part
    except:
        first_cate = all_cates.find_element(by=By.CLASS_NAME, value='jsx-2172888034 part')
    if not cate_valid(cate_name, first_cate):
        return
    need_more = True
    # 默认直接显示的row
    valid_supplier_arr = []
    tr_arr = []
    try:
        cate_table = first_cate.find_element(by=By.TAG_NAME, value='tbody')
        tr_arr = cate_table.find_elements(by=By.TAG_NAME, value='tr')
        for tr in tr_arr:
            if not need_more:
                break
            cate_price_ele = get_supplier_info(tr=tr, cate_index=cate_index, cate_name=cate_name)
            # 只有实心(1)数据才是有效的，只有空心(-1)才需要停止loop
            if cate_price_ele.is_valid_supplier():
                valid_supplier_arr.append(cate_price_ele.descritpion_arr())
            else:
                print(f'supplier invalid: {cate_price_ele.description_str()}')
                if cate_price_ele.stop_loop():
                    need_more = False
    except Exception as e:
        need_more = False
        LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} 默认打开的内容解析异常：{e} ')

    if need_more:
        click_more_row(cate_html=first_cate, cate_name=cate_name)
    # 折叠的row ##########################################################################################################
    dealed_count = len(tr_arr)
    all_cates2 = driver.find_element(by=By.CLASS_NAME, value='jsx-2172888034.prices-view')
    try:
        first_cate2 = all_cates2.find_element(by=By.CLASS_NAME, value='jsx-2172888034')  # jsx-2400378105 part
    except:
        first_cate2 = all_cates2.find_element(by=By.CLASS_NAME, value='jsx-2172888034 part')
    try:
        cate_table2 = first_cate2.find_element(by=By.TAG_NAME, value='tbody')
        tr_arr2 = cate_table2.find_elements(by=By.TAG_NAME, value='tr')
        left_tr_arr = tr_arr2[dealed_count:-1]
        for tr in left_tr_arr:
            if not need_more:
                break
            cate_price_ele2 = get_supplier_info(tr=tr, cate_index=cate_index, cate_name=cate_name)
            if cate_price_ele2.is_valid_supplier():
                valid_supplier_arr.append(cate_price_ele2.descritpion_arr())
            else:
                print(f'supplier invalid: {cate_price_ele2.description_str()}')
                if cate_price_ele2.stop_loop():
                    need_more = False
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} more 解析异常：{e} ')
    sheet_name_base64str = str(base64.b64encode(cate_name.encode('utf-8')), 'utf-8')
    IC_Stock_excel_write.add_arr_to_sheet(
        file_name=result_save_file,
        sheet_name=sheet_name_base64str,
        dim_arr=valid_supplier_arr)
    valid_supplier_arr.clear()


# 判断当前内容是否和cate_name 一致
def cate_valid(cate_name, first_row) -> bool:
    result = False
    try:
        cate_div = first_row.find_element(by=By.CLASS_NAME, value='jsx-312275976.jsx-2649123136.mpn')
        html_cate_name = cate_div.text
        # 去掉中间的空格防止，导入的cate 格式误差
        cate_name = cate_name.replace(" ", "")
        html_cate_name = html_cate_name.replace(" ", "")
        # 去掉结尾的+，因为cate_name ,结尾有无+都是一个型号
        if cate_name.endswith('+'):
            cate_name = cate_name[0:-1]
        if html_cate_name.endswith('+'):
            html_cate_name = html_cate_name[0:-1]
        result = bool(re.search(cate_name, html_cate_name, re.IGNORECASE))
        if not result:
            LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} cannot match')
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} cannot check name: {e}')
        result = False
    return result


# 将页面tr的内容 转化成octopart_price_info
# tr: contain row info
def get_supplier_info(tr, cate_index, cate_name) -> octopart_price_info:
    td_arr = tr.find_elements(by=By.TAG_NAME, value='td')
    star_td = td_arr[0]
    is_star = 0
    try:
        a = star_td.find_element(by=By.TAG_NAME, value='a')
        title = a.get_attribute('title')
        if title == 'Non-Authorized Stocking Distributor':
            is_star = -1
        elif title == 'Authorized Distributor':
            is_star = 1
        else:
            is_star = 0
    except:
        is_star = -1
    distribute_tr = td_arr[1]
    try:
        distribute_name = distribute_tr.find_element(by=By.TAG_NAME, value='a').text
    except:
        distribute_name = '--'
    SKU_tr = td_arr[2]
    try:
        sku = SKU_tr.text
    except:
        sku = "--"
    stock_tr = td_arr[3]
    try:
        stock = stock_tr.text
    except:
        stock = '--'
    MOQ_tr = td_arr[4]
    try:
        moq = MOQ_tr.text
    except:
        moq = '--'
    currency_type_tr = td_arr[6]
    try:
        currency_type = currency_type_tr.text
    except:
        currency_type = '--'
    k_price_tr = td_arr[10]
    try:
        k_price = k_price_tr.text
    except:
        k_price = '--'
    updated_tr = td_arr[12]
    try:
        updated_span = updated_tr.find_element(by=By.TAG_NAME, value='span')
        updated = updated_span.text
    except:
        updated = '--'
    manu_name = "--"
    octopart_price_ele = octopart_price_info.Octopart_price_info(cate=cate_name, manu=manu_name, is_star=is_star,
                                                                 distribute=distribute_name, SKU=sku, stock=stock,
                                                                 MOQ=moq, currency_type=currency_type, k_price=k_price,
                                                                 updated=updated)
    return octopart_price_ele


# 展开这个cate的更多distribute info
def click_more_row(cate_html, cate_name):
    try:
        footer_ele = cate_html.find_element(by=By.CLASS_NAME, value='jsx-3623225293.footer')
        more_button_div = footer_ele.find_element(by=By.CLASS_NAME, value='jsx-3623225293')
        more_button = more_button_div.find_element(by=By.TAG_NAME, value='button')
        more_button.click()
        WaitHelp.waitfor_octopart(True, False)
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{cate_name} click more exception: {e}')


#  请求频繁，导致出现弹框，有则关闭，无则异常
def close_alert():
    try:
        close_button = driver.find_element(by=By.CLASS_NAME, value='jsx-535551409.close-button')
        close_button.click()
    except Exception as e:
        return


def main():
    all_cates = IC_stock_excel_read.get_cate_name_arr(cate_source_file, 'all', 1)
    for (cate_index, cate_name) in enumerate(all_cates):
        if cate_index < 730:
            continue
        if cate_index%2 != 0:
            continue
        if cate_name is None:
            continue
        print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
        UserAgentHelper.driver_update_UA(driver)
        go_to_cate(cate_index, cate_name)
        WaitHelp.waitfor_octopart(True, False)
        close_alert()
        analy_html(cate_index, cate_name)



if __name__ == "__main__":
    UserAgentHelper.driver_update_UA(driver)
    driver.get(default_url)
    WaitHelp.waitfor_octopart(False, False)
    main()

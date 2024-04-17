import base64
import random
import ssl
import time

from WRTools import ChromeDriverManager
from selenium.webdriver.common.by import By
from WRTools import LogHelper, PathHelp, ExcelHelp, WaitHelp, MySqlHelp_recommanded
from selenium.common.exceptions import TimeoutException
from Manager import TaskManager, AccManage


ssl._create_default_https_context = ssl._create_unverified_context

driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(360)
# logic


sourceFile_dic = {'fileName': "/Users/liuhe/Desktop/卖什么/hxl.xlsx",
                  'sourceSheet': 'TIBrandS1',
                  'colIndex': 1,
                  'startIndex': 1,
                  'endIndex': 317}


default_url = 'https://www.digikey.cn/'
log_file = PathHelp.get_file_path('Digikey', 'DJ_product_status_log.txt')


# 登录账号
def login_Action():
    logbutton = driver.find_element(By.ID, 'my_digikey_logged_out')
    logbutton.click()
    WaitHelp.waitfor(True, False)
    name = driver.find_element(By.ID, 'username')
    name.clear()
    name.send_keys(AccManage.digikey['n'])
    password = driver.find_element(By.ID, 'password')
    password.clear()
    password.send_keys(AccManage.digikey['p'])
    log_btn = driver.find_element(By.ID, 'signOnButton')
    log_btn.click()
    WaitHelp.waitfor(True, False)


# 跳转到下一个指定的型号
def go_to_cate(cate_index, cate_name):
    try:
        header_area = driver.find_element(by=By.CLASS_NAME, value='header__search')
        input = header_area.find_element(by=By.TAG_NAME, value='input')
        input.clear()
        input.send_keys(cate_name)
        search_button = header_area.find_element(by=By.CLASS_NAME, value='search-button')
        search_button.click()
    except TimeoutException:
        timeout_ppn = cate_name
        LogHelper.write_log(log_file_name=log_file, content=f'go_to_cate {cate_name} timeout')
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'go_to_cate {cate_name} exception is: {e}')


# 解析某个型号的页面信息，先看未折叠的前三行，判断是否需要展开，展开，解析，再判断，再展开，再解析。。。。
def analy_html(cate_index, cate_name):
    # 判断是否需要点击详情
    if driver.current_url.__contains__('/products/detail'):
        getElement(cate_name)
    else:
        try:
            detail_links = driver.find_elements(By.CSS_SELECTOR, 'a.tss-1abf7dr-Link-anchor-buttonAnchor')
            if detail_links.__len__() > 2:
                detail_links = detail_links[0:2]
            if detail_links.__len__() > 0:
                print(f'{cate_name} go to details count {detail_links.__len__()}')
                for temp_link in detail_links:
                    temp_link.click()
                    WaitHelp.waitfor_account_import(True, False)
                    getElement(cate_name)
            else:
                print('没有建议 一个 ppn')
        except:
            print('直接展示')


#在详情页面获取，ppn 的具体信息
# Digi-Key 零件编号# 制造商# 制造商产品编号# 描述# 原厂标准交货期# 详细描述# 客户内部零件编号# 规格书# EDA/CAD 模型# 类别# 制造商# 系列# 包装# 产品状态
# 类型# 单向通道# 电压 - 反向断态（典型值）# 电压 - 击穿（最小值）# 不同 Ipp 时电压 - 箝位（最大值）# 电流 - 峰值脉冲 (10/1000µs)# 功率 - 峰值脉冲# 电源线路保护
# 应用   # 不同频率时电容 # 工作温度 # 安装类型 # 封装/外壳    # 供应商器件封装# 基本产品编号
def getElement(keyword):
    tables = driver.find_elements(By.TAG_NAME, 'table')
    base_info_ar = ['', '', '', '', '', '' ,'']
    if tables.__len__() > 0:
        baseInfo = tables[0]
        ppn = baseInfo.find_element(By.TAG_NAME, 'h1').text
        tbody = baseInfo.find_element(By.TAG_NAME, 'tbody')
        tr_list = tbody.find_elements(By.TAG_NAME, 'tr')
        digi_key_code = tr_list[0].find_elements(By.TAG_NAME, 'td')[1].text
        manu = tr_list[1].find_elements(By.TAG_NAME, 'td')[1].text
        manu_code = tr_list[2].find_elements(By.TAG_NAME, 'td')[1].text
        des = tr_list[3].find_elements(By.TAG_NAME, 'td')[1].text
        delivery_time = tr_list[4].find_elements(By.TAG_NAME, 'td')[1].text
        detail_des = tr_list[5].find_elements(By.TAG_NAME, 'td')[1].text
        base_info_ar = [ppn, manu, digi_key_code, manu_code, des, delivery_time, detail_des]
    attr_arr = ['', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '',
                '', '', '', '']
    attriTable = driver.find_elements(By.ID, 'product-attributes')
    if attriTable.__len__() > 0:
        tbody = attriTable[0].find_element(By.TAG_NAME, 'tbody')
        tr_list = tbody.find_elements(By.TAG_NAME, 'tr')
        category = tr_list[0].find_elements(By.TAG_NAME, 'td')[1].text
        serial = tr_list[2].find_elements(By.TAG_NAME, 'td')[1].text
        package = tr_list[3].find_elements(By.TAG_NAME, 'td')[1].text
        status = tr_list[4].find_elements(By.TAG_NAME, 'td')[1].text
        kind = tr_list[5].find_elements(By.TAG_NAME, 'td')[1].text
        single_channel = tr_list[6].find_elements(By.TAG_NAME, 'td')[1].text
        voltage_reverse = tr_list[7].find_elements(By.TAG_NAME, 'td')[1].text
        voltage_breakdown = tr_list[8].find_elements(By.TAG_NAME, 'td')[1].text
        voltage_ipp = tr_list[9].find_elements(By.TAG_NAME, 'td')[1].text
        peakCurrentPulse = tr_list[10].find_elements(By.TAG_NAME, 'td')[1].text
        peakPowerPulse = tr_list[11].find_elements(By.TAG_NAME, 'td')[1].text
        protect_power = tr_list[12].find_elements(By.TAG_NAME, 'td')[1].text
        apply = tr_list[13].find_elements(By.TAG_NAME, 'td')[1].text
        capacitance = tr_list[14].find_elements(By.TAG_NAME, 'td')[1].text
        operating_temperature = tr_list[15].find_elements(By.TAG_NAME, 'td')[1].text
        install_kind = tr_list[16].find_elements(By.TAG_NAME, 'td')[1].text
        shell =  tr_list[17].find_elements(By.TAG_NAME, 'td')[1].text
        supplier_packeage = tr_list[18].find_elements(By.TAG_NAME, 'td')[1].text
        product_code = tr_list[19].find_elements(By.TAG_NAME, 'td')[1].text
        attr_arr = [category, serial, package, status, kind, single_channel, voltage_reverse, voltage_breakdown, voltage_ipp, peakCurrentPulse, peakPowerPulse, protect_power, apply, capacitance, operating_temperature, install_kind, shell, supplier_packeage, product_code]
    result = base_info_ar + attr_arr + [sourceFile_dic['sourceSheet']]
    MySqlHelp_recommanded.DBRecommandChip().digikey_attr_write(data=[result])
    time.sleep(2.0)


def main():
    all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    for (cate_index, cate_name) in enumerate(all_cates):
        if cate_name is None or cate_name.__contains__('?'):
            continue
        elif cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
            go_to_cate(cate_index, str(cate_name))
            if cate_index > 0 and cate_index % 15 == 0:
                time.sleep(480)
            else:
                WaitHelp.waitfor_account_import(True, False)
            analy_html(cate_index, str(cate_name))


# 供应商器件封装
if __name__ == "__main__":
    driver.get(default_url)
    login_Action()
    main()


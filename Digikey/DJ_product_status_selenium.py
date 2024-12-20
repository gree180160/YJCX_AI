import base64
import math
import random
import ssl
import time

from WRTools import ChromeDriverManager
from selenium.webdriver.common.by import By
from WRTools import LogHelper, PathHelp, ExcelHelp, WaitHelp, MySqlHelp_recommanded
from selenium.common.exceptions import TimeoutException
from Manager import AccManage
from selenium.webdriver.common.action_chains import ActionChains

ssl._create_default_https_context = ssl._create_unverified_context

driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(360)
# logic

# url_index is :5 current_page is :207  total page is :7781
# url_index is :30 current_page is :9  total page is :2896
sourceFile_dic = {'fileName': PathHelp.get_file_path("", 'THolt2411.xlsx'),
                  'sourceSheet': 'url2',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 2}


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
def go_manu(cate_index, cate_name):
    try:
        header_area = driver.find_element(by=By.CLASS_NAME, value='header__search')
        input = header_area.find_element(by=By.TAG_NAME, value='input')
        input.clear()
        input.send_keys(cate_name)
        search_button = header_area.find_element(by=By.CLASS_NAME, value='search-button')
        search_button.click()
    except TimeoutException:
        timeout_ppn = cate_name
        LogHelper.write_log(log_file_name=log_file, content=f'go_manu {cate_name} timeout')
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'go_manu {cate_name} exception is: {e}')


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
            # go_to_cate(cate_index, str(cate_name))
            if cate_index > 0 and cate_index % 15 == 0:
                time.sleep(480)
            else:
                WaitHelp.waitfor_account_import(True, False)
            analy_html(cate_index, str(cate_name))


def get_secondURL():
    all_url = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    for (url_index, url_value) in enumerate(all_url):
        if url_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'url_index is :{url_index}')
            result = []
            driver.get(url_value)
            WaitHelp.waitfor(True, False)
            try:
                top = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="result-top"]')
                items = top.find_elements(By.CSS_SELECTOR, 'div[data-testid="card"]')
            except:
                top = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="subcategories-container"]')
                items = top.find_elements(By.CSS_SELECTOR, 'div[data-testid="image-view"]')
            for temp_item in items:
                try:
                    url = temp_item.find_element(By.CSS_SELECTOR, 'a.tss-css-yiafub-anchor').get_attribute('href')
                    title = temp_item.find_element(By.CSS_SELECTOR, 'div.tss-css-1nopv3b-categoryLabel').text
                    sub_title = temp_item.find_elements(By.CSS_SELECTOR, 'div.tss-css-cuw97q-categoryText')[-2].text
                    number = temp_item.find_elements(By.CSS_SELECTOR, 'div.tss-css-cuw97q-categoryText')[
                        -1].text.replace(
                        ' 种货品', '')
                except:
                    url = temp_item.find_element(By.CSS_SELECTOR, 'a[data-testid="subcategory-card"]').get_attribute('href')
                    title = temp_item.find_element(By.CSS_SELECTOR, 'p.tss-css-6lf7to-subCategoryLabel').text
                    sub_title = ''
                    number = temp_item.find_elements(By.CSS_SELECTOR, 'span.tss-css-aihsuu-itemCount')[
                        -1].text.replace(
                        ' 种货品', '')
                info = [url, title, sub_title, number]
                result.append(info)
            ExcelHelp.add_arr_to_sheet(sourceFile_dic['fileName'], '2', result)


def get_ppn():
    all_url = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                         sheet_name=sourceFile_dic['sourceSheet'],
                                         col_index=sourceFile_dic['colIndex'])
    for (url_index, url_value) in enumerate(all_url):
        if url_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            driver.get(url_value)
            WaitHelp.waitfor(True, False)
            sort_price()
            current_page = 1
            total_page = getTotal_page()
            while current_page <= total_page:
                result = []
                print(f'url_index is :{url_index} current_page is :{current_page}  total page is :{total_page}')
                table = driver.find_element(By.ID, 'data-table-0')
                tbody = table.find_element(By.TAG_NAME, 'tbody')
                rows = tbody.find_elements(By.TAG_NAME, 'tr')
                for temp_row in rows:
                    ppn = temp_row.find_elements(By.TAG_NAME, 'td')[1].find_element(By.CSS_SELECTOR, 'a[data-testid="data-table-product-number"]').text
                    des = temp_row.find_elements(By.TAG_NAME, 'td')[1].find_element(By.CSS_SELECTOR, 'div.tss-css-7dp38y-productColExpandedDescription').text
                    manu = temp_row.find_elements(By.TAG_NAME, 'td')[1].find_element(By.CSS_SELECTOR, 'a[data-testid="data-table-mfr-link"]').text
                    stock = temp_row.find_elements(By.TAG_NAME, 'td')[2].find_element(By.CSS_SELECTOR, 'div.tss-css-wkc3x7-infoListDataPrimary').text.replace(',','')
                    stock_status = temp_row.find_elements(By.TAG_NAME, 'td')[2].find_element(By.CSS_SELECTOR, 'div.tss-css-8e8qox-infoListDataSecondary').text
                    try:
                        price_list = temp_row.find_elements(By.TAG_NAME, 'td')[3].find_elements(By.CSS_SELECTOR, 'div.tss-css-wkc3x7-infoListDataPrimary')
                        if price_list.__len__() > 0:
                            price_info = price_list[-1].text
                            price_number = price_info.split(':')[0]
                            price = price_info.split(':')[1]
                        else:
                            price_number = ''
                            price = ''
                    except:
                        price_number = price = ''
                    valid_price = rule_prcice(price)
                    status = temp_row.find_elements(By.TAG_NAME, 'td')[6].text
                    if valid_price > 350:
                        info = [ppn, manu, des, stock, stock_status, price_number, price, status]
                        result.append(info)
                    else:
                        if price_number.__len__() > 0:
                            break
                ExcelHelp.add_arr_to_sheet(sourceFile_dic['fileName'], 'digikey', result)
                if result.__len__() < 10:
                    current_page = total_page # 强行终止
                if current_page < total_page:
                    go_next_page()
                current_page += 1


# 按价格降序
def sort_price():
    # todo move to element
    input_area = driver.find_elements(By.CSS_SELECTOR, 'input.MuiSelect-nativeInput')[0]
    driver.execute_script("arguments[0].scrollIntoView(true);", input_area)
    table = driver.find_element(By.CSS_SELECTOR, 'table.MuiTable-root')
    table_header = table.find_element(By.CSS_SELECTOR, 'thead.MuiTableHead-root')
    dsc_button = table_header.find_element(By.CSS_SELECTOR, 'button[data-testid="sort--101-dsc"]')
    dsc_button.click()
    time.sleep(60)


def getTotal_page():
    actions = ActionChains(driver)
    input_area = driver.find_elements(By.CSS_SELECTOR, 'input.MuiSelect-nativeInput')[0]
    driver.execute_script("arguments[0].scrollIntoView(true);", input_area)
    actions.move_to_element(input_area).click().perform()
    time.sleep(10.0)
    alert = driver.find_element(By.ID, 'per-page-selector-options')
    last = alert.find_elements(By.TAG_NAME, 'li')[-1]
    actions.move_to_element(last).click().perform()
    time.sleep(30.0)
    page_str = driver.find_element(By.CSS_SELECTOR, 'div.tss-css-vku2qe-usePerPageSelectorStyles-pageSelector').text.split('/')[1]
    page_str = page_str.replace(',', '')
    total_page = math.ceil(int(page_str)/100)
    return total_page


# 单价>350 才有效
def rule_prcice(price):
    price = price.replace('¥', '')
    price = price.replace(',', '')
    result = 0.0
    if len(price) > 0:
        try:
            result = float(price)
        except:
            result = 0.0
    else:
        result = 0.0
    result = round(result, 2)
    return result


def go_next_page():
    actions = ActionChains(driver)
    button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="btn-next-page"]')
    driver.execute_script("arguments[0].scrollIntoView(true);", button)
    actions.move_to_element(button).click().perform()
    button.click()
    WaitHelp.waitfor(True, False)


if __name__ == "__main__":
    driver.get(default_url)
    # login_Action()
    # main()
    time.sleep(16.0)
    get_ppn()

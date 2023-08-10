#  记录Task 提供的型号，在IC 中的库存信息
import base64
import math

from selenium.webdriver.common.by import By
import time
import undetected_chromedriver as uc
import ssl
from WRTools import ExcelHelp, WaitHelp, PathHelp, EmailHelper


ssl._create_default_https_context = ssl._create_unverified_context
# 定义要爬取的url

result_save_file = PathHelp.get_file_path('Tender', 'contract.xlsx')
result_save_sheet = 'Sheet'

# 定义一个变量来记录当前的页码
current_page = 1
total_page = 0

try:
    driver = uc.Chrome(use_subprocess=True)
    driver.set_page_load_timeout(1000)
except Exception as e:
    print(e)


def skip_login():
    try:
        skip_login_button = driver.find_element(By.CSS_SELECTOR, 'button.modal-form-reset')
        skip_login_button.click()
    except:
        print('skip login error')


def set_total_page():
    global total_page
    try:
        total_data = driver.find_elements(By.CSS_SELECTOR, 'b.main-tabs__count.count')[2].text
        total_data = total_data.replace(' ', '')
        total_page = math.ceil(int(total_data)/10)
    except:
        total_page = 0


def set_currentPage():
    global current_page
    page_area = driver.find_element(By.CSS_SELECTOR, 'div.pagination')
    current_page_ele = page_area.find_elements(By.CSS_SELECTOR, 'span.current')[-1]
    try:
        current_page = int(current_page_ele.text)
    except:
        current_page = total_page


def need_next_page():
    if int(current_page) < int(total_page):
        return True
    return False


def goto_nextPage():
    try:
        next_ele = driver.find_element(By.CSS_SELECTOR, 'a.page-link.next')
        driver.execute_script("arguments[0].click();", next_ele)
    except:
        print('goto next error')


def main():
    # 定义一个循环，直到爬取完所有的页码或者达到最大页码限制
    while True:
        # 打印当前的页码
        close_alert()
        print(f"正在爬取第{current_page}页...")
        # 访问网页
        # 找到所有的搜索结果，它们都在class为search-result-item的div标签里面
        items = driver.find_elements(By.CSS_SELECTOR, "div.card-item")
        # 判断是否有搜索结果
        page_result = []
        # 遍历每一个搜索结果
        for temp_item in items:
            try:
                # 定义一个字典来存储每个搜索结果的信息
                item_content = []
                Contract_No = temp_item.find_elements(By.CSS_SELECTOR, 'a.link')[0].text
                Contract_No = Contract_No.replace('Договор №', '')
                Contract_No = Contract_No.replace(' в ЕИС', '')

                Purchase_No = temp_item.find_elements(By.CSS_SELECTOR, 'a.link')[-1].text
                Purchase_No = Purchase_No.replace('Закупка №', '')
                Purchase_No = Purchase_No.replace(' в ЕИС', '')

                more_url = temp_item.find_element(By.CSS_SELECTOR, 'a.button-red').get_attribute("href")
                row_title = temp_item.find_element(By.CSS_SELECTOR, 'div.card-item__title').text
                # head
                contract_price = contract_security = status = '--'
                cells = temp_item.find_elements(By.CSS_SELECTOR, 'div.card-item__properties-cell')
                for (cell_index, tempCell) in enumerate(cells):
                    title_ele = tempCell.find_elements(By.CSS_SELECTOR, 'div.card-item__properties-name')
                    if title_ele.__len__() > 0:
                        title = title_ele[0].text
                        PSS_value = tempCell.find_element(By.CSS_SELECTOR, 'div.card-item__properties-desc').text
                        if title == 'ЦЕНА КОНТРАКТА' or title == 'ЦЕНА ДОГОВОРА':
                            contract_price = PSS_value
                        elif title == 'ОБЕСПЕЧЕНИЕ КОНТРАКТА' or title == 'ОБЕСПЕЧЕНИЕ ДОГОВОРА':
                            contract_security = PSS_value
                        elif title == 'СТАТУС':
                            status = PSS_value
                # publish_date, signature_data, deadline
                time_area = temp_item.find_element(By.CSS_SELECTOR, 'div.card-item__info')
                times = time_area.find_elements(By.TAG_NAME, 'time')
                publish_date = times[0].text
                signature_data = times[1].text
                deadline = times[2].text
                # organization
                org_area = temp_item.find_elements(By.CSS_SELECTOR, 'div.card-item__organization-main')[0]
                org_name = org_area.find_elements(By.TAG_NAME, 'p')[0].text
                org_tinKpp = org_area.find_elements(By.TAG_NAME, 'p')[1].text
                org_contact_det = org_area.find_elements(By.TAG_NAME, 'p')[2].text
                if org_contact_det == 'Контактные данные:':
                    org_contact_det = 'Информация скрыта'
                # customer
                cus_area = temp_item.find_elements(By.CSS_SELECTOR, 'div.card-item__organization-main')[1]
                cus_name = cus_area.find_elements(By.TAG_NAME, 'p')[0].text
                cus_tinKppReg = cus_area.find_elements(By.TAG_NAME, 'p')[1].text
                cus_det = cus_area.find_elements(By.TAG_NAME, 'p')[2].text
                if cus_det == 'Контактные данные:':
                    cus_det = 'Информация скрыта'
                cus_address = temp_item.find_elements(By.CSS_SELECTOR, 'div.content-address')[0].text
                cus_address = cus_address.replace('Адрес поставки: ', '')
                #supplier
                areas = temp_item.find_elements(By.CSS_SELECTOR, 'div.card-item__organization-main')
                if areas.__len__() >= 3:
                    supplier_area = areas[-1]
                    contents = supplier_area.find_elements(By.TAG_NAME, 'p')
                    supplier_name = contents[0].text
                    supplier_TinKpp = contents[1].text
                    supplier_tel = contents[-1].text
                else:
                    continue
                # 'Contract_No',"Purchase_No", 'title', 'contract_price', 'contract_security', 'status', 'published',
                #                   'signature_data', 'deadline', 'org_name', 'org_TinKpp', 'org_contact', 'cus_name', 'cus_TinKppReg',
                #                   'cus_contact', 'cus_address', 'supplier_name', 'supplier_TinKpp', 'supplier_tel', 'detail_url',
                #                   'page'
                item_content = [Contract_No, Purchase_No, row_title, change_money_ru(contract_price), contract_security, status, publish_date, signature_data, deadline,
                                org_name, org_tinKpp, org_contact_det,
                                cus_name, cus_tinKppReg, cus_det, cus_address,
                                supplier_name, supplier_TinKpp, supplier_tel,
                                more_url, current_page]
                print(item_content)
                # 把这个搜索结果添加到列表中
                page_result.append(item_content)
            except Exception as e:
                print(f'url is : {driver.current_url} get element error {e}')
        print(f'current page is {current_page}')
        ExcelHelp.add_arr_to_sheet(file_name=result_save_file, sheet_name=result_save_sheet, dim_arr=page_result)
        # 找到下一页的按钮，它在class为next-page的a标签里面
        set_currentPage()
        next_page = need_next_page()
        # 判断是否找到下一页的按钮
        if next_page:
            # 模拟点击下一页的按钮
            goto_nextPage()
            WaitHelp.waitfor_account_import(True, False)
            set_currentPage()
        else:
            # 如果没有找到下一页的按钮，说明已经爬取完所有的页码，跳出循环
            print(f"没有更多搜索结果，爬取结束。 current_page is:{current_page} total_page is: {total_page}")
            break


def change_money_ru(source_str: str):
    result = source_str.replace(' ', '')
    result = result.replace(',', '.')
    if result[-1] == '₽':
        result = result.replace('₽', '')
    elif result[-1] == '$':
        if result[0] == '0':
            result = result.replace('$', '')
        else:
            return source_str
    elif result[-1] == '€':
        if result[0] == '0':
            result = result.replace('€', '')
        else:
            return source_str
    else:
        result = result[:-1]
    if result.__len__() > 0:
        result = float(result.replace(' ', ''))
    return result


def close_alert():
    try:
        close_buttons = driver.find_elements(By.CSS_SELECTOR, 'button.button-red.refresh-button')
        if close_buttons.__len__() > 0:
            close_buttons[0].click()
            time.sleep(60.0)
    except Exception as e:
        print('close_alert error')
        # print(e)


def pre_deal_excel(date):
    global result_save_file
    result_save_file = PathHelp.get_file_path('Tender', f'tender_contract_{date}.xlsx')
    ExcelHelp.create_excel_file(result_save_file)
    title_arr = [['Contract_No',"Purchase_No", 'title', 'contract_price', 'contract_security', 'status', 'published',
                  'signature_data', 'deadline', 'org_name', 'org_TinKpp', 'org_contact', 'cus_name', 'cus_TinKppReg',
                  'cus_contact', 'cus_address', 'supplier_name', 'supplier_TinKpp', 'supplier_tel', 'detail_url',
                  'page']]
    ExcelHelp.add_arr_to_sheet(result_save_file, result_save_sheet, title_arr)


if __name__ == "__main__":
    index = -3 # -2 finished
    dateArr = ExcelHelp.read_sheet_content_by_name(file_name=PathHelp.get_file_path('Tender', 'contract.xlsx'), sheet_name='contract_url')
    row_content = dateArr[index]
    date = row_content[0]
    start_url = row_content[1]
    pre_deal_excel(date)
    driver.get(start_url)
    WaitHelp.waitfor_account_import(True, False)
    skip_login()
    time.sleep(2.0)
    set_total_page()
    main()
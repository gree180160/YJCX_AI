#  记录Task 提供的型号，在IC 中的库存信息
import base64
import math

from selenium.webdriver.common.by import By
import time
import undetected_chromedriver as uc
import ssl
from WRTools import ExcelHelp, WaitHelp, PathHelp, EmailHelper, StringHelp


ssl._create_default_https_context = ssl._create_unverified_context
# 定义要爬取的url

start_url = "https://www.rts-tender.ru/poisk/search?id=8b71e6d8-7228-4756-8e68-0ed9a8251e68"
result_save_file = PathHelp.get_file_path('Tender', 'Task.xlsx')
result_save_sheet = 'Sheet'
grade = 'A'

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
        total_data = driver.find_elements(By.CSS_SELECTOR, 'b.main-tabs__count.count')[1].text
        total_data = total_data.replace(' ', '')
        total_page = math.ceil(int(total_data)/10)
    except:
        total_page = 0
        print(f'{driver.current_url} ; set_total_page error')


def set_currentPage():
    global current_page
    try:
        page_area = driver.find_element(By.CSS_SELECTOR, 'div.pagination')
        current_page_ele = page_area.find_elements(By.CSS_SELECTOR, 'span.current')[-1]
        current_page = int(current_page_ele.text)
    except:
        current_page = total_page
        print(f'{driver.current_url} ; set_currentPage error')


def need_next_page():
    if int(current_page) < int(total_page):
        return True
    return False


def goto_nextPage():
    try:
        next_ele = driver.find_element(By.CSS_SELECTOR, 'a.page-link.next')
        driver.execute_script("arguments[0].click();", next_ele)
    except:
        print(f'{driver.current_url} ; goto_nextPage error')



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
                No = temp_item.find_elements(By.CSS_SELECTOR, 'a.link')[-1].text
                No = No.replace('Закупка №', '')
                No = No.replace('в ЕИС', '')
                more_url = temp_item.find_element(By.CSS_SELECTOR, 'a.button-red').get_attribute("href")
                row_titleRU = temp_item.find_element(By.CSS_SELECTOR, 'div.card-item__title').text
                # head
                start_pri = app_secu = contr_secu = status = '--'
                cells = temp_item.find_elements(By.CSS_SELECTOR, 'div.card-item__properties-cell')
                for (cell_index, tempCell) in enumerate(cells):
                    title_ele = tempCell.find_elements(By.CSS_SELECTOR, 'div.card-item__properties-name')
                    if title_ele.__len__() > 0:
                        title = title_ele[0].text
                        PSS_value = tempCell.find_element(By.CSS_SELECTOR, 'div.card-item__properties-desc').text
                        if title == 'НАЧАЛЬНАЯ ЦЕНА':
                            start_pri = PSS_value
                        elif title == 'ОБЕСПЕЧЕНИЕ ЗАЯВКИ':
                            app_secu = PSS_value
                        elif title == 'ОБЕСПЕЧЕНИЕ КОНТРАКТА':
                            contr_secu = PSS_value
                        elif title == 'СТАТУС':
                            status = PSS_value
                # date
                try:
                    publish_date = temp_item.find_element(By.CSS_SELECTOR, 'div.card-item__info').text
                    publish_date = publish_date.replace('Опубликовано: ', '')
                except:
                    publish_date = '--'
                try:
                    end_date = temp_item.find_element(By.CSS_SELECTOR, 'div.card-item__info-end-date').text
                    end_date = end_date.replace('Подать заявку до: ', '')
                except:
                    end_date = '--'
                try:
                    show_date = temp_item.find_element(By.CSS_SELECTOR, 'div.card-item__info-auction-time').text
                    show_date = show_date.replace('Дата проведения: ', '')
                except:
                    show_date = '--'
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
                item_content = [grade, No, row_titleRU, change_money_ru(start_pri), change_money_ru(app_secu), contr_secu.replace(' ', ''), status, publish_date, end_date, show_date,
                                org_name, org_tinKpp, org_contact_det, cus_name, cus_tinKppReg, cus_det, cus_address,
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
    sendEmail(result_save_file)


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


def sendEmail(result_file):
    EmailHelper.sendAttachment(result_save_file, 'Tender_info_A')


def close_alert():
    try:
        close_buttons = driver.find_elements(By.CSS_SELECTOR, 'button.button-red.refresh-button')
        if close_buttons.__len__() > 0:
            close_buttons[0].click()
            time.sleep(60.0)
    except Exception as e:
        print('close_alert error')
        # print(e)


def adjust_excel():
    global result_save_file
    today = time.strftime('%Y-%m-%d', time.localtime())
    result_save_file = PathHelp.get_file_path('Tender', f'tender_info_{today}_{grade}.xlsx')
    ExcelHelp.create_excel_file(result_save_file)
    title_arr = [
        ['grade', 'No', 'title_ru', 'starting_price', 'application_security', 'contract_security', 'status', 'published',
         'apply_data', 'show_data', 'org_name', 'org_TinKpp', 'org_contact', 'cus_name', 'cus_TinKppReg', 'cus_contact',
         'cus_address', 'detail_url', 'page']]
    ExcelHelp.add_arr_to_sheet(result_save_file, result_save_sheet, title_arr)


if __name__ == "__main__":
    driver.get(start_url)
    WaitHelp.waitfor_account_import(True, False)
    adjust_excel()
    skip_login()
    time.sleep(2.0)
    set_total_page()
    main()
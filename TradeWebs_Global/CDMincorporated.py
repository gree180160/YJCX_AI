# waldom
import ssl
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp, ChromeDriverManager
from Manager import AccManage
import time


ssl._create_default_https_context = ssl._create_unverified_context
try:
    driver = ChromeDriverManager.getWebDriver(0)
except Exception as e:
    print(e)

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TCDMincroporated.xlsx'),
                  'sourceSheet': 'source',
                  'colIndex': 1,
                  'startIndex': 3,
                  'endIndex': 10}
task_name = 'TCDMincorporated'
default_url = 'https://www.cdmincorporated.com/zh-hans'
login_url = 'https://www.cdmincorporated.com/zh-hans/account/login'
accouts_arr = [AccManage.cdmine['n'], AccManage.cdmine['p']]
current_page = 1
total_page = 1


# 获取当前页面的数据
def get_page_data(url, index):
    # [model, manufacturer, price, stock_status, stock, current_page]
    print(f'current_page is {current_page}  total_page is {total_page}')
    product_list = driver.find_elements(By.CSS_SELECTOR, 'product-card.card--product')
    page_data = []
    for product in product_list:
        try:
            product_area = product.find_element(By.CSS_SELECTOR, 'div.card__info.w-full')
            model = product_area.find_element(By.CSS_SELECTOR, 'p.card__title').text
            manufacturer = product_area.find_element(By.CSS_SELECTOR, 'p.card__vendor').text
            price_area = product_area.find_element(By.CSS_SELECTOR, 'span.price__current')
            price = price_area.find_elements(By.TAG_NAME, 'span')[1].text
            try:
                stock_info = product_area.find_element(By.CSS_SELECTOR, 'div.product-inventory__status').text
                stock_status = stock_info.split('(')[0].strip('\n').strip()  # 去除换行和空格
                stock = stock_info.split('(')[1].replace(')', '').strip()  # 去除括号和空格
                stock = stock.replace("个单位", '')
            except:
                stock_status = '无货'
                stock = '0'
            item = [model, manufacturer, price, stock_status, stock, current_page]
            print(f'index: {index}  model: {model}  manufacturer: {manufacturer}  price: {price} stock_stauts: {stock_status} stock: {stock}')
            page_data.append(item)
        except:
            continue
            print('item empty')
    if len(page_data) > 0:
        ExcelHelp.add_arr_to_sheet(sourceFile_dic['fileName'], 'result2', page_data)
    else:
        print('no data')


def go_to_manu(url, index):
    global current_page, total_page
    if index == 200:
        current_page = 8
        total_page = 891
    else:
        current_page = 1
        total_page = 1
    while str(url).__len__() > 0 and current_page <= total_page:
        if str(url).__contains__('filter.v.price.gte=3'):
            new_url = f'{url}&page={current_page}'
        else:
            new_url = f'{url}?page={current_page}'
        driver.get(new_url)
        WaitHelp.waitfor(True, False)
        setterTotalPage(url, index)
        get_page_data(url, index)
        current_page += 1


def setterTotalPage(url, index):
    global total_page
    try:
        pageArea = driver.find_element(By.CSS_SELECTOR, 'ul.pagination')
        page_items = pageArea.find_elements(By.TAG_NAME, 'li')
        if page_items.__len__() >= 4:
            page_last = page_items[-2]
            total_page = int(page_last.text)
        else:
            total_page = 1
    except:
        total_page = 1
    total_page = min(total_page, 30)


def login():
    driver.get(login_url)
    WaitHelp.waitfor(True, True)
    form = driver.find_element(By.ID, 'customer_login')
    username = form.find_element(By.ID, 'customer-email')
    username.clear()
    username.send_keys(accouts_arr[0])
    time.sleep(2)
    password = form.find_element(By.ID, 'customer-password')
    password.clear()
    password.send_keys(accouts_arr[1])
    time.sleep(2)

    form.find_element(By.TAG_NAME, 'button').click()
    WaitHelp.waitfor(True, True)
    WaitHelp.waitfor(True, False)


def main():
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    for (index, url) in enumerate(all_manu):
        while WaitHelp.isSleep_time():
            time.sleep(60 * 5)
        if index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'url is: {url}  manu_name is: {index}')
            go_to_manu(url, index)


if __name__ == "__main__":
    driver.get(default_url)
    time.sleep(60)
    login()
    WaitHelp.waitfor(True, False)
    main()
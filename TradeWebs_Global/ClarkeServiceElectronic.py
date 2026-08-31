# clarke&service electronic solution
import ssl
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp, ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time


ssl._create_default_https_context = ssl._create_unverified_context
try:
    driver = ChromeDriverManager.getWebDriver(0)
except Exception as e:
    print(e)

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TClarkeService.xlsx'),
                  'sourceSheet': 'source',
                  'colIndex': 1,
                  'startIndex': 1,
                  'endIndex': 10}
task_name = 'TClarkeService'
home_url = 'https://www.csesolutions.com.au/'
default_url = 'https://www.csesolutions.com.au/product/'

current_page = 1
total_page = 1


# 获取当前页面的数据
def get_page_data():
    # [model, manufacturer, price, stock, MOQ, des]
    page_result = []
    try:
        product_list = driver.find_elements(By.CSS_SELECTOR, 'div.conxall_product_wrapp.tba_inner_wrapp')
        for product in product_list:
            model = manufacturer = price = stock = MOQ = des = ""
            try:
                inner = product.find_element(By.CSS_SELECTOR, 'div.tba_inner')
                model = inner.find_element(By.CSS_SELECTOR, 'h6.pr_part_number').text  # 型号
                info = inner.find_element(By.CSS_SELECTOR, 'h3.mb-1').text
                manufacturer = info.split()[0]  # 厂商
                des = ' '.join(info.split()[1:])  # 描述
                price_info = inner.find_element(By.CSS_SELECTOR, 'h5.mt-0.mb-2').text
                price = re.sub(r'\([^)]*\)', '', price_info).strip()  # 价格
                stock = inner.find_elements(By.CSS_SELECTOR, 'h5.my-3.mx-3')[1].text.replace('In Stock: ', '').strip()  # 库存
                MOQ = inner.find_elements(By.CSS_SELECTOR, 'h5.my-3.mx-3')[0].text.replace('MOQ: ', '').strip()  # 最小起订量
            except Exception as e:
                print(f"item info error: {e}")
            item = [model, manufacturer, price, stock, MOQ, des]
            page_result.append(item)
        if page_result.__len__() > 0:
            print(page_result)
            ExcelHelp.add_arr_to_sheet(sourceFile_dic['fileName'], 'result', page_result)
        else:
            print('no data')
    except Exception as e:
        print(e)


def go_to_manu():
    global current_page, total_page
    driver.get(default_url)
    WaitHelp.waitfor(True, False)
    setFilter()
    WaitHelp.waitfor(True, False)
    setterTotalPage()
    get_page_data()
    while str(default_url).__len__() > 0 and current_page <= total_page:
        try:
            go_next_page()
        except Exception as e:
            print(f"操作出错：{e}")


def go_next_page():
    global current_page, total_page
    if current_page <= total_page:
        try:
            # 方式1：直接滑动到页面底部（最常用）
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(20.0)
            # 1. 定位当前页（带有current类的a标签）
            current_page_ele = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.pagination_list li a.current"))
            )
            current_li = current_page_ele.find_element(By.XPATH, "./parent::li")
            # 再找下一个兄弟li元素
            next_li = current_li.find_element(By.XPATH, "./following-sibling::li[1]")

            # 3. 定位下一页的a标签并点击（确保可点击）
            next_page = WebDriverWait(next_li, 10).until(
                EC.element_to_be_clickable((By.TAG_NAME, "a"))
            )
            next_page.click()
            print(f"开始 {current_page + 1} 页")
            WaitHelp.waitfor(True, False)
            WaitHelp.waitfor(True, False)
            current_page += 1
            get_page_data()
        except Exception as e:
            print(f"操作出错：{e} current page is: {current_page}")
            time.sleep(30.0)


def setterTotalPage():
    global total_page
    try:
        # 方式1：直接滑动到页面底部（最常用）
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(20.0)
        pageArea = driver.find_element(By.CSS_SELECTOR, 'ul.ul_list.pagination_list')
        page_items = pageArea.find_elements(By.TAG_NAME, 'li')
        page_last = page_items[-2]
        total_page = int(page_last.text)
    except:
        print('total page error')
        total_page = 1
    print(f'total page is  {total_page}')


def setFilter():
    #in stock
    try:
        checkbox_in_stock = driver.find_element(By.ID, "in_stockqty")
        checkbox_in_stock.click()
        print('设置in stock 成功')
    except:
        print('请手动设置in stock')
    time.sleep(20)
    print('请手动设置 page count')
    time.sleep(20)
    # #page count
    # page_count = driver.find_element(By.ID, "post_per_page")
    # page_count.click()
    # time.sleep(2)
    #
    # shadow_root = driver.execute_script("return arguments[0].shadowRoot", page_count)
    # # 3. 在shadow-root中定位包含"192"的选项并点击
    # option_192 = WebDriverWait(shadow_root, 10).until(
    #     EC.element_to_be_clickable((By.XPATH, ".//option[contains(text(), '192')]"))
    # )
    # option_192.click()
    # time.sleep(2)


def main():
    go_to_manu()


if __name__ == "__main__":
    driver.get(home_url)
    time.sleep(60)
    WaitHelp.waitfor(True, False)
    main()
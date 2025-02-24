import ssl
import sys
from selenium.webdriver.common.by import By
from WRTools import ChromeDriverManager
from WRTools import ExcelHelp, LogHelper, PathHelp, WaitHelp, MySqlHelp_recommanded, EmailHelper
from Manager import AccManage, URLManager
import time
from PIL import Image
import io
import base64
from selenium.webdriver.common.keys import Keys
import random

ssl._create_default_https_context = ssl._create_unverified_context

driver = ChromeDriverManager.getWebDriver(0)

accouts_arr = AccManage.oc_stock1

default_url = 'https://octopart.com/'

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TInfineonPowerManger.xlsx'),
                  'sourceSheet': 'ppn2',
                  'colIndex': 1,
                  'startIndex': 168,
                  'endIndex': 238}
task_name = 'TInfineonPowerManger'

log_file = PathHelp.get_file_path('Octopart_price', 'ocopar_price_log.txt')


#  请求频繁，导致出现弹框，有则关闭，无则异常
def close_alert():
    try:
        close_button = driver.find_element(by=By.CLASS_NAME, value='jsx-535551409.close-button')
        close_button.click()
    except Exception as e:
        print(e)
        return


# 解析某个型号的页面信息，如果有更多，直接点击，然后只选择start ， 遇到第一个不是star 的就返回
def analy_html(pn_index, pn):
    scroll_height = 5.0 + random.uniform(1, 10)
    driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_height)
    time.sleep(random.uniform(1, 5))
    try:
        all_cates_list = driver.find_elements(By.CSS_SELECTOR, '[data-testid="prices-view-part"]')
        # 获取价格和库存信息，所以只需要第一个型号
        first_result = all_cates_list[0]
        header = first_result.find_element(By.CSS_SELECTOR, '[data-testid="part-header"]')

        part_manu = header.find_element(By.CSS_SELECTOR, '[data-testid="serp-part-header-manufacturer"]').text
        part_number = header.find_element(By.CSS_SELECTOR, '[data-testid="serp-part-header-mpn"]').text
        part_des = header.find_element(By.CSS_SELECTOR, '[data-sentry-component="Description"]').text
        link = header.find_element(By.CSS_SELECTOR, '[data-testid=serp-part-header-mpn-link]')

        tbody = first_result.find_element(By.CSS_SELECTOR, '[data-testid="offer-table-body"]')
        supplier_list = tbody.find_elements(By.TAG_NAME, 'tr')
        min_index = -1
        min_value = sys.float_info.max
        for (temp_index, temp_supplier) in enumerate(supplier_list):
            k_pirce = temp_supplier.find_elements(By.TAG_NAME, 'td')[11].text
            try:
                temp_price = float(k_pirce)
            except:
                temp_price = sys.float_info.max
            if temp_price < min_value:
                min_value = temp_price
                min_index = temp_index
        if min_index >= 0: # 有价格信息
            min_distribute_info = supplier_list[min_index]
            distribute = min_distribute_info.find_elements(By.TAG_NAME, 'td')[1].text
            stock = min_distribute_info.find_elements(By.TAG_NAME, 'td')[4].text
            kprice_type = min_distribute_info.find_elements(By.TAG_NAME, 'td')[7].text
            kprice = temp_supplier.find_elements(By.TAG_NAME, 'td')[11].text
            kprice = kprice.replace("*", "")
        else:
            distribute = stock = kprice = kprice_type = ''
        #get base64
        try:
            stock_pic = getBase64(link)
        except Exception as e:
            LogHelper.write_log(log_file_name=log_file, content=f'{pn} 没有历史库存记录 ')
            stock_pic = ''
        #(ppn, manu, des, distribute, stock, currency_type, k_price, stock_pic, opn, task_name)
        info = [part_number, part_manu, part_des, distribute, stock, kprice_type, kprice, stock_pic, pn, task_name]
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{pn} 页面 解析异常：{e} ')
    MySqlHelp_recommanded.DBRecommandChip().octopart_market_write([info])


def getBase64(a_link):
    a_link.click()
    WaitHelp.waitfor(True, False)
    # 找到 nav 元素
    nav = driver.find_elements(By.TAG_NAME, 'nav')[1]  # 确保获取到正确的 nav 元素
    # header = driver.find_element()
    # 找到目标元素
    inventory_his = driver.find_element(By.CSS_SELECTOR, '[data-testid="inventory-history"]')
    # 获取 nav 的底部位置
    nav_location = nav.location['y']  # nav 元素的 y 坐标
    nav_height = nav.size['height']  # nav 元素的高度
    nav_bottom = nav_location + nav_height  # nav 的底部位置
    # 获取 inventory_his 的顶部位置
    inventory_his_location = inventory_his.location['y']  # inventory_his 元素的 y 坐标
    # 计算需要滚动的高度，使 inventory_his 顶部对齐到 nav 的底部
    scroll_height = inventory_his_location - nav_bottom
    # 滚动页面
    driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_height)
    time.sleep(1)  # 等待滚动完成

    # 获取该元素的截图并保存
    screenshot_path = 'inventory_history_screenshot.png'
    inventory_his.screenshot(screenshot_path)

    # 用PIL处理图片以减小体积
    # 加载图片
    image = Image.open(screenshot_path)
    # 降低图片质量到原来的1/4 (例如: 原始质量为100，调整为25)
    quality = 25  # 调整质量，您可以根据需要进行更改
    # 保存图片到BytesIO对象
    buffered = io.BytesIO()
    image.save(buffered, format="PNG", quality=quality)
    # 获取图片的字节内容
    image_bytes = buffered.getvalue()
    # 转换为Base64编码
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    return image_base64


# 验证是否处于验证IP 页面
def is_security_check() -> bool:
    # 400：Bad Request
    if driver.title == 'Please complete the security check - Octopart':
        result = True
        EmailHelper.mail_ip_error(AccManage.Device_ID)
    else:
        result = False
    return result


def main():
    all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    for (ppn_index, ppn) in enumerate(all_cates):
        if ppn is None or ppn.__contains__('?'):
            continue
        elif ppn_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'ppn_index is: {ppn_index}  pn is: {ppn}')
            url = URLManager.octopart_get_code_url(ppn, 1, "")
            driver.get(url)
            if ppn_index > 0 and ppn_index % 15 == 0:
                time.sleep(10*60)
            else:
                WaitHelp.waitfor_octopart(True, False)
            while True:
                if is_security_check():
                    time.sleep(60+random.uniform(1, 10))
                    print('is security ip')
                else:
                    break

            analy_html(ppn_index, ppn)


def login():
    login_span = driver.find_element(By.CSS_SELECTOR, 'span.truncate')
    login_span.click()
    time.sleep(15.0+random.uniform(1, 10))
    altiumAuthButton = driver.find_element(By.CSS_SELECTOR, "[data-sentry-component='AltiumAuthButton']")
    altiumAuthButton.click()
    time.sleep(18.0 + random.uniform(2, 15))

    email_input = driver.find_element(By.CSS_SELECTOR, "[data-locator='signin-email']")
    email_input.clear()
    time.sleep(3.0 + random.uniform(1, 10))
    email_input.send_keys(accouts_arr[0])
    time.sleep(2.0 + random.uniform(1, 10))
    pw_input = driver.find_elements(By.CSS_SELECTOR, "[data-locator='signin-password']")[1]
    pw_input.clear()
    time.sleep(2.5 + random.uniform(1, 10))
    pw_input.send_keys(accouts_arr[1])
    time.sleep(3.5 + random.uniform(1, 10))
    # 定位到内容为 "Sign In" 的 <span> 元素
    login_btn = driver.find_element(By.CSS_SELECTOR, "[data-locator='signin-submit']")
    # 对找到的元素执行操作，例如点击
    login_btn.click()
    time.sleep(60.0+random.uniform(5, 15))


if __name__ == "__main__":
    driver.get(default_url)
    time.sleep(90.0+random.uniform(1, 10))
    login()
    main()

# 硬之城
import ssl
from WRTools import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp
import time

ssl._create_default_https_context = ssl._create_unverified_context


driver_option = webdriver.ChromeOptions()
driver = ChromeDriverManager.getWebDriver(1)
driver.set_page_load_timeout(480)

default_url = 'https://www.allchips.com/'


result_save_file = PathHelp.get_file_path('TradeWebs', 'AllChips.xlsx')
log_file = PathHelp.get_file_path('TradeWebs', 'log.txt')
current_page = 1
total_page = 0


# 获取当前页面的数据
def get_page_data(manu_id):
    result = []
    print(f'manu_id is: {manu_id} current page is :{current_page} total page is :{total_page}')
    product_models = driver.find_element(By.ID, 'listTable').find_elements(By.TAG_NAME, 'tr')
    for model in product_models:
        ppnInfo = []
        try:
            # ppn, manu,des, stock, date_line, moq, mpq, maq, batch, price
            ppn = model.find_element(By.CSS_SELECTOR, 'a.partNumber').text
            manu = model.find_element(By.CSS_SELECTOR, 'div.brand-info').text.replace('品牌：', '')
            des = model.find_element(By.CSS_SELECTOR, 'div.category').text.replace('品类：', '')
            stock = model.find_element(By.CSS_SELECTOR, 'div.stock-info').text.replace('库存：', '')
            mpq = model.find_element(By.CSS_SELECTOR, 'div.mpq-info').text.replace('最小包:', '')
            moq = model.find_element(By.CSS_SELECTOR, 'div.moq-info').text.replace('起订量:', '')
            maq = model.find_element(By.CSS_SELECTOR, 'div.multiple-info').text.replace('递增量:', '')
            price_info = model.find_elements(By.CSS_SELECTOR, 'div.price-cell')
            if price_info.__len__() > 1:
                price_div = price_info[-2]
            else:
                price_div = price_info[0]
            price_amount = price_div.find_element(By.CSS_SELECTOR, 'div.amount-td').text
            price = price_div.find_element(By.CSS_SELECTOR, 'div.cnprice-td').text.replace('￥', '')
            date_line = model.find_element(By.CSS_SELECTOR, 'label.cn-delivery').text
            ppnInfo = [ppn, manu, des, mpq, moq, maq, stock, price_amount, price, date_line]
        except Exception as e:
            print('get_page_data error : {e}')
        result.append(ppnInfo)
    # 保存数据到CSV
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'allchips', result)


def go_to_manu(manuID):
    global current_page
    time.sleep(2.0)
    new_url = f'https://www.allchips.com/topics/stock?brandId={manuID}&page=1'
    driver.get(new_url)
    WaitHelp.waitfor_account_import(True, False)
    setTotal_page()
    current_page = 1
    while current_page <= total_page:
        get_page_data(manuID)
        if current_page == total_page:
            break;
        else:
            go_nextPage(manuID)


def setTotal_page():
    global total_page
    try:
        pages_area = driver.find_element(By.CSS_SELECTOR, 'div.page-nav.fl')
        pages_str = pages_area.find_elements(By.TAG_NAME, 'span')[-1].text
        total_page = min(int(pages_str), 20)
    except:
        print('get total_page error')
        total_page = 1 # 只有一页，不显示页数
        driver.get(default_url)
        time.sleep(10.0)


def go_nextPage(manu_id):
    global current_page
    new_url = f'https://www.allchips.com/topics/stock?brandId={manu_id}&page={current_page+1}'
    driver.get(new_url)
    WaitHelp.waitfor_account_import(True, False)
    current_page += 1


def main():
    # 'https://www.allchips.com/topics/stock?brandId=5_4_14_1_2_68_39_62_84_25_125'
    manus = [125]
    for temp_id in manus:
        go_to_manu(temp_id)


if __name__ == "__main__":
    driver.get(default_url)
    WaitHelp.waitfor_octopart(False, False)
    main()

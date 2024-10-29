# 易洛蒙
import math
import ssl
from WRTools import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp
import time
import undetected_chromedriver as uc
from undetected_chromedriver import ChromeOptions

ssl._create_default_https_context = ssl._create_unverified_context


driver_option = webdriver.ChromeOptions()
driver = uc.Chrome(use_subprocess=True, options=driver_option)
driver.set_page_load_timeout(480)
default_url = 'https://cn.element14.com/w/search/prl/results?gs=true&ICID=I-CT-LP-GET-MORE-FOR-LESS-ALL_PRODS-MAY_23-WF3726510&st=clearance_cn&range=inc-in-stock-grp'


result_save_file = PathHelp.get_file_path('TradeWebs', 'Element14.xlsx')
log_file = PathHelp.get_file_path('TradeWebs', 'log.txt')
current_page = 1
total_page = 0


# 获取当前页面的数据
def get_page_data():
    result = []
    print(f' current page is :{current_page} total page is :{total_page}')
    tdody = driver.find_element(By.CSS_SELECTOR, 'tbody.ProductListerTablestyles__TableBody-sc-j76asa-8.gzQcRy')
    product_models = tdody.find_elements(By.CSS_SELECTOR, 'tr.ProductListerTablestyles__TableRow-sc-j76asa-5.jMKtrG')
    for model in product_models:
        ppnInfo = []
        try:
            # ppn, manu,des, stock, date_line, moq, mpq, maq, batch, price
            ppn = model.find_element(By.CSS_SELECTOR, 'div.ManufacturerPartNoTableCellstyles__PartNumber-sc-9z3ajz-3.bqtnlz').text
            manu = model.find_element(By.CSS_SELECTOR, 'div.ProductDescriptionTableCellstyles__ProductValue-sc-p80ycp-1.egCVvG').text
            des = model.find_element(By.CSS_SELECTOR, 'a.ProductDescriptionTableCellstyles__ProductLink-sc-p80ycp-3.cHFrJJ').text
            stock = model.find_element(By.CSS_SELECTOR, 'div.AvailabilityPrimaryStatusstyles__StatusMessage-sc-101ypue-2.hkxOec').text.replace('有货', '')
            mpq = model.find_element(By.CSS_SELECTOR, 'div.PriceForTableCellstyles__ProductValue-sc-1eyeov0-2.cNJAua').text
            moq = model.find_element(By.CSS_SELECTOR, 'div.QuantityAddToBasketTableCellstyles__QuantityWrapper-sc-x5d4mf-3.jbnsOC').text.split(' / ')[0].replace('最少：', '')
            maq = model.find_element(By.CSS_SELECTOR, 'div.QuantityAddToBasketTableCellstyles__QuantityWrapper-sc-x5d4mf-3.jbnsOC').text.split(' / ')[1].replace('多个：', '')
            price_info = model.find_element(By.CSS_SELECTOR, 'td.ProductListerTablestyles__TableCell-sc-j76asa-9.hAmTOz.PRICE')
            price_list = price_info.find_elements(By.CSS_SELECTOR, 'div.PriceBreakupTableCellstyles__PriceBreak-sc-ylr3xn-4.dvzRdf')
            max_price = price_list[0]
            max_price_amount = max_price.find_element(By.CSS_SELECTOR,
                                                  'span.PriceBreakupTableCellstyles__BaseQuantity-sc-ylr3xn-3.kRBVsh').text
            max_price_str = max_price.find_element(By.CSS_SELECTOR,
                                           'span.PriceBreakupTableCellstyles__Price-sc-ylr3xn-6.jsjSzn').text.replace('(', '').replace(')', '').replace('CNY', '')
            if price_list.__len__() > 1:
                min_price = price_list[-1]
                min_price_amount = min_price.find_element(By.CSS_SELECTOR, 'span.PriceBreakupTableCellstyles__BaseQuantity-sc-ylr3xn-3.kRBVsh').text
                min_price_str = min_price.find_elements(By.CSS_SELECTOR, 'span.PriceBreakupTableCellstyles__Price-sc-ylr3xn-6.jsjSzn')[-1].text.replace('(', '').replace(')', '').replace('CNY', '')
            else:
                min_price_amount = '/'
                min_price_str = '/'
            date_line = model.find_element(By.CSS_SELECTOR, 'div.InStockStatusstyles__AddtionalText-sc-7bt2a-2.gKWJJq').text
            ppnInfo = [ppn, manu, des, mpq, moq, maq, stock, max_price_amount, max_price_str, min_price_amount, min_price_str, date_line]
        except Exception as e:
            print('get_page_data error : {e}')
        result.append(ppnInfo)
    # 保存数据到CSV
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(result_save_file, 'element14_other', result)


def go_to_manu():
    time.sleep(2.0)
    WaitHelp.waitfor_account_import(True, False)
    setTotal_page()
    while current_page <= total_page:
        get_page_data()
        if current_page == total_page:
            break;
        else:
            go_nextPage()


def setTotal_page():
    global total_page
    try:
        pages_area = driver.find_element(By.CSS_SELECTOR, 'div.ProductCategoryTemplatestyles__SearchResultWrapper-sc-1he9gtv-6.ejYNRN')
        pages_str = pages_area.find_element(By.TAG_NAME, 'span').text.replace(',','')
        total_page = math.ceil(int(pages_str)/50)
    except:
        print('get total_page error')
        total_page = 0
        driver.get(default_url)
        time.sleep(10.0)


def go_nextPage():
    global current_page
    page_button_area = driver.find_element(By.CSS_SELECTOR, 'div.bx--pagination__control-buttons')
    next_page_button = page_button_area.find_elements(By.TAG_NAME, 'button')[-1]
    next_page_button.click()
    WaitHelp.waitfor_account_import(True, False)
    current_page += 1


def main():
    go_to_manu()


if __name__ == "__main__":
    driver.get('https://cn.element14.com')
    time.sleep(20)
    driver.get('https://cn.element14.com/infineon-cyw20822-9?ICID=I-HP-LB-INFINEON-CYW20822-AUG_24-WF3624160')
    time.sleep(10)
    driver.get('https://cn.element14.com/get-more-for-less?ICID=I-CT-SO-GET_MORE_LESS-JUL_24-WF3726510')
    time.sleep(10)
    driver.get('https://cn.element14.com/c/semiconductors-ics?st=clearance_cn&gs=true&ICID=I-CT-LP-GET-MORE-FOR-LESS-SEMIS_ICS-MAY_23-WF3726510')
    time.sleep(10)
    driver.get(default_url)
    WaitHelp.waitfor_octopart(False, False)
    time.sleep(2*60)
    main()

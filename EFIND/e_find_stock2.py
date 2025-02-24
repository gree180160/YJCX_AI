
#  记录Task 提供的型号，在efind中的库存信息
import time
from selenium.webdriver.common.by import By
from WRTools import ChromeDriverManager
import ssl
import datetime
from WRTools import ExcelHelp, WaitHelp, PathHelp, EmailHelper, MySqlHelp_recommanded, LogHelper


ssl._create_default_https_context = ssl._create_unverified_context

log_file = PathHelp.get_file_path('EFIND', 'e_find_log.txt')

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TInfineonPowerManger.xlsx'),
                  'sourceSheet': 'ppn2',
                  'colIndex': 1,
                  'startIndex': 100,
                  'endIndex': 120}
task_name = 'TInfineonPowerManger'

try:
    driver = ChromeDriverManager.getWebDriver(1)
except Exception as e:
    print(e)


#   二维数组，page 列表， table 列表
def analy_html(cate_index, cate_name, st_manu):
    input_area = driver.find_element(By.ID, 'sf')
    input_area.clear()
    input_area.send_keys(cate_name)
    btn = driver.find_element(By.CSS_SELECTOR, 'input.sbtn')
    btn.click()
    WaitHelp.waitfor(True, False)
    total_stock = 0
    check = driver.find_elements(By.ID, 'fbMan1')
    while check.__len__() > 0:
        time.sleep(10.0)
        print("check code")
        check = driver.find_elements(By.ID, 'fbMan1')
    # check code
    sresult = driver.find_element(By.ID, 'sresults')
    match = (sresult.find_element(By.CSS_SELECTOR, 'span.sterm').text == cate_name)
    while not match:
        driver.refresh()
        time.sleep(120)
        match = (sresult.find_element(By.CSS_SELECTOR, 'span.sterm').text == cate_name)
    try:
        get_supplier(cate_name, st_manu, total_stock)
    except Exception as e:
        LogHelper.write_log(log_file, f'analy_html error:{e}')


# 获取supplier 总揽
def get_supplier(ppn, manu, stock):


    try:
        isf = driver.find_element(By.ID, 'isf')
        total_sup = isf.find_element(By.CSS_SELECTOR, 'span.alls').text
        stock_sup = isf.find_element(By.CSS_SELECTOR, 'span.inss').text
        prf = driver.find_element(By.ID, 'prf')
        price_sup = prf.find_element(By.CSS_SELECTOR, 'span.prss').text
        price_stat = driver.find_element(By.ID, 'pricestat_data')
        mid_price = price_stat.find_elements(By.TAG_NAME, 'i')[0].text
        min_price = price_stat.find_elements(By.TAG_NAME, 'i')[1].text
        max_price = price_stat.find_elements(By.TAG_NAME, 'i')[2].text
        info = [ppn, manu, total_sup, price_sup, stock_sup, stock, mid_price, min_price, max_price, task_name]
        MySqlHelp_recommanded.DBRecommandChip().efind_supplier_write([info])
    except:
        print(f'{ppn} get_supplier error')


def convert_russian_date_to_chinese(russian_date):
    if russian_date.__contains__('только что'):
        current_date = datetime.datetime.now()
        # 格式化日期，确保月份和日期都是两位数
        formatted_date = current_date.strftime("%Y.%m.%d")
        return formatted_date
    elif russian_date.__contains__('20'):
        russian_date = russian_date.replace('Актуальность: ', '').strip()
        # 俄语月份与中文月份的映射
        month_mapping = {
            'января': '01',
            'февраля': '02',
            'марта': '03',
            'апреля': '04',
            'мая': '05',
            'июня': '06',
            'июля': '07',
            'августа': '08',
            'сентября': '09',
            'октября': '10',
            'ноября': '11',
            'декабря': '12'
        }
        # 分割日期字符串
        parts = russian_date.split()
        # 提取日期、月份和年份
        day = parts[0]  # 例如 '17'
        month = parts[1]  # 例如 'октября'
        year = parts[2]  # 例如 '2024'
        # 获取对应的月份数字
        month_number = month_mapping.get(month)
        # 生成中文日期格式
        chinese_date = f"{year}.{month_number}.{day}"
        return chinese_date
    return ''


def select_area():
    input_area = driver.find_element(By.ID, 'sf')
    input_area.clear()
    input_area.send_keys('LM7321MFX/NOPB')
    btn = driver.find_element(By.CSS_SELECTOR, 'input.sbtn')
    btn.click()
    time.sleep(15.0)
    #  WaitHelp.waitfor(True, False)
    city = driver.find_element(By.ID, 'filter_city')
    filter_button = city.find_element(By.CSS_SELECTOR, 'a.filter_button')
    filter_button.click()
    time.sleep(20.0)
    towns_list = driver.find_element(By.ID, 'towns_list')
    ru = towns_list.find_element(By.XPATH, "//a[contains(text(), 'Россия')]")
    ru.click()
    time.sleep(60.0)


def main():
    all_cates = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'], 2)
    for (cate_index, cate_name) in enumerate(all_cates):
        if cate_name.__contains__('?'):
            continue
        elif cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
            if cate_index % 7 == 0 and cate_index > 0:
                time.sleep(60*5)
            analy_html(cate_index, cate_name, all_manu[cate_index])

# [['LM35-23B05R2', 'mornsun', 'MORNSUN', 'Chang Ming International Technology Co., Limited', '2024.10.25', 'Дата изготовления:2023', '', '5000', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'Shenzhen Haoxinsheng Technology Co., Ltd', '2023.09.7', 'DC: within 2 years, NEW ORIGINAL\nДата изготовления:23+\nТип упаковки: Static-Free Vacuum T\nМинимальный заказ:1pcs', '', '6689', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'Mornsun', 'Триатрон', '2024.10.27', 'LM35-23B05R2, AC-DC преобразователь в корпусе, MORNSUN\nВ упаковке: 10 шт.\nМинимальный заказ:10 шт.', '10+ 1065.96 р.', '13', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'Энергофлот', '2024.10.28', 'Минимальный заказ:1', '1+ 1315.41 р.', '16', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'МирКомпонентов', '2024.10.28', 'AC/DC преобразователи корпусированные\nВ упаковке: 20\nМинимальный заказ:1', '1+ 1652.65 р.\n6+ 1449.69 р.\n120+ 1304.72 р.', '16', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'Контест', '2024.10.28', '', '1+ 1425.42 р.', '12', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'Триема', '2024.10.28', 'LM35-23B05R2. Товар в наличии. Доставк…раскрыть', '1+ 1213 р.', '26', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'ЗУМ-ЭК', '2024.10.5', 'AC/DC преобразователи корпусированные', '', '16', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'Интер Чип', '2024.10.28', '', '', '16', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'Электроник +', '2024.10.28', 'Минимальный заказ:1 штука', '1+ 1240.44 р.\n100+ 1088.11 р.\n1000+ 979.3 р.', '18', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'РИВ Электроникс', '2024.10.28', 'Минимум 1шт.\nМинимальный заказ:1', '1+ 1277 р.\n7+ 1093 р.\n130+ 883.8 р.', '0', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'Интерия ЭК', '2024.10.28', 'AC/DC преобразователи корпусированные', '1+ 915.64 р.', '0', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'АВЕОР', '2024.10.28', '', '168+ 836.09 р.', '0', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'НТК МОСТЭК', '2024.10.28', '', '10+ 975.58 р.', '0', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'Mornsun Guangzhou Science & Technology Co.', 'Берёзка Электронные Компоненты', '2024.10.28', 'AC/DC преобразователи корпусированные …раскрыть\nВ упаковке: 1\nМинимальный заказ:1', '', '0', 'Mornsun'], ['LM35-23B05R2', 'mornsun', '', 'База Электроники', '2024.10.28', 'Минимальный заказ:1', '1+ 1333.69 р.', '16', 'Mornsun'], ['LM35-23B05R2', 'mornsun', '', 'База Электроники', '2024.10.28', 'Минимальный заказ:1', '1+ 1786.24 р.', '16', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'Гамма-Компоненты', '2024.10.7', 'AC/DC преобразователи корпусированные\nМинимальный заказ:3', '1+ 11.73 $', '16', 'Mornsun'], ['LM35-23B05R2', 'mornsun', '', 'Фирма Миком', '2024.10.27', '', '1+ 1395.5 р.\n6+ 1178.78 р.\n20+ 1044.47 р.\n60+ 971.03 р.', '15', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'Светозар Компонент', '2024.10.28', 'Минимальный заказ:6', '', '16', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN Guangzhou S& T', 'Клик-ПРО', '2024.10.28', '', '', '1', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'АВЭЛКОМ', '2024.10.28', 'AC/DC преобразователи корпусированные\nВ упаковке: 20\nМинимальный заказ:1', '1+ 1265.27 р.\n20+ 1037.11 р.', '0', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'Элвек', '2024.10.28', 'Минимальный заказ:1', '1+ 1367.14 р.\n6+ 1066 р.\n120+ 835.48 р.', '0', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN', 'Промчип', '2024.10.21', '', '120+ 833.29 р.', '0', 'Mornsun'], ['LM35-23B05R2', 'mornsun', '', 'Элсин (Торгэлектроника)', '2024.10.27', 'Источники питания', '120+ 912.58 р.', '0', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'Mornsun Guangzhou Science & Technology Co., Ltd', 'Промэлектроника', '2024.10.28', '', '', '0', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'Mornsun Power', 'Элитан', '2024.10.28', '', '', '0', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'Mornsun Power', 'Элитан', '2024.10.28', '', '', '0', 'Mornsun'], ['LM35-23B05R2', 'mornsun', 'MORNSUN(金升阳)', 'Микротел компонент', '2024.10.28', '', '1+ 11.983 $', '104', 'Mornsun']]
# ['LM35-23B05R2', 'mornsun', '25', '18', '13', 12006, '1240.44 р.', '833.29 р.', '1786.24 р.', 'Mornsun']


if __name__ == "__main__":
    driver.get('https://efind.ru/')
    time.sleep(2.0)
    select_area()
    main()

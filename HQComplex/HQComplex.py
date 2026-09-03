# 华强网库存和指数一次性获取
import time

from WRTools import ExcelHelp, WaitHelp, PathHelp, LogHelper, Record_data, ChromeDriverManager, EmailHelper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import ssl
from Manager import AccManage, URLManager

log_file = PathHelp.get_file_path('HQComplex', 'HQComplexLog.txt')
ssl._create_default_https_context = ssl._create_unverified_context

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TRFBJT.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 19}
task_name = 'TRFBJT'

db = Record_data.RecordData()
accouts_arr = [AccManage.HQ_hot_1['n'], AccManage.HQ_hot_1['p']]
VerificationCodePage = 0
login_url = "https://passport.hqew.com/login"

driver = ChromeDriverManager.getWebDriver(1)
driver.set_window_size(height=800, width=1200)
current_cate_has_date = True


def login_action(aim_url):
    driver.get(login_url)
    if aim_url.__contains__(login_url):
        WaitHelp.waitfor_ICHot(False, False)
        # begin login
        driver.find_element(by=By.ID, value='J_loginName').clear()
        driver.find_element(by=By.ID, value='J_loginName').send_keys(accouts_arr[0])
        driver.find_element(by=By.ID, value='J_loginPsw').clear()
        driver.find_element(by=By.ID, value='J_loginPsw').send_keys(accouts_arr[1])
        WaitHelp.waitfor_ICHot(False, False)
        driver.find_element(By.ID, value='J_checkpripolicy_account').click() # 协议
        time.sleep(2.0)
        driver.find_element(by=By.ID, value='J_btnLogin').click()
        WaitHelp.waitfor(True, False)


# 验证当前页面是否正在等待用户验证，连续三次请求出现验证码页面，则关闭页面
def checkVerificationCodePage(ppn) -> bool:
    global VerificationCodePage
    if driver.find_element(By.TAG_NAME, 'body').text.__contains__('频繁') or driver.find_element(By.TAG_NAME, 'body').text.__contains__('访问太快了'):
        VerificationCodePage += 1
        print(f'{ppn} check code')
        EmailHelper.mail_HQ_hot(AccManage.Device_ID)
        result = True
    else:
        VerificationCodePage = 0
        result = False
    if VerificationCodePage >= 20:
        driver.close()
    return result


# 获取单个型号库存info
def getSupplierInfo(cate_name, manu):
    result = []
    tables = driver.find_elements(By.CSS_SELECTOR, 'table.list-table')
    if tables.__len__() > 1:
        info_table = tables[1]
        tr_arr = info_table.find_elements(By.TAG_NAME, 'tr')
        for (index, tr_info) in enumerate(tr_arr):
            yzpms = tr_info.find_elements(By.CSS_SELECTOR, 'a.icon-yzpm')
            yzs = tr_info.find_elements(By.CSS_SELECTOR, 'a.i-yuan')
            if yzpms.__len__() > 0 or yzs.__len__() > 0:
                row_info = get_saveSupplierInfo(cate_name, manu, tr_info)
                if row_info.__len__() > 0:
                    result.append(row_info)
    return result


# ppn, std_manu, supplier, sup_manu, batch, stock, packing, param, place, instruction, publish_date, task_name
def get_saveSupplierInfo(ppn, manu, tr):
    try:
        supplier_name = tr.find_element(By.CSS_SELECTOR, 'a.company.company-cinfo-click').text
    except:
        supplier_name = ''
    try:
        sup_ppn = tr.find_element(By.CSS_SELECTOR, 'td.td-model').find_element(By.TAG_NAME, 'a').text # todo, 数据库
    except:
        sup_ppn = ''
    try:
        sup_manu = tr.find_element(By.CSS_SELECTOR, 'td.td-brand').text
    except:
        sup_manu = ''
    try:
        batch = tr.find_element(By.CSS_SELECTOR, 'td.td-pproductDate').text
    except:
        batch = ''
    try:
        stock_tr = tr.find_element(By.CSS_SELECTOR, 'td.td-stockNum')
        stock = stock_tr.find_element(By.TAG_NAME, 'p').text
    except:
        stock = ''
    try:
        packing = tr.find_element(By.CSS_SELECTOR, 'td.td-ppackage').text
    except:
        packing = ''
    try:
        param = tr.find_element(By.CSS_SELECTOR, 'td.td-param').text
    except:
        param = ''
    try:
        place = tr.find_element(By.CSS_SELECTOR, 'td.td-storeLocation').text
    except:
        place = ''
    try:
        instruction = tr.find_element(By.CSS_SELECTOR, 'td.td-premark').text
    except:
        instruction = ''
    try:
        publish_date = tr.find_elements(By.TAG_NAME, 'td')[-2].text
    except:
        publish_date = ''
    result = [ppn, manu, supplier_name, sup_ppn, sup_manu, batch, stock, packing, param, place, instruction, publish_date, task_name]
    return result


#  #search info#
def has_hotData() -> bool:
    nodatas_areas = driver.find_elements(By.CSS_SELECTOR, 'div.no-data')
    if nodatas_areas.__len__() > 0:
        return False
    return True


def get_echar_data(char_id) -> []:
    result = []

    # 2. 等待目标图表容器加载
    # 3. 等待ECharts实例初始化和系列数据加载完成
    try:
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script(f"""
                            const dom = document.getElementById('{char_id}');
                            const chart = echarts.getInstanceByDom(dom);
                            if (!chart) return false;
                            const option = chart.getOption();
                            return option && option.series && option.series.length > 0 &&
                                   option.series[0].data && option.series[0].data.length > 0;
                        """)
        )
        # 4. 执行JS从ECharts实例提取对应图表的数据
        y_values = driver.execute_script(f"""
                        const dom = document.getElementById('{char_id}');
                        const chart = echarts.getInstanceByDom(dom);
                        const option = chart.getOption();
                        const series = option.series[0];
                        const data = series.data.map(function(item) {{
                            // data可能为数值，或对象（如 {{value: <数值>}}）
                            if (item === null || item === undefined || typeof item !== 'object') return item;
                            return item.value;
                        }});
                        return data;
                    """)
        # 5. 数据清洗（处理null和NaN）
        arr1_cleaned = [
            None if v is None or (isinstance(v, float) and not v == v)  # 处理null和NaN
            else v
            for v in y_values
        ]
        result = arr1_cleaned
    except Exception as e:
        print(f'获取{char_id}信息失败')
    return result


# 获取单个型号热度, 库存, 价格 信息
# cate_name：型号
# isWeek：【周/月】
def getSearchInfo(cate_name, isWeek):
    showingCheckCode = checkVerificationCodePage(cate_name)
    while showingCheckCode:
        WaitHelp.waitfor(True, False)
        showingCheckCode = checkVerificationCodePage(cate_name)
    result = []
    try:
        # 1. 根据isWeek确定目标图表的容器ID（页面已从Highcharts改版为ECharts）
        peak_id = "J-detailChar" if isWeek else "J-detailChar-Month"
        stock_id = "J-stockChar" if isWeek else "J-stockChar-Month"
        price_id = "J-priceChar" if isWeek else "J-priceChar-Month"
        peak_data = get_echar_data(peak_id)
        stock_data = get_echar_data(stock_id)
        price_data = get_echar_data(price_id)
        result = [peak_data, stock_data, price_data]
        # print(f"型号 {cate_name} {period}数据获取成功，{result}")
    except Exception as e:
        period = "周" if isWeek else "月"
        print(f"型号 {cate_name} {period} 指数数据获取失败: {str(e)}")
        print(f"url is: {str(driver.current_url)}")
        LogHelper.write_log(log_file, f"型号 {cate_name} {period}指数数据错误: {str(e)}")
    return result


# 查询列表中所有需要查询的型号的搜索指数
def main(precise):
    all_cates = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'], 2)
    for (index, ppn) in enumerate(all_cates):
        if ppn.__contains__('?'):
            continue
        elif index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            while WaitHelp.isSleep_time():
                time.sleep(60 * 5)
            print(f'cate_index is: {index}  cate_name is: {ppn}')
            manu = all_manu[index]
            driver.get(URLManager.HQ_stock_url(ppn, precise))
            if index > 0 and index % 13 == 0:
                time.sleep(10*60)
            else:
                WaitHelp.waitfor(True, False)
            showingCheckCode = checkVerificationCodePage(ppn)
            while showingCheckCode:
                WaitHelp.waitfor(True, False)
                showingCheckCode = checkVerificationCodePage(ppn)
            # 获取supplier 信息
            supplier_info_arr = getSupplierInfo(ppn, manu)
            if supplier_info_arr.__len__() > 0:
                db.hq_stock_write(supplier_info_arr)
            else:
                # [ppn, manu, supplier_name, sup_ppn, sup_manu, batch, stock, packing, param, place, instruction, publish_date, task_name]
                db.hq_stock_write([[ppn, manu, "--", "", "", "", "0", "", "", "", "", "", task_name]])
                print(f"{ppn} without supplier data")
            # 获取peak data
            link_elem = driver.find_element(By.CSS_SELECTOR, "a.yun-zhishu")
            link_elem.click()
            WaitHelp.waitfor(True, False)
            cate_info = [ppn, manu,
                         '[0.00, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                         '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                         '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                         '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                         '', '', task_name]
            if has_hotData():
                try:
                    week_arr = getSearchInfo(ppn, True)
                    time.sleep(1.0)
                    if week_arr.__len__() > 0:  # 有周数据，请求月数据
                        is_month_active = False
                        while not is_month_active:
                            month_lab = driver.find_element(By.ID, 'monthTab')
                            month_lab.click()
                            # 等待月数据图表刷新
                            WaitHelp.waitfor(True, False)
                            is_month_active = "active" in month_lab.get_attribute("class")
                        month_arr = getSearchInfo(ppn, False)
                        if month_arr.__len__() > 0:
                            cate_info = [ppn, manu,
                                         str(week_arr[0]), str(month_arr[0]),
                                         str(week_arr[1]), str(month_arr[1]),
                                         str(week_arr[2]), str(month_arr[2]),
                                         task_name]
                            db.hq_hot_write([cate_info])
                except Exception as e:
                    print(f"型号 {ppn} 获取指数信息error {e}")
            else:
                print(f"型号 {ppn} 没有指数数据")
            db.hq_hot_write([cate_info])


if __name__ == "__main__":
    try:
        driver.get("https://www.hqew.com/")
        time.sleep(60)
        login_action(login_url)
        WaitHelp.waitfor_account_import(True, False)
        driver.get("https://www.hqew.com/")
        time.sleep(60)
        main()
    except Exception as e:
        print(f"主程序错误: {str(e)}")
        LogHelper.write_log(log_file, f"主程序错误: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

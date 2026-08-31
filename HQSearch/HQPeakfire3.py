import time
from WRTools import ExcelHelp, WaitHelp, PathHelp, LogHelper, EmailHelper, Record_data
from selenium.webdriver.common.by import By
from WRTools import ChromeDriverManager
import ssl
from Manager import AccManage, URLManager
from selenium.webdriver.support.ui import WebDriverWait

log_file = PathHelp.get_file_path('HQSearch', 'HQPeakfireLog.txt')

ssl._create_default_https_context = ssl._create_unverified_context

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TRFBJT.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 193,
                  'endIndex': 194}
task_name = 'TRFBJT'

db = Record_data.RecordData()
accouts_arr = [AccManage.HQ_hot_3['n'], AccManage.HQ_hot_3['p']]
login_url = "https://passport.hqew.com/login"
driver = ChromeDriverManager.getWebDriver(3)
driver.set_window_size(height=800, width=1380)
current_cate_has_date = True
VerificationCodePage = 0


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


def has_hotData() -> bool:
    nodatas_areas = driver.find_elements(By.CSS_SELECTOR, 'div.no-data')
    if nodatas_areas.__len__() > 0:
        return False
    return True


# 获取单个型号热度信息
# cate_name：型号
# isWeek：【周/月】搜索指数
def getSearchInfo(cate_name, manu, isWeek):
    showingCheckCode = checkVerificationCodePage(cate_name)
    while showingCheckCode:
        WaitHelp.waitfor(True, False)
        showingCheckCode = checkVerificationCodePage(cate_name)
    result = []
    try:
        # 1. 根据isWeek确定目标图表的ID
        chart_id = "J-detailChar" if isWeek else "J-detailChar-Month"

        # 2. 等待目标图表容器加载，并获取其data-highcharts-chart属性（图表索引）
        chart_container = driver.find_element(By.ID, chart_id)
        chart_index = int(chart_container.get_attribute("data-highcharts-chart"))

        # 3. 等待图表数据加载完成（确保系列和数据点存在）
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script(f"""
                const chart = window.Highcharts.charts[{chart_index}];
                return chart && chart.series && chart.series.length > 0 && chart.series[0].data.length > 0;
            """)
        )

        # 4. 执行JS提取对应图表的数据
        y_values = driver.execute_script(f"""
            const chart = window.Highcharts.charts[{chart_index}];
            const series = chart.series[0];  // 确认系列索引正确
            return series.data.map(p => p.options?.y ?? null);
        """)

        # 5. 数据清洗
        arr1_cleaned = [
            None if v is None or (isinstance(v, float) and not v == v)  # 处理null和NaN
            else v
            for v in y_values
        ]
        result = arr1_cleaned
        # print(f"型号 {cate_name} {period}数据获取成功，长度: {len(result)}")

    except Exception as e:
        period = "周" if isWeek else "月"
        print(f"型号 {cate_name} {period}数据获取失败: {str(e)}")
        print(f"url is: {str(driver.current_url)}")
        LogHelper.write_log(log_file, f"型号 {cate_name} {period}数据错误: {str(e)}")
    return result


# 验证当前页面是否正在等待用户验证，连续三次请求出现验证码页面，则关闭页面
def checkVerificationCodePage(ppn) -> bool:
    global VerificationCodePage
    if driver.current_url.__contains__('https://passport.hqew.com/robottocheck'):
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


# 查询列表中所有需要查询的型号的搜索指数
def main():
    try:
        all_cates = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                               sourceFile_dic['colIndex'])
        all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'], 2)
        for (index, ppn) in enumerate(all_cates):
            while WaitHelp.isSleep_time():
                    time.sleep(60*5)
            if ppn.__contains__('?'):
                continue
            elif index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
                print(f'cate_index is: {index}  cate_name is: {ppn}')
                manu = all_manu[index]
                driver.get(URLManager.HQ_hot_url(ppn))
                WaitHelp.waitfor(True, False)
                if has_hotData():
                    week_arr = getSearchInfo(ppn, manu, True)
                    time.sleep(1.0)
                    if week_arr.__len__() > 0:  # 有周数据，请求月数据
                        is_month_active = False
                        while not is_month_active:
                            month_lab = driver.find_element(By.ID, 'monthTab')
                            month_lab.click()
                            # 等待月数据图表刷新
                            WaitHelp.waitfor(True, False)
                            is_month_active = "active" in month_lab.get_attribute("class")
                        month_arr = getSearchInfo(ppn, manu, False)
                        if month_arr.__len__() > 0:
                            cate_info = [ppn, manu, str(week_arr), str(month_arr), task_name]
                            db.hq_hot_write([cate_info])
                else:
                    print(f"型号 {ppn} 没有数据")
                    cate_info = [ppn, manu, '[0.00, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]', '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]', task_name]
                    db.hq_hot_write([cate_info])

    finally:
        driver.quit()  # 无论是否出错，都关闭浏览器


if __name__ == "__main__":
    try:
        driver.get("https://www.hqew.com/")
        login_action(login_url)
        WaitHelp.waitfor_account_import(True, False)
        main()
    except Exception as e:
        print(f"主程序错误: {str(e)}")
        LogHelper.write_log(log_file, f"主程序错误: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()


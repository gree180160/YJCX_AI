import time
from WRTools import ExcelHelp, WaitHelp, PathHelp, MySqlHelp_recommanded, LogHelper
from selenium.webdriver.common.by import By
from WRTools import ChromeDriverManager
import ssl
from Manager import AccManage, URLManager
# 替换 time.sleep(10.0) 为显式等待（示例）
from selenium.webdriver.support.ui import WebDriverWait

log_file = PathHelp.get_file_path('HQSearch', 'HQPeakfireLog.txt')

ssl._create_default_https_context = ssl._create_unverified_context

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TTILDOVoltageStabilizer.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 7173,
                  'endIndex': 7600}
task_name = 'TTILDOVoltageStabilizer'


accouts_arr = [AccManage.HQ_hot_4['n'], AccManage.HQ_hot_4['p']]

login_url = "https://passport.hqew.com/login"

driver = ChromeDriverManager.getWebDriver(0)
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


def has_hotData() -> bool:
    nodatas_areas = driver.find_elements(By.CSS_SELECTOR, 'div.no-data')
    if nodatas_areas.__len__() > 0:
        return False
    return True


# 获取单个型号热度信息
# cate_name：型号
# isWeek：【周/月】搜索指数
def getSearchInfo(cate_name, manu, isWeek):
    result = []
    try:
        # 等待图表数据加载（关键：确保切换标签后数据已刷新）
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return window.Highcharts && window.Highcharts.charts.length > 0")
        )
        # 执行JS前先确认图表和系列存在
        y_values = driver.execute_script("""
            const chart = window.Highcharts.charts[0];  // 确认索引正确
            if (!chart || !chart.series || chart.series.length === 0) return [];
            const series = chart.series[0];  // 确认系列索引正确
            return series.data.map(p => p.options?.y ?? null);  // 兼容null值
        """)
        # 数据清洗
        arr1_cleaned = [None if v is None or (isinstance(v, float) and not v == v) else v for v in y_values]
        result = arr1_cleaned
        print(f"型号 {cate_name} {'周' if isWeek else '月'} 数据获取成功，长度: {result}")
    except Exception as e:
        print(f"型号 {cate_name} 数据获取失败: {str(e)}")
        LogHelper.write_log(log_file, f"型号 {cate_name} 错误: {str(e)}")  # 记录错误日志
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
                week_arr = getSearchInfo(ppn, manu, True)
                time.sleep(1.0)
                if week_arr.__len__() > 0:  # 有周数据，请求月数据
                    month_lab = driver.find_element(By.ID, 'monthTab')
                    month_lab.click()
                    # 等待月数据图表刷新
                    WebDriverWait(driver, 10).until(
                        lambda d: d.execute_script("return window.Highcharts.charts[0].series[0].data.length > 0")
                    )
                    month_arr = getSearchInfo(ppn, manu, False)
                    if month_arr.__len__() == 0:
                        time_lab = driver.find_element(By.ID, 'timetabs')
                        m_link = time_lab.find_elements(By.TAG_NAME, 'a')[1]
                        m_link.click()
                        time.sleep(10.0)
                        month_arr = getSearchInfo(ppn, manu, False)
                    if month_arr.__len__() > 0:
                        cate_info = [ppn, manu, str(week_arr), str(month_arr), task_name]
                        MySqlHelp_recommanded.DBRecommandChip().hq_hot_write([cate_info])
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

import time

from WRTools import ExcelHelp, WaitHelp, PathHelp, MySqlHelp_recommanded, LogHelper
from selenium.webdriver.common.by import By
from WRTools import ChromeDriverManager
import ssl
from Manager import AccManage, URLManager

log_file = PathHelp.get_file_path('HQSearch', 'HQPeakfireLog.txt')
ssl._create_default_https_context = ssl._create_unverified_context

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TNXPMPU.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 1949,
                  'endIndex': 836*3}
task_name = 'TNXPMPU'


accouts_arr = [AccManage.HQ_hot_3['n'], AccManage.HQ_hot_3['p']]
login_url = "https://passport.hqew.com/login"

driver = ChromeDriverManager.getWebDriver(3)
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
    weekInfos = driver.find_elements(By.ID, 'template_0')
    result = []
    if weekInfos.__len__() > 0:
        div_id = 'J-detailChar' if isWeek else 'J-detailChar-Month'
        try:
            detail_w_div = driver.find_element(By.ID, div_id)
            hot_table = detail_w_div.find_elements(By.CSS_SELECTOR, 'g.highcharts-data-labels.highcharts-series-0.highcharts-line-series.highcharts-color-0')[0]
            dots = hot_table.find_elements(By.CSS_SELECTOR,
                                            'g.highcharts-label.highcharts-data-label.highcharts-data-label-color-0')
            for temp_d in dots:
                result.append(temp_d.find_element(By.TAG_NAME, 'tspan').text)
        except Exception as e:
            LogHelper.write_log(log_file, f'{cate_name} week info error {e}')
    return result


# 查询列表中所有需要查询的型号的搜索指数
def main():
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
            time.sleep(10.0)
            if week_arr.__len__() > 0:  # 有周数据，请求月数据
                time_lab = driver.find_element(By.ID, 'timetabs')
                m_link = time_lab.find_elements(By.TAG_NAME, 'a')[1]
                m_link.click()
                time.sleep(20.0)
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


if __name__ == "__main__":
    driver.get("https://www.hqew.com/")
    login_action(login_url)
    WaitHelp.waitfor_account_import(True, False)
    main()

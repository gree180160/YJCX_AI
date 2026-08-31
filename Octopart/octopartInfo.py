import ssl
import sys
from selenium.webdriver.common.by import By
from WRTools import ChromeDriverManager
from WRTools import ExcelHelp, LogHelper, PathHelp, WaitHelp, Record_data, EmailHelper
from Manager import AccManage, URLManager
import time
import json
from selenium.webdriver.common.action_chains import ActionChains
import random

ssl._create_default_https_context = ssl._create_unverified_context

driver = ChromeDriverManager.getWebDriver(0)

accouts_arr = AccManage.oc_stock1
altium_home = 'https://altium.com'
altium_login = 'https://auth.altium.com/?ReturnUrl=https://www.altium.com/'
default_url = 'https://octopart.com/'
CHART_CONTAINER_SELECTOR = (By.CSS_SELECTOR, "div.recharts-responsive-container")
TARGET_COMPONENT_NAME = "AreaChart"  # 组件名包含此字符串
TARGET_DATA_SENTRY = "AreaChart"  # data-sentry-element值

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TTILDOVoltageStabilizer.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 4}
task_name = 'TTILDOVoltageStabilizer'

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
            authors = temp_supplier.find_elements(By.CSS_SELECTOR, '[data-testid="authorized"]')
            if authors.__len__() > 0:
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
        #get info
        try:
            stock_data = getStockData(link)
        except Exception as e:
            stock_data = []
            LogHelper.write_log(log_file_name=log_file, content=f'{pn} 没有历史库存记录! {e} ')
        try:
            tech_data = getTechnicalSpecifications()
        except Exception as e:
            tech_data = []
            LogHelper.write_log(log_file_name=log_file, content=f'{pn} 没有技术规格信息 ! {e}')
        try:
            supplier_data = getSupplierInfo()
        except Exception as e:
            supplier_data = []
            LogHelper.write_log(log_file_name=log_file, content=f'{pn} 没有供应链信息 ! {e}')
        #(ppn, manu, des, distribute, stock, currency_type, k_price, opn, stock_data, tech_data, supplier_data, task_name)
        stock_data_json = json.dumps(stock_data, ensure_ascii=False)
        tech_data_json = json.dumps(tech_data, ensure_ascii=False)
        supplier_data_json = json.dumps(supplier_data, ensure_ascii=False)
        info = [part_number, part_manu, part_des, distribute, stock, kprice_type, kprice, pn, stock_data_json, tech_data_json, supplier_data_json, task_name]
        Record_data.RecordData().octopart_info_write([info])
    except Exception as e:
        LogHelper.write_log(log_file_name=log_file, content=f'{pn} 页面 解析异常：{e} ')


def getStockData(a_link):
    stock_data = []
    try:
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
        ######从rect中获取data
        rectInstance = get_raw_react_instance()
        if rectInstance:
            props = find_target_component(rectInstance)
            if props:
                if isinstance(props, dict):
                    stock_data = process_data(props['data'])
                elif isinstance(props, list):
                    stock_data = process_data(props)
    except Exception as e:
        print(f"getStockData失败: {str(e)}")
    return stock_data


def get_raw_react_instance():
    """获取必要的React信息（只返回关键字段，避免循环引用）"""
    global driver
    try:
        chart_container = driver.find_element(*CHART_CONTAINER_SELECTOR)
        # 关键修改：JS只提取child节点的必要字段（不返回完整实例）
        js_code = """
        const container = arguments[0];
        // 找到React Fiber实例
        const fiberKeys = Object.keys(container).filter(k => 
            k.startsWith('__reactFiber$') || 
            k.startsWith('__reactInternalInstance$')
        );
        if (!fiberKeys.length) {
            return null;
        }
        const fiberInstance = container[fiberKeys[0]];
        // 只返回child节点的关键信息（避免完整实例的循环引用）
        const child = fiberInstance.child;
        if (!child) {
            return { hasChild: false };
        }
        // 提取我们需要的字段（memoizedProps、type、elementType）
        return {
            hasChild: true,
            childProps: child.memoizedProps || child.pendingProps,
            childType: child.type || child.elementType,
            childElementType: child.elementType  // 额外备份类型信息
        };
        """
        # 执行JS，返回精简后的信息（无循环引用）
        react_info = driver.execute_script(js_code, chart_container)

        if not react_info:
            print("未获取到React相关信息")
            return None
        return react_info
    except Exception as e:
        print(f"获取React信息失败: {str(e)}")
        return None


def find_target_component(react_info):
    """用Python逻辑查找目标组件（基于精简的React信息）"""
    if not react_info or not react_info.get('hasChild'):
        return None

    # 从精简信息中提取属性（避免处理完整实例）
    props = react_info.get('childProps', {})
    component_type = react_info.get('childType', {}) or react_info.get('childElementType', {})

    # 提取组件信息
    component_name = component_type.get('displayName') or component_type.get('name') or ""
    data_sentry = props.get('data-sentry-element', "")
    has_data = isinstance(props.get('data'), list) and len(props.get('data', [])) > 0

    # 匹配条件
    if (TARGET_COMPONENT_NAME in component_name and
        data_sentry == TARGET_DATA_SENTRY and has_data):
        return props  # 直接返回props，包含data
    else:
        print("组件不匹配")
        print(f"实际信息: 名称={component_name}, data-sentry={data_sentry}")
        return None


def process_data(raw_data):
    """处理数据（纯Python逻辑）"""
    if not raw_data or not isinstance(raw_data, list):
        return []

    cleaned_data = []
    for item in raw_data:
        item_copy = item.copy()
        # 删除xAxisDate字段（如果存在）
        if "xAxisDate" in item_copy:
            del item_copy["xAxisDate"]
        cleaned_data.append(item_copy)
    return cleaned_data


def getTechnicalSpecifications():
    a = driver.find_element(By.ID, 'Specs')
    techArea = a.find_element(By.XPATH, './following-sibling::*[1]')
    rows = techArea.find_elements(By.CSS_SELECTOR, '[data-testid="resource-row"]')
    try:
        a = driver.find_element(By.TAG_NAME, 'button')
        if a:
            a.click()
            time.sleep(20.0 + random.uniform(1, 30))
    except:
        print('展开全部失败')
    tech_data = []
    for row in rows:
        if row.find_elements(By.TAG_NAME, 'span').__len__() >= 2:
            title = row.find_elements(By.TAG_NAME, 'span')[0].text
            value = row.find_elements(By.TAG_NAME, 'span')[1].text
            row_tech = {"title": title, "value": value}
        if row_tech:
            tech_data.append(row_tech)
    return tech_data


def getSupplierInfo():
    a = driver.find_element(By.ID, 'SupplyChain')
    supplierArea = a.find_element(By.XPATH, './following-sibling::*[1]')
    rows = supplierArea.find_elements(By.CSS_SELECTOR, '[data-testid="resource-row"]')
    supplier_data = []
    for row in rows:
        if row.find_elements(By.TAG_NAME, 'span').__len__() >= 2:
            title = row.find_elements(By.TAG_NAME, 'span')[0].text
            value = row.find_elements(By.TAG_NAME, 'span')[1].text
            row_tech = {"title": title, "value": value}
        if row_tech:
            supplier_data.append(row_tech)
    return supplier_data


def getNumberAlias():
    a = driver.find_element(By.ID, 'AlternatePartNumbers')
    alternateArea = a.find_element(By.XPATH, './following-sibling::*[1]')
    part_list = alternateArea.find_elements(By.TAG_NAME, 'li')
    alias_data = []
    for item in part_list:
        alias_data.append(item.text)
    return alias_data


# 验证是否处于验证IP 页面
def is_security_check() -> bool:
    times = 0
    while driver.find_elements(By.ID, 'px-captcha').__len__() > 0:
        # 创建 ActionChains 对象
        times += 1
        actions = ActionChains(driver)
        # 模拟长按操作
        actions.click_and_hold(driver.find_element(By.ID, 'px-captcha')).perform()
        # 保持长按状态一段时间（例如 3 秒）
        time.sleep(25)
        # 释放鼠标
        actions.release().perform()
        time.sleep(52.5 + random.uniform(1, 10))
    return times > 5


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
            if is_security_check():
                print('is security ip')
                driver.close()
            analy_html(ppn_index, ppn)


def ocLogin():
    login_span = driver.find_element(By.CSS_SELECTOR, 'span.truncate')
    login_span.click()
    time.sleep(45.0+random.uniform(1, 20))
    altiumAuthButton = driver.find_element(By.CSS_SELECTOR, "[data-sentry-component='AltiumAuthButton']")
    altiumAuthButton.click()
    time.sleep(60.0 + random.uniform(2, 25))


def altiumLogin():
    email_input = driver.find_element(By.CSS_SELECTOR, "[data-locator='signin-email']")
    email_input.clear()
    time.sleep(5.0 + random.uniform(3, 13))
    email_input.send_keys(accouts_arr[0])
    time.sleep(2.0 + random.uniform(2, 20))
    pw_input = driver.find_elements(By.CSS_SELECTOR, "[data-locator='signin-password']")[1]
    pw_input.clear()
    time.sleep(2.5 + random.uniform(1, 10))
    pw_input.send_keys(accouts_arr[1])
    time.sleep(3.5 + random.uniform(1, 10))
    # 定位到内容为 "Sign In" 的 <span> 元素
    login_btn = driver.find_element(By.CSS_SELECTOR, "[data-locator='signin-submit']")
    # 对找到的元素执行操作，例如点击
    login_btn.click()
    time.sleep(60.0 + random.uniform(5, 15))


if __name__ == "__main__":
    driver.get(altium_home)
    time.sleep(50.0 + random.uniform(1, 10))
    driver.get(altium_login)
    time.sleep(90.0 + random.uniform(1, 10))
    altiumLogin()

    driver.get(default_url)
    time.sleep(90.0+random.uniform(1, 10))
    driver.get(default_url)
    time.sleep(90.0 + random.uniform(1, 10))
    ocLogin()
    main()
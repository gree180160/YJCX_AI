
#  记录Task 提供的型号，在IC 中的库存信息
import time, re
from selenium.webdriver.common.by import By
import random
from WRTools import ChromeDriverManager
import ssl
import traceback
from Manager import AccManage, URLManager
from WRTools import ExcelHelp, WaitHelp, PathHelp, Record_data
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ssl._create_default_https_context = ssl._create_unverified_context


sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TBomHot.xlsx'),
                  'sourceSheet': 'ppn3',
                  'colIndex': 1,
                  'startIndex': 7,
                  'endIndex': 10}
task_name = 'TBomHot'

accouts_arr = [AccManage.IC_stock_2['n'], AccManage.IC_stock_2['p']]

try:
    driver = ChromeDriverManager.getWebDriver(2)
except Exception as e:
    print(e)


def login_action():
    login_a_arr = driver.find_elements(By.CSS_SELECTOR, 'a.bar_login_text.tologin')
    if login_a_arr and login_a_arr.__len__() > 0:
        login_a = login_a_arr[0]
        login_a.click()
        time.sleep(30.0)
        # begin login
        accout_current = accouts_arr
        driver.find_element(by=By.ID, value='username').clear()
        driver.find_element(by=By.ID, value='username').send_keys(accout_current[0])
        time.sleep(5.0)
        driver.find_element(by=By.ID, value='password').clear()
        driver.find_element(by=By.ID, value='password').send_keys(accout_current[1])
        time.sleep(5.0)
        WaitHelp.waitfor_account_import(False, False)
        driver.find_element(by=By.ID, value='btn_login').click()
        WaitHelp.waitfor_ICHot(True, False)


#   二维数组，page 列表， table 列表
def get_stock(cate_index, cate_name, st_manu):
    search_url = URLManager.cxyx_stock_url(cate_name, 1)
    login_action()
    driver.get(search_url)
    # 延时几秒确保页面加载完毕
    # WaitHelp.waitfor_ICHot(True, False)
    WaitHelp.waitfor(True, False)
    # confuse 行为- 滑动任意高度
    # scroll_height = 25.0 + random.uniform(1, 30)
    # driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_height)
    body = driver.find_element(By.CSS_SELECTOR, "tbody.search_resultList")
    tr_arr = body.find_elements(By.CSS_SELECTOR, "tr.search_resultLi")
    row_count = len(tr_arr)
    result = []
    try:
        for i in range(row_count):
            # 每一轮都重新拿一遍tr列表，取第i行，拿到全新DOM对象，不是旧壳
            tr_arr = body.find_elements(By.CSS_SELECTOR, "tr.search_resultLi")
            if i >= len(tr_arr):
                break
            temp_tr = tr_arr[i]

            if not temp_tr.is_displayed():
                continue

            try:
                # 滚动当前全新tr对象
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block:'center', behavior:'instant'});", temp_tr)
                    time.sleep(0.6)  # 调高一点，给虚拟列表渲染
                except:
                    print('scrollIntoView error')

                td_arr = temp_tr.find_elements(By.TAG_NAME, 'td')
                if len(td_arr) <= 3:
                    continue

                # -----supplier -----------------
                supplier = td_arr[0].find_element(By.CSS_SELECTOR, 'p.supplier_detail_name').text

                ppn = ""
                manu = ""
                category = ""
                productC_partBox_div_arr = td_arr[1].find_element(By.CSS_SELECTOR,
                                                                  'div.productC_partBox').find_elements(
                    By.TAG_NAME, 'div')
                if len(productC_partBox_div_arr) > 0:
                    ppn = productC_partBox_div_arr[1].find_elements(By.TAG_NAME, 'a')[0].text
                    manu = productC_partBox_div_arr[2].text.replace("品牌：", "")
                    category = productC_partBox_div_arr[4].text.replace("分类：", "")
                # get  price_step
                target_li_list = td_arr[2].find_element(By.CSS_SELECTOR, "ul.originalPriceBox").find_elements(By.TAG_NAME, 'li')
                print(f"DEBUG i={i},supplier={supplier}, li_count={len(target_li_list)}")

                displayed_li = []
                for li in target_li_list:
                    display_style = driver.execute_script("""
                        return window.getComputedStyle(arguments[0]).getPropertyValue('display');
                    """, li)
                    if display_style == "flex":
                        displayed_li.append(li)

                all_valid_prices = []
                for li in displayed_li:
                    try:
                        count = driver.execute_script("""
                            var span = arguments[0].querySelector('span.price_ladder_left');
                            return span ? span.textContent.trim() : '';
                        """, li)
                        price_raw = driver.execute_script("""
                            var span = arguments[0].querySelector('span.price_ladder_right');
                            return span ? span.textContent.trim() : '';
                        """, li)
                        if count and price_raw:
                            all_valid_prices.append(f"{count}:{price_raw}")
                    except Exception:
                        continue

                if all_valid_prices:
                    last_valid_item = all_valid_prices[-1]
                    count_str, price_str = last_valid_item.split(":")
                    try:
                        price_format = f"{float(price_str):.2f}"
                        price_step = f"{count_str}:{price_format}"
                    except Exception:
                        price_step = last_valid_item
                else:
                    price_step = ""

                batch_tr = td_arr[3]
                stock = batch_tr.find_elements(By.CSS_SELECTOR, 'span.clr-newblock')[0].text
                batch = batch_tr.find_elements(By.CSS_SELECTOR, 'span.clr-newblock')[1].text
                # save supplier
                result.append([supplier, ppn, manu, category, price_step, stock, batch, task_name])

            except Exception as e:
                err_stack = traceback.format_exc()
                print(f"tr error {e}\n堆栈信息:\n{err_stack}")

        # 循环结束后入库
        if len(result) > 0:
            Record_data.RecordData().ic_cxyx_stock_write(result)
    except Exception as e:
        print(f'page error {e}')


def confuseAction(action):
    if action:
        a_item = action()
        try:
            a_item.click()
            time.sleep(8.5 + random.uniform(1, 10))
            # 关闭新页面（如果打开了新的窗口）
            if len(driver.window_handles) > 1:
                driver.close()
            # 返回初始页面（如果需要）
            driver.switch_to.window(driver.window_handles[0])
        except:
            print('confuse error')
    else:
        print('action is None')


# 创新学院
def confuse_XCSchool():
    try:
        ad1 = driver.find_elements(By.CSS_SELECTOR, 'a.header_nav_item')[-1]
        return ad1
    except:
        return None


# 供应商详情
def confuse_supplier_info():
    try:
        suppliers = driver.find_elements(By.CSS_SELECTOR, 'div.product_supplier_detail')
        if suppliers.__len__() > 0:
            return random.choice(suppliers)
    except:
        return None


# help center
def confuse_helpCenter():
    try:
        right_items = driver.find_elements(By.CSS_SELECTOR, 'div.bar_right_item')
        help_center = right_items[-2]
        help_link = help_center.find_element(By.TAG_NAME, 'a')
        return help_link
    except:
        return None


# 诚信监督
def confuse_oversight():
    try:
        right_items = driver.find_elements(By.CSS_SELECTOR, 'div.bar_right_item')
        oversight = right_items[-3]
        oversight_link = oversight.find_element(By.TAG_NAME, 'a')
        return oversight_link
    except:
        return None


def confuse_ICHome():
    try:
        ICHome_link = driver.find_element(By.CSS_SELECTOR, 'a.footer_website_item')[0]
        return ICHome_link
    except:
        return None


def main():
    # List of confuse actions
    confuse_actions = [
        confuse_XCSchool,
        confuse_supplier_info,
        confuse_helpCenter,
        confuse_oversight,
        confuse_ICHome
    ]
    all_cates = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                           sourceFile_dic['colIndex'])
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'], 2)
    for (cate_index, cate_name) in enumerate(all_cates):
        while WaitHelp.isSleep_time():
            time.sleep(60 * 5)
        if cate_name.__contains__('?'):
            continue
        elif cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
            if cate_index % 7 == 0 and cate_index > 0:
                time.sleep(60 * 5)
            get_stock(cate_index, cate_name, all_manu[cate_index])
            # Every three categories, perform a confuse action
            if (cate_index + 1) % 3 == 0:
                random_action = random.choice(confuse_actions)
                confuseAction(random_action)


if __name__ == "__main__":
    driver.get('https://www.icweb.net/')
    time.sleep(2.5 + random.uniform(1, 10))
    login_action()
    main()

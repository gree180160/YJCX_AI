# es electronic source
import ssl
from selenium.webdriver.common.by import By
from WRTools import ExcelHelp, PathHelp, WaitHelp, ChromeDriverManager
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import traceback
from selenium.common.exceptions import TimeoutException


ssl._create_default_https_context = ssl._create_unverified_context
try:
    driver = ChromeDriverManager.getWebDriver(0)
except Exception as e:
    print(e)

sourceFile_dic = {'fileName': PathHelp.get_file_path(None, 'TEVG.xlsx'),
                  'sourceSheet': 'cate_link',
                  'colIndex': 1,
                  'startIndex': 8,
                  'endIndex': 130}
task_name = 'TEVG.xlsx'
home_url = 'https://www.evg.de/de/shop'
cate_url = 'https://www.evg.de/de/shop'


current_page = 1
total_page = 1


# 获取当前页面的数据
def get_page_data(url, index):
    # [model, manufacturer, stock, price1_title, price1, price2_title, price2]
    table_container = driver.find_element(By.CSS_SELECTOR, 'div.listing.row.products')
    product_list = table_container.find_elements(By.CSS_SELECTOR, 'div.col.product-content')
    page_data = []
    for product in product_list:
        model = manufacturer = stock = price1_title = price1 = price2_title = price2 = ""
        try:
            model = product.find_element(By.CSS_SELECTOR, 'p.products_model').find_element(By.TAG_NAME, 'b').text
            manufacturer = product.find_element(By.CSS_SELECTOR, 'p.manufacturer').find_element(By.TAG_NAME, 'b').text
            price_container = product.find_element(By.CSS_SELECTOR, 'div.price-box')
            price_items = price_container.find_elements(By.CSS_SELECTOR, 'div.price-item')
            if price_items.__len__() >= 2:
                price1_title = price_items[0].find_element(By.CSS_SELECTOR, 'div.list-product-item-from').text.replace("Ab ", "")
                price1 = price_items[0].find_element(By.CSS_SELECTOR, 'div.list-product-text').text.replace('je EUR ', '')
                price2_title = price_items[-1].find_element(By.CSS_SELECTOR, 'div.list-product-item-from').text.replace("Ab ", "")
                price2 = price_items[-1].find_element(By.CSS_SELECTOR, 'div.list-product-text').text.replace('je EUR ', '')
            elif price_items.__len__() == 1:
                price1_title = price_items[0].find_element(By.CSS_SELECTOR, 'div.list-product-item-from').text.replace("Ab ", "")
                price1 = price_items[0].find_element(By.CSS_SELECTOR, 'div.list-product-text').text.replace('je EUR ', '')
                price2_title = price2 = ''
            try:
                stock_str = product.find_element(By.CSS_SELECTOR, 'div.stocklabel-list').find_elements(By.TAG_NAME, 'span')[-1].text
                stock = stock_str.split(' ')[0]
            except:
                stock = stock_str
        except Exception as e:
            print("item error")
        if stock != '0' and stock != '':
            item = [model, manufacturer, stock, price1_title, price1, price2_title, price2, index, current_page]
            page_data.append(item)
    return page_data


def go_to_manu(url, index):
    global current_page, total_page
    if index == 999:
        current_page = 1
        total_page = 1
    else:
        current_page = 1
        total_page = 1
    while current_page <= total_page:
        # https://www.evg.de/de/shop/stecker-steckverbinder/rundsteckverbinder/schraubverriegelung/m16-steckverbinder-ip-67-fabrikat-binder/zubehoer?next_page=2
        new_url = f"{url}?next_page={current_page}"
        driver.get(new_url)
        WaitHelp.waitfor(True, False)
        page_data = get_page_data(url, index)
        if page_data.__len__() == 0:
            break
        ExcelHelp.add_arr_to_sheet(sourceFile_dic['fileName'], 'result', page_data)
        time.sleep(3.0)
        if current_page == 1:
            set_total_page()
        current_page += 1


def set_total_page():
    global total_page
    try:
        # 方式1：直接滑动到页面底部（最常用）
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(20.0)
        page_links = driver.find_element(By.CSS_SELECTOR, 'div.nav-pages.btn-group').find_elements(By.TAG_NAME, 'a')
        if page_links.__len__() > 3:
            total_page_str = page_links[-2].text
            total_page = int(total_page_str)
        else:
            total_page = 1
    except Exception as e:
        total_page = 1
    print(f"total page is: {total_page}")


# 假设你的自定义工具类保留（若WaitHelp/ExcelHelp未定义，需确保其存在）
# from your_helper import WaitHelp, ExcelHelp, sourceFile_dic

def get_layer_links(driver, wait, max_retry=3):
    """
    通用函数：获取当前页面的层级链接（提取href字符串，避免元素失效）
    :param driver: selenium driver实例
    :param wait: WebDriverWait实例
    :param max_retry: 最大重试次数（避免死循环）
    :return: 该层级所有链接的href列表
    """
    # 初始化重试计数器
    retry_count = 0
    while retry_count < max_retry:
        try:
            # 显式等待核心元素加载（复用传入的wait超时时间）
            table = wait.until(
                EC.presence_of_element_located((By.ID, 'categorie-listing'))
            )
            list_container = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.listing.categorie-listing.equalize-no-panels')
                )
            )
            # 获取所有a标签元素，提取href并去重
            link_elems = list_container.find_elements(By.CSS_SELECTOR, 'a.vertical-helper.image-link')
            href_list = [elem.get_attribute('href') for elem in link_elems if elem.get_attribute('href')]
            print(f"当前层级获取到 {len(href_list)} 个链接")
            return href_list

        except TimeoutException:
            retry_count += 1
            print(f"【重试{retry_count}/{max_retry}】页面元素加载超时，正在刷新页面...")
            # 优化1：用refresh()强制刷新（比get(current_url)更彻底，避免缓存）
            driver.refresh()
            # 优化2：等待页面重新加载（可根据实际情况调整，比如先短等，再逐步延长）
            time.sleep(20 * retry_count)  # 重试次数越多，等待时间越长（20s→40s→60s）
            continue  # 回到循环开头，重新尝试获取元素

        except Exception as e:
            print(f"提取当前层级链接失败: {e}")
            traceback.print_exc()
            return []

    # 超过最大重试次数，退出循环并提示
    print(f"已重试{max_retry}次仍超时，放弃获取当前层级链接 {driver.current_url}")
    return []


def get_cate_urls():
    # 初始化驱动（若外部已初始化，可移除；需确保driver全局可用）
    # driver = webdriver.Chrome()  # 根据实际浏览器配置
    wait = WebDriverWait(driver, 30)  # 显式等待实例，超时10秒
    links = []

    try:
        # 第一步：访问初始分类页面，获取第一层链接（href列表）
        driver.get(cate_url)
        WaitHelp.waitfor(True, False)  # 保留原有等待（若需兼容）
        first_hrefs = get_layer_links(driver, wait)

        # 遍历第一层链接
        for first_href in first_hrefs:
            try:
                driver.get(first_href)
                WaitHelp.waitfor(True, False)
                second_hrefs = get_layer_links(driver, wait)

                # 遍历第二层链接
                for second_href in second_hrefs:
                    try:
                        driver.get(second_href)
                        WaitHelp.waitfor(True, False)
                        third_hrefs = get_layer_links(driver, wait)

                        # 遍历第三层链接
                        for third_href in third_hrefs:
                            try:
                                driver.get(third_href)
                                WaitHelp.waitfor(True, False)
                                fourth_hrefs = get_layer_links(driver, wait)

                                # 遍历第四层链接
                                for fourth_href in fourth_hrefs:
                                    try:
                                        driver.get(fourth_href)
                                        WaitHelp.waitfor(True, False)
                                        fifth_hrefs = get_layer_links(driver, wait)

                                        # 第五层为最终商品列表链接，存入结果
                                        for fifth_href in fifth_hrefs:
                                            print(f"获取商品列表链接: {fifth_href}")
                                            links.append(fifth_href)
                                    except Exception as e:
                                        print(f"第四层链接 {fourth_href} 处理失败: {e}")
                                        traceback.print_exc()
                                        continue
                            except Exception as e:
                                print(f"第三层链接 {third_href} 处理失败: {e}")
                                traceback.print_exc()
                                continue
                    except Exception as e:
                        print(f"第二层链接 {second_href} 处理失败: {e}")
                        traceback.print_exc()
                        continue
            except Exception as e:
                print(f"第一层链接 {first_href} 处理失败: {e}")
                traceback.print_exc()
                continue
    except Exception as e:
        print(f"核心流程异常: {e}")
        traceback.print_exc()
    finally:
        # 将结果写入Excel（保留原有逻辑）
        if links:
            ExcelHelp.add_arr_to_col(sourceFile_dic['fileName'], 'cate_link', links)
            print(f"共获取 {len(links)} 个商品列表链接，已写入Excel")
        else:
            print("未获取到任何商品列表链接")
        # 若驱动为本地初始化，需关闭（根据实际场景）
        # driver.quit()


def main():
    all_manu = ExcelHelp.read_col_content(sourceFile_dic['fileName'], sourceFile_dic['sourceSheet'],
                                          sourceFile_dic['colIndex'])
    for (index, url) in enumerate(all_manu):
        while WaitHelp.isSleep_time():
            time.sleep(60 * 5)
        if index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'index: {index}, url is: {url}')
            go_to_manu(url, index)


if __name__ == "__main__":
    driver.get(home_url)
    WaitHelp.waitfor(True, False)
    main()
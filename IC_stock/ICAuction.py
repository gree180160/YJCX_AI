import time

import requests
from bs4 import BeautifulSoup
from WRTools import ExcelHelp, PathHelp
from datetime import datetime


current_time = datetime.now()
current_date = current_time.strftime("%Y-%m-%d")


def get_page_info(page):
    url = f'https://kcwy.ic.net.cn/overstock/overstock_pickup.php?Page={page}'
    mac_arr = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.187 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:117.0) Gecko/20100101 Firefox/117.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:116.0.3) Gecko/20100101 Firefox/116.0.3'
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15'
    ]
    headers = {
        'User-Agent': mac_arr[page-1]
    }
    response = requests.get(url, headers=headers)
    time.sleep(10.0)
    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.find_all('div', class_='hotList_index')
    result = []
    for item in items:
        model = item.select('p.proTit.tc')[0].text
        manufacturer = item.select('span.factory')[0].text
        manufacturer = manufacturer.replace("厂商：", "")
        manufacturer = manufacturer.replace("\r\n", "")
        manufacturer = manufacturer.replace("\t", "")
        quantity = item.select('span.num')[0].text
        quantity = quantity.replace('数量：', '')
        batch = item.select('span.batchNum')[0].text
        batch = batch.replace('批号：', '')
        price = item.select('span.pointUnitPrice')[0].text
        price = price.replace('单价：', '')
        temp = [model, manufacturer, quantity, batch, price, current_date]
        result.append(temp)
        print(temp)
    ExcelHelp.add_arr_to_sheet(PathHelp.get_file_path(None, 'TICAuction240429.xlsx'), 'Auction', result)


if __name__ == "__main__":
    total_page = 3
    for temp_page in range(1, total_page+1):
        time.sleep(1.0)
        get_page_info(temp_page)
    print('over')
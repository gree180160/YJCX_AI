import time
import ssl
from bs4 import BeautifulSoup
import requests
from WRTools import IPHelper, UserAgentHelper, LogHelper, WaitHelp, EmailHelper
from IC_stock import IC_stock_excel_read, IC_Stock_excel_write
from findchips_stock_info import findchips_stock_info_onePart, findchips_stock_info_oneSupplier
from GrabAndDistribute import grab_goods_cate


ssl._create_default_https_context = ssl._create_unverified_context
default_url = 'https://www.findchips.com/'
result_save_file = '/Users/liuhe/PycharmProjects/SeleniumDemo/Findchips_stock/grab_goods_sum.xlsx'
result_sheet_name = 'findchips_0915am'
log_file = '/Users/liuhe/PycharmProjects/SeleniumDemo/Findchips_stock/findchips_stock_log.txt'
cookies = {'fc_locale':'zh-CN', 'fc_timezone':'Asia%2FShanghai'}
headers = {'User-Agent': UserAgentHelper.getRandowUA(),
               'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
               'Accept-Encoding': 'gzip,deflate, br',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Connection': 'keep-alive'}


def get_findchips_stock(cate_index, cate_name):
    headers['User-Agent'] = UserAgentHelper.getRandowUA()
    url = f"https://www.findchips.com/search/{cate_name}"
    print('url is:', url)
    try:
        req = requests.get(url=url, headers=headers, cookies=cookies, proxies=IPHelper.getRandowProxy_contry4(), timeout=(60, 120))
        if cate_index > 0 and cate_index % 15 == 0:
            time.sleep(60 * 8)
        else:
            WaitHelp.waitfor(True, isDebug=False)
    except Exception as e:
        LogHelper.write_log(log_file, f'{cate_name} request get exception: {e}')
        return
    # print(f'respond is :{req.text}')
    soup = BeautifulSoup(req.text, 'lxml')
    try:
        supplier_list = soup.select('div .distributor-results')
        supplier_info_arr = []
        email_info_arr = []
        for element in supplier_list:
            try:
                author = element.find('span', attrs={'class': 'other-disti-details'}).string  # Authorized Distributor
                is_author = ('Authorized Distributor' in author)
            except:
                is_author = False
            if not is_author:
                continue
            else:
                head = element.find('h3', attrs={'class': 'distributor-title'})
                supplier_name = head.find('a').contents[2]
                table = element.find('table')
                tbody = table.find('tbody')
                tr_list = tbody.select('tr')
                stock_sum = 0
                last_ele = None
                for tr in tr_list:
                    td_arr = tr.select('td')
                    part_a = td_arr[0].find('a')
                    part_value = part_a.string
                    part_url = part_a['href']
                    manu_value = td_arr[1].text
                    stock_str = td_arr[3].text
                    part_info = findchips_stock_info_onePart(cate=cate_name, manu=manu_value, supplier=supplier_name,
                                                             authorized=is_author, part_url=part_url,
                                                             stock_str=stock_str)
                    if part_info.is_valid_supplier:
                        last_ele = part_info
                        stock_sum += part_info.stock
                    else:
                        print(f'unvalid_supplier: {part_info.description_str}')
                if last_ele is not None:
                    supplier_info = findchips_stock_info_oneSupplier(cate=cate_name, manu=manu_value,
                                                                     supplier=supplier_name,
                                                                     authorized=is_author, part_url=part_url,
                                                                     stock_sum=stock_sum)
                    supplier_info_arr.append(supplier_info.descritpion_arr())
                    if supplier_info.need_email():
                        email_info_arr.append([supplier_info.supplier, cate_name, supplier_info.stock_sum])
        if len(email_info_arr) > 0:
            EmailHelper.mail_Findchips(email_info_arr)
        email_info_arr.clear()
        IC_Stock_excel_write.add_arr_to_sheet(
            file_name=result_save_file,
            sheet_name=result_sheet_name,
            dim_arr=supplier_info_arr)
        supplier_info_arr.clear()
        WaitHelp.waitfor(False, isDebug=False)
        req = None
        soup = None
    except Exception as e:
        LogHelper.write_log(log_file, f'{cate_name} getStockInfo exception: {e}')


def main():
    all_cates = grab_goods_cate.new_jsonAndGradeA_cates()
    for (cate_index, cate_name) in enumerate(all_cates):
        if cate_index % 2 == 1:
            continue
        if cate_name is None:
            continue
        print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
        get_findchips_stock(cate_index, cate_name)


if __name__ == '__main__':
    main()
import ssl
import time

from bs4 import BeautifulSoup
import requests
from WRTools import IPHelper, UserAgentHelper, LogHelper, WaitHelp, ExcelHelp, PathHelp
from Findchips_stock.findchips_stock_info import findchips_stock_info_onePart, findchips_stock_info_oneSupplier
from Manager import TaskManager


ssl._create_default_https_context = ssl._create_unverified_context

sourceFile_dic = {'fileName': PathHelp.get_file_path(TaskManager.Taskmanger().task_name, 'Task.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': TaskManager.Taskmanger().start_index,
                  'endIndex': TaskManager.Taskmanger().end_index}
result_save_file = PathHelp.get_file_path(TaskManager.Taskmanger().task_name, 'findchip_stock.xlsx')

log_file = PathHelp.get_file_path('Findchips_stock', 'findchips_stock_log.txt')
cookies = {'fc_locale':'zh-CN', 'fc_timezone':'Asia%2FShanghai'}
headers = {'User-Agent': UserAgentHelper.getRandowUA(),
               'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
               'Accept-Encoding': 'gzip,deflate, br',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Connection': 'keep-alive'}
default_url = 'https://www.findchips.com/'


def get_findchips_stock(cate_index, cate_name, send_email):
    headers['User-Agent'] = UserAgentHelper.getRandowUA_Mac()
    url = f"https://www.findchips.com/search/{cate_name}"
    try:
        req = requests.get(url=url, headers=headers, cookies=cookies, timeout=(240, 360))
        if cate_index > 0 and cate_index % 15 == 0:
            WaitHelp.waitfor_account_import(True, False)
        else:
            WaitHelp.waitfor(True, isDebug=False)
    except Exception as e:
        LogHelper.write_log(log_file, f'{cate_name} request get exception: {e}')
        return
    # print(f'respond is :{req.text}')
    if req.status_code != 200:
        LogHelper.write_log(log_file, f'{cate_name} req.status_code: {req.status_code}')
    soup = BeautifulSoup(req.text, 'lxml')
    # 该ppn 没有记录
    if not has_content(soup):
        supplier_info_arr = [[cate_name, "//", '//', False, '', "--"]]
        ExcelHelp.add_arr_to_sheet(
            file_name=result_save_file,
            sheet_name='findchip_stock',
            dim_arr=supplier_info_arr)
        return
    try:
        supplier_list = soup.select('div .distributor-results')
        supplier_info_arr = []
        for element in supplier_list:
            try:
                author = element.find('span', attrs={'class': 'other-disti-details'}).string  # Authorized Distributor
                is_author = ('Authorized Distributor' in author)
            except:
                is_author = False
            if not is_author:
                continue
            else:
                head = element.find('h2', attrs={'class': 'distributor-title'})
                if head is None:
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
                    part_url = part_a['href'][0:30]
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
        ExcelHelp.add_arr_to_sheet(
            file_name=result_save_file,
            sheet_name='findchip_stock',
            dim_arr=supplier_info_arr)
        supplier_info_arr.clear()
        WaitHelp.waitfor(False, isDebug=False)
    except Exception as e:
        LogHelper.write_log(log_file, f'{cate_name} request get exception: {e}')
        supplier_info_arr = [[cate_name, "//", '//', False, '', "//"]]
        ExcelHelp.add_arr_to_sheet(
            file_name=result_save_file,
            sheet_name='findchip_stock',
            dim_arr=supplier_info_arr)


# 是否有合适的搜索结果
def has_content(soup):
    try:
        no_result = soup.find('p', attrs={'class': 'no-results'})
        if no_result == None:
            return True
        else:
            return False
    except:
        return True


def combine_result(source_files:[], aim_file):
    for temp in source_files:
        data = ExcelHelp.read_sheet_content_by_name(file_name=temp, sheet_name='IC_stock')

        ExcelHelp.add_arr_to_sheet(file_name=aim_file, sheet_name='IC_stock', dim_arr=data)
        time.sleep(2.0)



def main():
    all_cates = ExcelHelp.read_col_content(file_name=sourceFile_dic['fileName'],
                                           sheet_name=sourceFile_dic['sourceSheet'],
                                           col_index=sourceFile_dic['colIndex'])
    for (cate_index, cate_name) in enumerate(all_cates):
        if cate_index in range(sourceFile_dic['startIndex'], sourceFile_dic['endIndex']):
            print(f'cate_index is: {cate_index}  cate_name is: {cate_name}')
            if cate_name is None:
                break;
            get_findchips_stock(cate_index, cate_name, send_email=False)


if __name__ == '__main__':
    main()

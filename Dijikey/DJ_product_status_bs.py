import ssl
import time

from bs4 import BeautifulSoup
import requests
from WRTools import IPHelper, UserAgentHelper, LogHelper, WaitHelp, ExcelHelp, PathHelp



ssl._create_default_https_context = ssl._create_unverified_context

sourceFile_dic = {'fileName': PathHelp.get_file_path('TInfenion_40H', 'Task.xlsx'),
                  'sourceSheet': 'ppn',
                  'colIndex': 1,
                  'startIndex': 0,
                  'endIndex': 2}
result_save_file = PathHelp.get_file_path('TInfenion_40H', 'dijikey_status.xlsx')

log_file = '/Users/liuhe/PycharmProjects/SeleniumDemo/Dijikey/DJ_product_status_log.txt'
cookies = {'fc_locale':'zh-CN', 'fc_timezone':'Asia%2FShanghai'}
headers = {'User-Agent': UserAgentHelper.getRandowUA(),
               'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
               'Accept-Encoding': 'gzip,deflate, br',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Connection': 'keep-alive'}
default_url = 'https://www.digikey.com/'


def get_dj_product_status(cate_index, cate_name):
    headers['User-Agent'] = UserAgentHelper.getRandowUA_Mac()
    url = f"https://www.digikey.cn/en/products/detail/*/{cate_name}/4914222?amp%3BWT.z_header=search_go"
    print(f'url is: {url}')
    try:
        req = requests.get(url=url, headers=headers, cookies=cookies, timeout=(600, 360))
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
    try:
        #prodcut description
        try:
            des_table = soup.select('table')[0]
            des_tbody = des_table.select('tbody')[0]
            des_tr = des_tbody.select('tr')[3]
            des_title = des_tr.select('td')[0].text
            if des_title == 'Description':
                des_td = des_tr.select('td')[1]
                des_content = des_td.text
            else:
                des_content = '//'
        except:
            des_content = '//'
        # product status
        try:
            sta_table = soup.select('table')[1]
            sta_tbody = sta_table.select('tbody')[0]
            sta_tr = sta_tbody.select('tr')[4]

            status_title = sta_tr.select('td')[0].text
            if status_title == 'Product Status':
                sta_td = sta_tr.select('td')[1]
                status_content = sta_td.text
            else:
                status_content = '//'
        except:
            status_content = '//'
        result = [cate_name, des_content, status_content]
        WaitHelp.waitfor(False, isDebug=False)
    except Exception as e:
        LogHelper.write_log(log_file, f'{cate_name} request get exception: {e}')
        result = [[cate_name, "//", '//']]
    ExcelHelp.add_arr_to_sheet(
            file_name=result_save_file,
            sheet_name='dijikey_status',
            dim_arr=[result])


def combine_result(source_files:[], aim_file):
    for temp in source_files:
        data = ExcelHelp.read_sheet_content_by_name(file_name=temp, sheet_name='dijikey_status')
        ExcelHelp.add_arr_to_sheet(file_name=aim_file, sheet_name='dijikey_status', dim_arr=data)
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
            get_dj_product_status(cate_index, cate_name)


if __name__ == '__main__':
    # main()
    combine_result(["/Users/liuhe/Desktop/progress/TInfineon/55H/11/dijikey_status.xlsx", "/Users/liuhe/Desktop/progress/TInfineon/55H/sz/dijikey_status.xlsx", "/Users/liuhe/Desktop/progress/TInfineon/55H/04/dijikey_status.xlsx"], PathHelp.get_file_path('TInfenion_55H', 'dijikey_status.xlsx'))
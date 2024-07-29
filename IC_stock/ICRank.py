# 根据关键字查找P/N, manu
from bs4 import BeautifulSoup
from WRTools import LogHelper, PathHelp, ExcelHelp
from Manager import URLManager
from urllib.parse import parse_qs
import os
import re
from urllib.parse import urlparse


result_file = PathHelp.get_file_path(None, 'TICHot_202402.xlsx')
sheet_name = "ppn"
file_path = PathHelp.get_file_path("IC_stock", 'view-source_https___icpi.ic.net.cn_hotsearch.html')
log_file = PathHelp.get_file_path("IC_stock", 'IC_log.txt')


# get ppn
def get_category(file_name):
    path = file_name
    htmlfile = open(path, 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    soup = BeautifulSoup(htmlhandle, 'html5lib')
    analyth_html(soup=soup)


# 解析html，获取cate，kind
def analyth_html(soup):
    info_list = []
    try:
        tables = soup.select('table.pinleri_tb')
        kinds = ['hot', 'search_increase', 'price_increase', 'price_decrease']
        for (table_index, table) in enumerate(tables):
            if table_index < 4: # hot
                table_info = deal(table, kinds[table_index])
                info_list = info_list + table_info
    except Exception as e:
        print('analyth_html error')
    print(info_list)
    ExcelHelp.add_arr_to_sheet(result_file, sheet_name, info_list)


def deal(table, kind) -> list:
    reuslt = []
    trs = table.select('tr.data-v-ee76e850')[1:]
    for tr in trs:
        a = tr.select('a')[0]
        ppn = [a.text, kind]
        reuslt.append(ppn)
    return reuslt


if __name__ == "__main__":
    get_category(file_name=file_path)

    # STM32F103C8T6, STM32F407VET6, STM32F103RCT6, LM358DR, STM8S003F3P6TR, ULN2803ADWR, STM32F405RGT6, STM32F030K6T6, ATMEGA8A - AU, XCF32PFSG48C, ST7FLITE05Y0B6, 88
    # F6820 - B0 - BRT4I160, IRFR9120NTRPBF, XC3S500E - 4
    # FTG256I, CC1120RHBR, LMD18400N / NOPB, IRFP4310ZPBF, CC1310F128RGZR, XC7VX1140T - 2
    # FLG1928I, MSP430F5437AIPN, SN74HC574N, AMS1117 - 3.3
    # V, MC78M05BDTRKG, PIC16F877A - I / PT, BQ24715RGRR, TLC5615ID, AO3400A, SMBJ15A, DRV2603RUNR, 24L
    # C512T - I / SN, TLV70018DDCR, SN65HVD33DR, TMS320F28027PTT, SDINBDG4 - 8
    # G, SN74HC374N, RT9193 - 33
    # GB, SN65MLVD206DR, OPA277U, MT40A512M16TB - 062
    # E: R, LM66100DCKR,
'''
var textContents = [];
var trTags = document.querySelectorAll('tr');
trTags.forEach(function(tr) {
    var aTags = tr.querySelectorAll('a');
    aTags.forEach(function(a) {
        textContents.push(a.textContent);
    });
});

var textContents = [];
var trTags = document.querySelectorAll('div[data-v-31b6cba6]');
trTags.forEach(function(tr) {
    var aTags = tr.querySelectorAll('span');
    aTags.forEach(function(a) {
        textContents.push(a.textContent);
    });
});

// 创建一个新的div元素来展示结果
var resultDiv = document.createElement('div');
resultDiv.textContent = textContents.join(', '); // 将数组内容以逗号分隔显示
document.body.appendChild(resultDiv);
'''
# const productNames = Array.from(document.querySelectorAll('.h2')).map(name => name.textContent.trim());
# console.log(productNames);
from WRTools import ExcelHelp, PathHelp
from enum import Enum
import base64
import re


class Octopart_manu(Enum):
    NoManu = 0
    Allegro = 1
    Infineon = 2
    Holt = 3
    Renesas = 4
    ADI = 5
    NXP = 6
    Skyworks = 7
    Texas_Instruments = 8
    Vishay = 9
    Vicor = 10
    Microchip = 11
    VPT = 12
    Altera = 13
    XILINX = 14
    Onsemi = 15
    STMicroelectronics = 16

    def get_manu(self) -> str:
        manuid_list = [
            '',
            '8330',
            '453;202;706;12547;196',
            '1279',
            '572;203;833',
            '26;244;12048;2274',
            '561;296;145',
            '1967;583',
            '262;370;1148',
            '',
            '2089',
            '252;45;523;2631;1047;1727',
            '12444',
            '199;14939',
            '7;404',
            '278;473;1595',
            '355',
        ]
        return manuid_list[self.value]


# octopart
# https://octopart.com/search?q=PIC18&currency=USD&specs=0
def octopart_get_page_url(key_name, page, manu: Octopart_manu) -> str:
    cate_str = str(key_name)
    cate_str = cate_str.replace('/', '%2F')
    cate_str = cate_str.replace('#', '%23')
    cate_str = cate_str.replace('+', '%2B')
    cate_str = cate_str.replace(',', '%2C')

    if manu.value > 0:
        manu_str = manu.get_manu()
        manu_param = '&manufacturer_id=' + manu_str.replace(';', '&manufacturer_id=')
    else:
        manu_param = ''
    page_param = '' if page == 1 else '&start=' + str(page*10 - 10)
    url = f'https://octopart.com/search?q={cate_str}&currency=USD&specs=0{manu_param}{page_param}'
    return url


# octopart
def octopart_get_code_url(key_name, page, manu: Octopart_manu) -> str:
    cate_str = str(key_name)
    cate_str = cate_str.replace('/', '%2F')
    cate_str = cate_str.replace('#', '%23')
    cate_str = cate_str.replace('+', '%2B')
    cate_str = cate_str.replace(',', '%2C')

    if manu.value > 0:
        manu_str = manu.get_manu()
        manu_param = '&manufacturer_id=' + manu_str.replace(';', '&manufacturer_id=')
    else:
        manu_param = ''
    page_param = '' if page == 1 else '&start=' + str(page*10 - 10)
    url = f'view-source:https://octopart.com/search?q={cate_str}&currency=USD&specs=0{manu_param}{page_param}'
    return url


# 根据keyname page 0 的数据获取total page ，然后获取page 0 之后的页面的url并保存
def octopart_page_more_url(sourcefile: str, page0_sheet: str, manu: Octopart_manu):
    pn_file = sourcefile
    pninfo_list = ExcelHelp.read_sheet_content_by_name(file_name=pn_file, sheet_name=page0_sheet)
    last_search_param = ''
    for pnInfo in pninfo_list:
        pninfo_url_list = []
        try:
            if pnInfo is None:
                continue
            key_name = str(pnInfo[2])
            if key_name is None:
                continue
            current_search_param = key_name
            if current_search_param == last_search_param:
                continue
            else:
                last_search_param = current_search_param
            total_p = int(pnInfo[3])
            current_p = 2
            if total_p > 1:
                while current_p <= total_p:
                    url = octopart_get_page_url(key_name=key_name, page=current_p, manu=manu)
                    pninfo_url_list.append([url])
                    current_p += 1
        except:
            print(pnInfo + "exception")
        if pninfo_url_list.__len__() > 0:
            ExcelHelp.add_arr_to_sheet(file_name=pn_file, sheet_name='url_pagemore2', dim_arr=pninfo_url_list)
    print('over')


# IC 交易网

def IC_stock_url(ppn: str, page=0):
    cate_str = str(ppn)
    cate_str = cate_str.replace('/', '%2F')
    cate_str = cate_str.replace('#', '%23')
    cate_str = cate_str.replace('+', '%2B')
    cate_str = cate_str.replace(',', '%2C')
    return f"https://www.ic.net.cn/search/{cate_str}.html?isExact=1&page={page}"


def IC_hot_url(ppn: str):
    cate_str = str(ppn)
    cate_str = cate_str.replace('/', '%2F')
    cate_str = cate_str.replace('#', '%23')
    cate_str = cate_str.replace('+', '%2B')
    cate_str = cate_str.replace(',', '%2C')
    search_url = f'https://icpi.ic.net.cn/detail_icpi?partno={cate_str}'
    return search_url


# https://fh.hqew.com/detail/500020657.html
def HQ_hot_url(ppn: str):
    cate_str = str(ppn)
    if has_special_chars(cate_str):
        cate_str = '==' + str(base64.b64encode(cate_str.encode('utf-8')), 'utf-8')
    search_url = f'https://fh.hqew.com/detail/{cate_str}.html'
    return search_url


# https://s.hqew.com/ULN2003ADR_10.html
def HQ_stock_url(ppn: str):
    cate_str = str(ppn)
    if has_special_chars(cate_str):
        cate_str = '==' + str(base64.b64encode(cate_str.encode('utf-8')), 'utf-8')
    search_url = f'https://s.hqew.com/{cate_str}_10.html'
    return search_url


def has_special_chars(text):
    pattern = re.compile('[^a-zA-Z0-9\s]')  # 匹配非字母、数字和空格的字符
    if pattern.search(text):
        return True
    else:
        return False


if __name__ == "__main__":
    # octopart_page_more_url(sourcefile=PathHelp.get_file_path(None, file_name='TSkyworks.xlsx'), page0_sheet='page0_ppn_2', manu=Octopart_manu.Skyworks)
    print(HQ_hot_url('ADC0804LCWMX/NOPB'))
    print(HQ_hot_url('M4T32-BR12SH1'))
    print(HQ_hot_url('STB120NF10T4'))



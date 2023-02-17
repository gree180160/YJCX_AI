import string
import time
import re


class findchips_stock_info_onePart:
    def __init__(self, cate, manu, supplier, authorized, part_url, stock_str):
        self.cate = cate
        self.manu = reggularStr(manu)  # 使用findchips 数据
        self.supplier = reggularStr(supplier)
        self.authorized = authorized
        self.part_url = get_short_url(supplier=self.supplier, url=reggularStr(part_url), cate_name=cate)
        self.stock_str = reggularStr(stock_str)
        self.stock = get_stock(stock_str)

    def is_valid_supplier(self) -> bool:
        result = False
        if self.authorized:
            if not self.supplier.__contains__('Flip Electronics ECIA Member'):
                result = True
        return result

    def description_str(self) -> string:
        result = f'{self.cate or "--"}, {self.manu or "--"}, {self.supplier}, {self.authorized}, {self.part_url}, {self.stock_str}, {self.stock}'
        return result


class findchips_stock_info_oneSupplier:
    def __init__(self, cate, manu, supplier, authorized, part_url, stock_sum):
        self.cate = cate
        self.manu = reggularStr(manu)  # 使用findchips 数据
        self.supplier = reggularStr(supplier)
        self.authorized = authorized
        self.part_url = get_short_url(supplier=self.supplier, url=reggularStr(part_url), cate_name=cate)
        self.stock_sum = stock_sum
        self.search_date = time.strftime('%Y-%m-%d', time.localtime())

    def need_email(self):
        return self.stock_sum > 0

    def description_str(self) -> string:
        result = f'{self.cate or "--"}, {self.manu or "--"}, {self.supplier}, {self.authorized}, {self.part_url}, {self.stock_sum}, {self.search_date}'
        return result

    def descritpion_arr(self) -> list:
        result = [self.cate or "--", self.manu or "--", self.supplier, self.authorized, self.part_url, self.stock_sum, self.search_date]
        return result


#     delete /n and space at begin and end
def reggularStr(source):
    result = source.replace('\n', '')
    result = result.strip()
    return result


def get_short_url(supplier, url, cate_name) -> string:
        result = url
        if ('Arrow ') in supplier:
            result = f'https://www.arrow.com/en/products/{cate_name}/murata-manufacturing?&utm_source=findchips'
        elif supplier == 'TTI':
            result = f'https://www.tti.com/content/ttiinc/en/apps/part-detail.html?partsNumber={cate_name}&mfgShortname=MUR&utm=704'
        elif supplier == 'Mouser Electronics':
            result = f'https://www.mouser.cn/ProductDetail/Murata-Electronics/{cate_name}?qs=to8XolpOzrOREPd%2Fx%2FLxrw%3D%3D&utm_source=findchips'
        elif 'Verical' in supplier:
            result = f'https://www.verical.com/pd/murata-manufacturing-ceramic---multilayer-{cate_name}?utm_source=findchips'
        elif 'Chip1Stop' in supplier:
            result = f'https://www.chip1stop.com/product/detail?partId=MURA-0093105&utm_term={cate_name}&cid=MURA-0093105'
        return result


def get_stock(stock_str) -> int:
        result = 0
        if stock_str is None or (stock_str == 0):
            return result
        if len(stock_str) == 0:
            return result
        if 'Out of Stock' in stock_str:
            return result
        if 'On Order' in stock_str:
            return result
        digital = ''.join(re.findall('[0-9]',stock_str))   # 只保留数字
        if digital.__len__() > 0:
            result = int(digital)
        else:
            result = 0
        return result


if __name__ == '__main__':
    reggularStr('                            Mean Well')
   # a = get_stock('Temporarily Out of Stock')
   # b = get_stock('66 On Order')
   # c = get_stock('Americas - 0')
   # d = get_stock('Americas 2373')
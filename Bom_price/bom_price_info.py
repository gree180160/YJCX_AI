import time


class Bom_price_info:
    def __init__(self, cate, manu, supplier, package, year, quoted_price, release_time, stock_num):
        self.cate = cate
        self.manu = manu
        self.supplier = supplier
        self.package = package  # 封装
        self.year = year
        self.quoted_price = quoted_price
        self.release_time = release_time
        self.stock_num = stock_num
        self.search_date = time.strftime('%Y-%m-%d', time.localtime())

    def is_valid_supplier(self) -> bool:
        valid_time_arr = ['3天内', '1周内']
        if valid_time_arr.__contains__(self.release_time):
            return True
        else:
            return False

    def description_str(self):
        result = f'{self.cate or "--"}, {self.manu or "--"}, {self.supplier}, {self.package}, {self.year}, {self.quoted_price}, {self.release_time}, {self.stock_num}, {self.search_date}'
        return result

    def descritpion_arr(self):
        result = [self.cate or "--", self.manu or "--", self.supplier, self.package, self.year, self.quoted_price, self.release_time, self.stock_num, self.search_date]
        return result



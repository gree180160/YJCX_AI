import time
import WRTools.WaitHelp


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
        self.valid_supplier = self.is_valid_supplier()

    def is_valid_supplier(self) -> bool:
        valid_time_arr = ['3天内', '1周内']
        if valid_time_arr.__contains__(self.release_time):
            return True
        else:
            numberDays = WRTools.WaitHelp.daysPassed(self.release_time)
            if 0 < numberDays <= 8:
                return True
            return False

    def description_str(self):
        result = f'{self.cate or "--"}, {self.manu or "--"}, {self.supplier}, {self.package}, {self.year}, {self.quoted_price}, {self.release_time}, {self.stock_num}, {self.search_date}, {"valid supplier" if self.valid_supplier else "invalid supplier"}'
        return result

    def descritpion_arr(self):
        result = [self.cate or "--",
                  self.manu or "--",
                  self.supplier,
                  self.package,
                  self.year,
                  self.quoted_price,
                  self.release_time,
                  self.stock_num,
                  self.search_date,
                  self.valid_supplier]
        return result


if __name__ == "__main__":
    WRTools.WaitHelp.daysPassed('2023-01-12')
    WRTools.WaitHelp.daysPassed('2023-01-13')
    WRTools.WaitHelp.daysPassed('2023-01-10')
    WRTools.WaitHelp.daysPassed('3天内')



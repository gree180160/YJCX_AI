import time
import WRTools.WaitHelp


class Bom_price_info:
    def __init__(self, cate, manu, supplier, package, lot, quoted_price, release_time, stock_num):
        self.cate = cate
        self.manu = manu
        self.supplier = supplier
        self.package = package  # 封装
        self.lot = lot
        self.quoted_price = quoted_price.replace('官\n', '')
        self.release_time = release_time
        self.stock_num = stock_num
        self.valid_supplier = self.is_valid_supplier()

    def is_valid_supplier(self) -> bool:
        if self.supplier.__contains__("此供应商选择了隐藏公司名"):
            return False
        if self.quoted_price.__contains__("*"):
            return False
        if self.release_time.__contains__('周') or self.release_time.__contains__('API实时'):
            return True
        valid_time_arr = ['3天内', '1周内', '今天', '昨天', '1月内']
        if valid_time_arr.__contains__(self.release_time):
            return True
        else:
            numberDays = WRTools.WaitHelp.daysPassed(self.release_time)
            if 0 < numberDays <= 30: #8
                return True
            else:
                print(f'thatDay invalid: {self.release_time}')
            return False

# (`ppn`, `manu`, `supplier`, `package`, `lot`, `quoted_price`, `release_time`, `stock_num`, `valid_supplier`)
    def description_str(self):
        result = f'{self.cate or "--"}, {self.manu or "--"}, {self.supplier}, {self.package}, {self.lot}, {self.quoted_price}, {self.release_time}, {self.stock_num}, {"valid supplier" if self.valid_supplier else "invalid supplier"}'
        return result

    def descritpion_arr(self):
        result = [self.cate or "--",
                  self.manu or "--",
                  self.supplier,
                  self.package,
                  self.lot,
                  self.quoted_price,
                  self.release_time,
                  self.stock_num,
                  self.valid_supplier]
        return result


if __name__ == "__main__":
    WRTools.WaitHelp.daysPassed('2023-01-12')
    WRTools.WaitHelp.daysPassed('2023-01-13')
    WRTools.WaitHelp.daysPassed('2023-01-10')
    WRTools.WaitHelp.daysPassed('3天内')



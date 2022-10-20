import time


class Octopart_price_info:
    def __init__(self, cate, manu, is_star, distribute, SKU, stock, MOQ, currency_type, k_price, updated):
        self.cate = cate
        self.manu = manu
        self.is_star = is_star
        self.distribute = distribute
        self.SKU = SKU
        self.stock = stock
        self.MOQ = MOQ
        self.currency_type = currency_type
        self.k_price = k_price
        self.updated = updated
        self.search_date = time.strftime('%Y-%m-%d', time.localtime())

    def is_valid_supplier(self) -> bool:
        if self.is_star > 0:
            return True
        else:
            return False

    def stop_loop(self) -> bool:
        if self.is_star < 0:
            return True
        else:
            return False

    def description_str(self):
        result = f'{self.cate or "--"}, {self.manu or "--"}, {self.is_star}, {self.distribute}, {self.SKU}, {self.stock}, {self.MOQ}, {self.currency_type}, {self.updated}, {self.search_date} '
        return result

    def descritpion_arr(self):
        result = [self.cate or "--", self.manu or "--", self.is_star, self.distribute, self.SKU, self.stock, self.MOQ,
                  self.currency_type, self.k_price, self.updated, self.search_date]
        return result



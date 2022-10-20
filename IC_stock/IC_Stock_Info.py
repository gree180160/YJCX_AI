import time


class IC_Stock_Info:
    def __init__(self, supplier, isICCP, isSSCP, model, isSpotRanking, isHotSell, manufacturer, stock_num, search_date):
        self.supplier = supplier
        self.isICCP = isICCP
        self.isSSCP = isSSCP
        self.model = model
        self.isSpotRanking = isSpotRanking
        self.isHotSell = isHotSell
        self.Manufacturer = manufacturer
        self.stock_num = stock_num
        self.search_date = search_date

    def shouldSave(self):
        result = False
        if self.isICCP or self.isSSCP or self.isSpotRanking or self.isHotSell:
            result = True
        return result

    def description_str(self):
        result = f'{self.supplier or "--"} , {"ICCP" if self.isICCP else "notICCP"} ,  {"SSCP" if self.isSSCP else "notSSCP"}, {self.model or "--"} , {"SpotRanking" if self.isSpotRanking else "notSpotRanking"} , {"HotSell" if self.isHotSell else "notHotSell"} , {self.Manufacturer or "--"} , {self.stock_num} , {time.strftime("%Y-%m-%d", time.localtime())}'
        return result

    def descritpion_arr(self):
        result = [self.supplier or "--", "ICCP" if self.isICCP else "notICCP", "SSCP" if self.isSSCP else "notSSCP", self.model or "--", "SpotRanking" if self.isSpotRanking else "notSpotRanking", "HotSell" if self.isHotSell else "notHotSell", self.Manufacturer or "--", self.stock_num, self.search_date]
        return result

    def is_valid_supplier(self):
        if self.isICCP or self.isSSCP:
            return True
        else:
            return False

    def get_valid_stock_num(self):
        result = 0
        if self.isSpotRanking:
            result = int(self.stock_num)
        else:
            if self.isICCP or self.isSSCP:
                result = int(self.stock_num)
        return result

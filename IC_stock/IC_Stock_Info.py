
class IC_Stock_Info:
    def __init__(self, supplier, isICCP, isSSCP, model, isSpotRanking, isHotSell, batch, pakaging, manufacturer, stock_num):
        self.supplier = supplier
        self.isICCP = isICCP
        self.isSSCP = isSSCP
        self.model = model
        self.isSpotRanking = isSpotRanking
        self.isHotSell = isHotSell
        self.batch:str = str(batch)
        self.pakaging = pakaging
        self.Manufacturer = manufacturer
        self.stock_num = stock_num

    def shouldSave(self):
        result = False
        if self.isICCP or self.isSSCP or self.isSpotRanking:
            result = True
        return result

    def description_str(self):
        result = f'{self.model or "--"}, {self.Manufacturer or "--"} , {self.supplier or "--"}, {"ICCP" if self.isICCP else "notICCP"}, {"SSCP" if self.isSSCP else "notSSCP"}, {"SpotRanking" if self.isSpotRanking else "notSpotRanking"}, {"HotSell" if self.isHotSell else "notHotSell"}, {self.batch}, {self.pakaging}, {self.stock_num}'
        return result

    def descritpion_arr(self):
        #(ppn, manu, supplier, isICCP, isSSCP, iSRanking, isHotSell, batch, pakaging, stock_num)
        result = [self.model or "--",
                  self.Manufacturer or "--",
                  self.supplier or "--",
                  1 if self.isICCP else 0,
                  1 if self.isSSCP else 0,
                  1 if self.isSpotRanking else 0,
                  1 if self.isHotSell else 0,
                  self.batch,
                  self.pakaging,
                  self.stock_num]
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


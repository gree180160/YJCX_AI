from WRTools import StringHelp


class IC_Stock_Info:
    def __init__(self, supplier, isICCP, isSSCP, model, st_manu, isSpotRanking, isHotSell,isYouXian, batch, pakaging, supplier_manu, stock_num):
        self.supplier = supplier
        self.isICCP = isICCP
        self.isSSCP = isSSCP
        self.model = model
        self.st_manu = st_manu
        self.isSpotRanking = isSpotRanking
        self.isHotSell = isHotSell
        self.isYouXian = isYouXian
        self.batch:str = StringHelp.IC_batch(str(batch))
        self.pakaging = pakaging
        self.supplier_manu = supplier_manu
        self.stock_num = stock_num

    def description_str(self):
        result = f'{self.model or "--"},{self.st_manu or "--"}, {self.supplier_manu or "--"} , {self.supplier or "--"}, {"ICCP" if self.isICCP else "notICCP"}, {"SSCP" if self.isSSCP else "notSSCP"}, {"SpotRanking" if self.isSpotRanking else "notSpotRanking"}, {"HotSell" if self.isHotSell else "notHotSell"},{"YouXian" if self.isYouXian else "notYouXian"}, {self.batch}, {self.pakaging}, {self.stock_num}'
        return result

    def descritpion_arr(self):
        # (ppn, st_manu, supplier_manu, supplier, isICCP, isSSCP, iSRanking, isHotSell, stock_num)
        result = [self.model or "--",
                  self.st_manu or "--",
                  self.supplier_manu or "--",
                  self.supplier or "--",
                  1 if self.isICCP else 0,
                  1 if self.isSSCP else 0,
                  1 if self.isSpotRanking else 0,
                  1 if self.isHotSell else 0,
                  1 if self.isYouXian else 0,
                  self.batch,
                  self.pakaging,
                  self.stock_num]
        return result

    # *************for not manu **************
    def is_valid_supplier(self):
        if self.isICCP or self.isSSCP or self.isSpotRanking:
            return True
        else:
            return False

    def shouldSave(self):
        result = False
        if self.isICCP or self.isSSCP or self.isSpotRanking:
            result = True
        return result

    def get_valid_stock_num(self):
        result = 0
        if self.isSpotRanking or self.isICCP or self.isSSCP:
            result = int(self.stock_num)
        return result

    # *************for not holt **************
    def shouldSave_holt(self):
        result = False
        if self.isICCP or self.isSSCP or self.isYouXian or self.isSpotRanking:
            result = True
        return result

    def is_valid_supplier_holt(self):
        if self.isICCP or self.isSSCP or self.isYouXian or self.isSpotRanking:
            return True
        else:
            return False

    def get_valid_stock_num_holt(self):
        result = 0
        if self.isICCP or self.isSSCP or self.isYouXian or self.isSpotRanking:   #or self.isHotSell
            result = int(self.stock_num)
        return result


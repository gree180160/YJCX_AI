# 供应商信息
class Supplier_count_struct:
    supplier_name: str
    ppn_count: int

    def __init__(self, supplier_name):
        self.supplier_name = supplier_name
        self.ppn_count = 0


#   品牌的供应商信息
class Manu_supp:
    manu_name: str
    supplier_info: [Supplier_count_struct]

    def __init__(self, manu_name):
        self.manu_name = manu_name
        self.supplier_info = []

    #  写入数据
    def input_record(self, manu_name: str, supplier_name: str):
        if self.manu_name == manu_name:
            supplier_index = None
            for (index, temp_supplier) in enumerate(self.supplier_info):
                if temp_supplier.supplier_name == supplier_name:
                    supplier_index = index
                    break
            if supplier_index is None:
                self.supplier_info.append(Supplier_count_struct(supplier_name=supplier_name))
                supplier_index = len(self.supplier_info) - 1
            self.supplier_info[supplier_index].ppn_count += 1

    #  到处数据，导出的是一个二维数组
    def output_record(self) -> list:
        result = []
        self.supplier_info = sorted(self.supplier_info, key=lambda x: x.ppn_count, reverse=True)
        for temp_sup in self.supplier_info:
            info = [self.manu_name, temp_sup.supplier_name, temp_sup.ppn_count]
            result.append(info)
        return result

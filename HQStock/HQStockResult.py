# 计算cate
# 输入型号 输出两个字段：
# （1） 靠谱供应商数量（记录中有且只有'原装'&'原装排名'两种)
# （2） 靠谱库存数量


from WRTools import PathHelp, ExcelHelp, MySqlHelp_recommanded


# 将同一个ppn到所有stock 累加，然后按照保存到数组中
def HQ_stock_sum(cate_source_file, sheetname):
    pps = ExcelHelp.read_col_content(file_name= cate_source_file, sheet_name=sheetname, col_index=1)
    manufactures = ExcelHelp.read_col_content(file_name= cate_source_file, sheet_name=sheetname, col_index=2)
    HQ_stocks = ExcelHelp.read_sheet_content_by_name(cate_source_file, sheet_name='HQ_stock')
    result = []
    for (index, temp_ppn) in enumerate(pps):
        ppn_str = str(temp_ppn)
        if ppn_str == 'ppn':
            continue
        valid_supplier_sum = 0
        valid_stock_sum = 0
        # ppn, std_manu, supplier, sup_manu, batch, stock, packing, param, place, instruction, publish_date, task_name
        for (row_index, row_content) in enumerate(HQ_stocks):
            ppn_ic = str(row_content[0])
            if ppn_ic.upper() == ppn_str.upper():
                stock_num = int(row_content[6])
                if stock_num < 10:
                    valid_supplier_sum += 0.01
                else:
                    valid_supplier_sum += 1.0
                valid_stock_sum += stock_num
        result.append([ppn_str, manufactures[index], valid_supplier_sum, int(valid_stock_sum)])
    ExcelHelp.add_arr_to_sheet(file_name=cate_source_file, sheet_name="HQ_stock_sum", dim_arr=result)


def read_record(save_file, task_name):
    record = MySqlHelp_recommanded.DBRecommandChip().hq_stock_read(f'task_name = "{task_name}"')
    ExcelHelp.add_arr_to_sheet(save_file, 'HQ_stock', record)


if __name__ == "__main__":
    aim_file = PathHelp.get_file_path(None, 'TRU202412_1k.xlsx')
    task_name = 'TRU202412_1k'
    read_record(aim_file, task_name)
    HQ_stock_sum(aim_file, 'ppn')
    print('over')

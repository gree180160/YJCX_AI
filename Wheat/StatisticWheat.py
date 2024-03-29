from WRTools import ExcelHelp, PathHelp


def statistic_buy():
    ppn_list = ExcelHelp.read_col_content(file_name=PathHelp.get_file_path('Wheat', 'WheatTask.xlsx'), sheet_name='manu', col_index=1)
    source_file = PathHelp.get_file_path('Wheat', 'wheat_buyer.xlsx')
    sheet_content = ExcelHelp.read_sheet_content_by_name(file_name=source_file, sheet_name='manu_record')
    all_info = []
    for ppn in ppn_list:
        # [ppn, record_number, buyer_number]
        ppn_info = [ppn, 0, 0]
        buyer_list = []
        for row in sheet_content:
            if row[0] == ppn:
                buyer_list.append(row[2])
        if buyer_list.__len__() > 0:
            ppn_info = [ppn, buyer_list.__len__(), list(set(buyer_list)).__len__()]
        all_info.append(ppn_info)
    ExcelHelp.add_arr_to_sheet(file_name=source_file, sheet_name='statistic_manu', dim_arr=all_info)


if __name__ == "__main__":
    statistic_buy()
import Arrow_transition
import Findchips_stock
from IC_stock import IC_stock_excel_read, IC_Stock_excel_write
from openpyxl import load_workbook


def arrow_data_combine():
    source_file = '/Users/liuhe/Desktop/progress/0906/myarrow/arrow_transition_cate_0906.xlsx'
    aim_file = '//GrabAndDistribute/grab_Distribute_cate_0906.xlsx'
    aim_sheet = 'myarrow'
    wb = load_workbook(source_file)
    for (index, sheet) in enumerate(wb.worksheets):
        source_list = IC_stock_excel_read.get_sheet_content_by_index(file_name=source_file, sheet_index=index)
        IC_Stock_excel_write.add_arr_to_sheet(file_name=aim_file, sheet_name=aim_sheet, dim_arr=source_list)


if __name__ == '__main__':
    arrow_data_combine()

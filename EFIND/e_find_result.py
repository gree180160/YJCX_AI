from WRTools import PathHelp, ExcelHelp, WaitHelp, MySqlHelp_recommanded
import re
import json
from urllib.request import urlopen


def read_record(save_file, task_name):
    record = MySqlHelp_recommanded.DBRecommandChip().efind_supplier_read(f'task_name = "{task_name}"')
    ExcelHelp.add_arr_to_sheet(save_file, 'efind_supplier', record)


if __name__ == "__main__":
    aim_file = PathHelp.get_file_path(None, 'TRU202412_7k.xlsx')
    task_name = 'TRU202412_7k'
    read_record(aim_file, task_name)
    # HQ_stock_sum(aim_file, 'ppn4')
    print('over')
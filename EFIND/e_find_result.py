import time

from WRTools import PathHelp, ExcelHelp, WaitHelp, Record_data
import re
import json
from urllib.request import urlopen


def read_record(save_file, task_name):
    record = Record_data.RecordData().efind_supplier_read(f'task_name = "{task_name}"')
    ExcelHelp.add_arr_to_sheet(save_file, 'efind_supplier', record)


if __name__ == "__main__":
    aim_file = PathHelp.get_file_path(None, 'TRenesasIsolators.xlsx')
    task_name = 'TRenesasIsolators'
    read_record(aim_file, task_name)
    print('over')
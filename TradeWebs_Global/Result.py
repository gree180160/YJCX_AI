import time

from WRTools import PathHelp, ExcelHelp, Record_data
import re


def read_record_future(save_file, task_name):
    record = Record_data.RecordData().future_info_read(f'task_name = "{task_name}"')
    ExcelHelp.add_arr_to_sheet(save_file, 'future', record)


def read_record_arrow(save_file, task_name):
    record = Record_data.RecordData().arrow_info_read(f'task_name = "{task_name}"')
    ExcelHelp.add_arr_to_sheet(save_file, 'arrow', record)


if __name__ == "__main__":
    aim_file = PathHelp.get_file_path(None, 'TRenesasIsolators.xlsx')
    task_name = 'TRenesasIsolators'
    read_record_future(aim_file, task_name)
    time.sleep(10.0)
    read_record_arrow(aim_file, task_name)
    print('over')
from Manager import AccManage
from WRTools import MySqlHelp_recommanded


class Taskmanger:
    task_name = 'TInfineonIGBT'
    if AccManage.Device_ID == 'Mac':
        start_index = 0
        end_index = 250
    elif AccManage.Device_ID == '11':
        start_index = 250
        end_index = 500
    elif AccManage.Device_ID == 'sz':
        start_index = 500
        end_index = 750
    elif AccManage.Device_ID == '42':
        start_index = 750
        end_index = 1000
    elif AccManage.Device_ID == '04':
        start_index = 1000
        end_index = 1250


class Task_IC_hot_F_manger:
    task_name = 'TVicor'
    base = 11700 #11100 finished
    start_index = base + 60
    end_index = base + 79


class Task_IC_hot_C_manger:
    task_name = 'TVicor'
    base = 11800
    start_index = base + 79
    end_index = base + 100




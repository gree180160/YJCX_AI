from Manager import AccManage
from WRTools import MySqlHelp_recommanded


class Taskmanger:
    task_name = 'TYjcxCloundStock'
    if AccManage.Device_ID == 'Mac':
        start_index = 1
        end_index = 1000
    elif AccManage.Device_ID == '11':
        start_index = 1000
        end_index = 2000
    elif AccManage.Device_ID == 'sz':
        start_index = 2000
        end_index = 3000
    elif AccManage.Device_ID == '42':
        start_index = 3000
        end_index = 4000
    elif AccManage.Device_ID == '04':
        start_index = 4000
        end_index = 5000


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




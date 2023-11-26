from Manager import AccManage
from WRTools import MySqlHelp_recommanded


class Taskmanger:
    task_name = 'TRuStock'
    if AccManage.Device_ID == 'Mac':
        start_index = 0
        end_index = 350
    elif AccManage.Device_ID == '11':
        start_index = 400
        end_index = 800
    elif AccManage.Device_ID == 'sz':
        start_index = 800
        end_index = 1200
    elif AccManage.Device_ID == '42':
        start_index = 1200
        end_index = 1600
    elif AccManage.Device_ID == '04':
        start_index = 1600
        end_index = 2000


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




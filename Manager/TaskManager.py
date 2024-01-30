from Manager import AccManage
from WRTools import MySqlHelp_recommanded


class Taskmanger:
    # task_name = 'TRUNeeds202401'
    task_name = 'TAliceHolt'
    if AccManage.Device_ID == 'Mac':
        start_index = 0
        end_index = 700
    elif AccManage.Device_ID == '11':
        start_index = 700
        end_index = 1400
    elif AccManage.Device_ID == 'sz':
        start_index = 1400
        end_index = 2100
    elif AccManage.Device_ID == '42':
        start_index = 2100 #3000-3189
        end_index = 2800
    elif AccManage.Device_ID == '04':
        start_index = 2800# 4000-4182
        end_index = 3390


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




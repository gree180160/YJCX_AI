from Manager import AccManage
from WRTools import MySqlHelp_recommanded


class Taskmanger:
    task_name = 'TRuStock'
    if AccManage.Device_ID == 'Mac':
        start_index = 0
        end_index = 660
    elif AccManage.Device_ID == '11':
        start_index = 660
        end_index = 1320
    elif AccManage.Device_ID == 'sz':
        start_index = 1320
        end_index = 1980
    elif AccManage.Device_ID == '42':
        start_index = 1980
        end_index = 2640
    elif AccManage.Device_ID == '04':
        start_index = 2640
        end_index = 3300


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
    # task_name = 'TTI'
    # base = 2000
    # start_index = base + 0
    # end_index = base + 100

#
# class DB_Task:
#     def get_sum_ppn(self):
#         MySqlHelp.IC_hot_m_read()

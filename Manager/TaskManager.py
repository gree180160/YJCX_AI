from Manager import AccManage


class Taskmanger:
    task_name = 'TVicor10H'
    if AccManage.Device_ID == 'Mac':
        start_index = 0
        end_index = 100
    elif AccManage.Device_ID == '11':
        start_index = 125
        end_index = 250
    elif AccManage.Device_ID == 'sz':
        start_index = 250
        end_index = 375
    elif AccManage.Device_ID == '42':
        start_index = 375
        end_index = 500
    elif AccManage.Device_ID == '04':
        start_index = 0
        end_index = 100


class Task_IC_hot_F_manger:
    task_name = 'TVicor'
    base = 0
    if AccManage.Device_ID == 'Mac':
        start_index = base + 0
        end_index = base + 100
    elif AccManage.Device_ID == '11':
        start_index = base + 100
        end_index = base + 200
    elif AccManage.Device_ID == 'sz':
        start_index = base + 200
        end_index = base + 300
    elif AccManage.Device_ID == '04':
        start_index = base + 300
        end_index = base + 400
    elif AccManage.Device_ID == '42':
        start_index = base + 400
        end_index = base + 500


class Task_IC_hot_C_manger:
    task_name = 'TVicor'
    base = 500
    if AccManage.Device_ID == 'Mac':
        start_index = base + 0
        end_index = base + 100
    elif AccManage.Device_ID == '11':
        start_index = base + 100
        end_index = base + 200
    elif AccManage.Device_ID == 'sz':
        start_index = base + 200
        end_index = base + 300
    elif AccManage.Device_ID == '04':
        start_index = base + 300
        end_index = base + 400
    elif AccManage.Device_ID == '42':
        start_index = base + 400
        end_index = base + 500
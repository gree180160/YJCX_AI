from Manager import AccountMange


class Taskmanger:
    task_name = 'TRenesasAll_105H'
    if AccountMange.Device_ID == 'Mac':
        start_index = 0
        end_index = 125
    elif AccountMange.Device_ID == '11':
        start_index = 125
        end_index = 250
    elif AccountMange.Device_ID == 'sz':
        start_index = 250
        end_index = 375
    elif AccountMange.Device_ID == '04':
        start_index = 375
        end_index = 500
    elif AccountMange.Device_ID == '42':
        start_index = 400
        end_index = 500
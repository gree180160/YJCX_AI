from WRTools import ExcelHelp, WaitHelp, PathHelp, EmailHelper, StringHelp, MySqlHelp_recommanded
import os


def save_db():
    fold_path = '/Users/liuhe/Desktop/progress/TTender_info'
    file_name_list = os.listdir(fold_path)
    file_name_list.sort()
    for temp_file in file_name_list[7:]: # tender_info_2023-08-30_B finished
        saved_no = []
        if temp_file.__contains__('_A.xlsx'):
            file_content_arr = []
            sheet_content = ExcelHelp.read_sheet_content_by_name(f'{fold_path}/{temp_file}', 'Sheet')
            for (row_index, temp_row) in enumerate(sheet_content):
                if row_index > 0 and (not saved_no.__contains__(temp_row[1])):
                    row_value = temp_row[1:]
                    update_time = temp_file[12:22] + " 00:00:00"
                    row_value.append(update_time)
                    file_content_arr.append(row_value)
                    saved_no.append(temp_row[1])
            # print(file_content_arr)
            MySqlHelp.rts_render_A(file_content_arr)
        elif temp_file.__contains__('_B.xlsx'):
            file_content_arr = []
            sheet_content = ExcelHelp.read_sheet_content_by_name(f'{fold_path}/{temp_file}', 'Sheet')
            for (row_index, temp_row) in enumerate(sheet_content):
                if row_index > 0 and (not saved_no.__contains__(temp_row[1])):
                    row_value = temp_row[1:]
                    update_time = temp_file[12:22] + " 00:00:00"
                    row_value.append(update_time)
                    file_content_arr.append(row_value)
                    saved_no.append(temp_row[1])
            # print(file_content_arr)
            MySqlHelp.rts_render_B(file_content_arr)


def rosKeyword():
    keywordlist = ExcelHelp.read_col_content(PathHelp.get_file_path('B2B', 'Task.xlsx'), 'keywordAll', 1)
    ros_file = ExcelHelp.read_sheet_content_by_name(PathHelp.get_file_path('B2B', 'ros.xlsx'), 'ros')
    result = []
    for temp_keyword in keywordlist:
        for row_content in ros_file:
            if row_content[0].__contains__(temp_keyword) or row_content[8].__contains__(temp_keyword) or row_content[-1].__contains__(temp_keyword):
                new_value = [temp_keyword] + row_content
                result.append(new_value)
    ExcelHelp.add_arr_to_sheet(PathHelp.get_file_path('B2B', 'ros.xlsx'), 'keyword_sum', result)


if __name__ == "__main__":
    rosKeyword()
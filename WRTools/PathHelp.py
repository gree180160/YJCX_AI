from sys import platform
import os
import sys
from Manager import TaskManager
from WRTools import ExcelHelp


def get_file_path(super_path, file_name) -> str:
    result = root_path = getRootPath()
    if platform.startswith('linux'):
        tail = ''
    elif platform.startswith('win'):
        tail = f'\\{super_path}\\{file_name}' if super_path else f'\\{file_name}'
    else:
        tail = f'/{super_path}/{file_name}' if super_path else f'/{file_name}'
    result = root_path + tail
    return result


def get_IC_hot_image_fold(task_name):
    image_fold = getRootPath() + f"/{task_name}" + "/IC_hot_images"
    return image_fold


# 获得根路径
def getRootPath():
    # 获取文件目录
    curPath = os.path.abspath(os.path.dirname(__file__))
    # 获取项目根路径，内容为当前项目的名字
    if platform.startswith('linux'):
        tail = ''
    elif platform.startswith('win'):
        tail = rootPath = curPath[:curPath.find('YJCX_AI') + len('YJCX_AI')]
    else:
        tail = rootPath = curPath[:curPath.find('YJCX_AI') + len('YJCX_AI')]
    return rootPath


# 从根目录下开始获取其他路径
def getOtherPath(abspath:str):
    # 调用了上述获得项目根目录的方法
    rootPath = getRootPath()
    dataPath = os.path.abspath(rootPath + '/' + abspath)
    return dataPath


def get_chrome_path():

    return ''


def get_firfox_path():
    return ''


# 获得路径，当前文件所在路径
def resource_path(relative_path):
    # 是否Bundle Resource
    if getattr(sys, 'frozen', False):
        # running in a bundle
        base_path = sys._MEIPASS
        print('true',base_path)
    else:
        # running live
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def change_screenShotName(fold_path):
    pn_file = get_file_path(TaskManager.Taskmanger().task_name, 'Task.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=1)[TaskManager.Taskmanger().start_index: TaskManager.Taskmanger().end_index]
    file_name_list = os.listdir(fold_path)
    valid_files = []
    for (index, temp) in enumerate(file_name_list):
        if temp.startswith("火狐截图_"):
            valid_files.append(temp)
    valid_files.sort()
    print(valid_files)
    for (index, temp) in enumerate(valid_files):
        print(temp)
        if True:
            is_week_data = index < ppn_list.__len__()
            print(ppn_list[index % ppn_list.__len__()])
            right_ppn = ppn_list[index % ppn_list.__len__()].replace('/', '%2F')
            imageName_new = right_ppn + ('_W' if is_week_data else '_M') + '.png'
            os.rename(fold_path + '/' + temp, fold_path + '/' + imageName_new)


if __name__ == "__main__":
    # keyword_source_file = get_file_path(super_path=None, file_name='Tkeyword.xlsx')
    # log_file = get_file_path(super_path='Octopart_category', file_name='octopart_key_cate_log.txt')
    # print(keyword_source_file)
    # print(log_file)-
    # print(getOtherPath('TRenesasAll_10H'))
    change_screenShotName(fold_path=get_file_path('IC_Search', 'temp_hot_images'))


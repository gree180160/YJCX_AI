from sys import platform
import os
import sys
from WRTools import ExcelHelp
from pathlib import Path


def get_file_path(super_path: str | None, file_name: str) -> str:
    root_path = getRootPath()
    parts = [root_path]
    if super_path:
        parts.append(super_path)
    parts.append(file_name)
    return os.path.join(*parts)


def get_IC_hot_image_fold(task_name):
    image_fold = getRootPath() + f"/{task_name}" + "/IC_hot_images"
    return image_fold


def getRootPath() -> str:
    # 项目根目录 = ChipCrawler 目录(本文件位于 ChipCrawler/WRTools/PathHelp.py,向上两级)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    return str(project_root)


# 从根目录下开始获取其他路径
def getOtherPath(abspath:str):
    # 调用了上述获得项目根目录的方法
    rootPath = getRootPath()
    dataPath = os.path.abspath(rootPath + '/' + abspath)
    return dataPath


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


def change_screenShotName_Firfox(fold_path):
    pn_file = get_file_path(None, f'00.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=1)[0,0]
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


def change_screenShotName_Chrome(fold_path):
    pn_file = get_file_path('0', 'Task.xlsx')
    ppn_list = ExcelHelp.read_col_content(file_name=pn_file, sheet_name='ppn', col_index=1)[0: 0]
    file_name_list = os.listdir(fold_path)
    valid_files = []
    for (index, temp) in enumerate(file_name_list):
        if temp.startswith("Screenshot_"):
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
    keyword_source_file = get_file_path(super_path=None, file_name='TADIPMICBatteryManagement.xlsx')
    # log_file = get_file_path(super_path='Octopart_category', file_name='octopart_key_cate_log.txt')
    print(keyword_source_file)
    # print(log_file)-
    # print(getOtherPath('TRenesasAll_10H'))
    # change_screenShotName_Firfox(fold_path=get_file_path('IC_Search', 'temp_hot_images'))
    # change_screenShotName_Chrome(fold_path=get_file_path('IC_Search', 'temp_hot_images'))


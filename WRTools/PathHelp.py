from sys import platform
import os
import sys


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
    rootPath = curPath[:curPath.find('YJCX_AI') + len('YJCX_AI')]
    return rootPath


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


if __name__ == "__main__":
    # keyword_source_file = get_file_path(super_path=None, file_name='TKeywords.xlsx')
    # log_file = get_file_path(super_path='Octopart_category', file_name='octopart_key_cate_log.txt')
    # print(keyword_source_file)
    # print(log_file)-
    print(getOtherPath('TRenesasAll_10H'))



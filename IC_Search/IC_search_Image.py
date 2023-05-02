# IC 搜索量图片处理
import os
import time

from PIL import Image, ImageGrab
from WRTools import ChracterReconition, ExcelHelp, PathHelp

# AUIRF1404ZS   AUIRF1405   AUIRF1405ZL， AUIRF2804S
# （推荐ppn过多，看
# 根据图片高度，<1000，说明没有数据），1700-1800， 月指数，3000-35000，周指数
def rule_image_names(fold_path):
    source_file = PathHelp.get_file_path("TInfenion_55H", 'TInfenion_55H.xlsx')
    source_ppn_list = ExcelHelp.read_col_content(file_name=source_file, sheet_name='ppn', col_index=1)[37:73]
    check_ppn_list = []
    for temp in source_ppn_list:
        if temp:
            check_ppn_list.append(ppn_checkChange(temp))
    file_name_list = os.listdir(fold_path)
    file_name_list.sort()
    unmatch_image = []
    for temp in file_name_list:
        if temp.endswith('.png'):
            file_path = fold_path + '/' + temp
            rec_ppn = ChracterReconition.get_ppn(fold_path=fold_path, image_name=file_path)
            rec_ppn = rec_ppn.replace('.', '')
            rec_ppn = rec_ppn.strip()
            if rec_ppn in source_ppn_list:
                is_week_data = is_week_search(file_path)
                imageName_new = rec_ppn + ('__W' if is_week_data else '__M') + '.png'
                os.rename(fold_path + '/' + temp, fold_path + '/' + imageName_new)
                # print(f'  match---- file : {temp} , ppn: {ppn}')
            else:
                check_changedppn = ppn_checkChange(rec_ppn)
                if check_changedppn in check_ppn_list and check_ppn_list.count(check_changedppn) == 1:
                    is_week_data = is_week_search(file_path)
                    check_right_index = check_ppn_list.index(check_changedppn)
                    imageName_new = source_ppn_list[check_right_index] + ('__W' if is_week_data else '__M') + '.png'
                    os.rename(fold_path + '/' + temp, fold_path + '/' + imageName_new)
                    # print(f'  changed match---- file : {temp} , ppn: {ppn}')
                else:
                    unmatch_image.append([rec_ppn, temp])
                    print(f'unmatch---- file : {temp} , ppn: {check_changedppn}')


# 是否是周指数
def is_week_search(image_name):
    # 打开一张图
    img = Image.open(image_name)
    # 图片尺寸
    img_size = img.size
    h = img_size[1]  # 图片高度
    w = img_size[0]  # 图片高度
    if w > 2800:
        scale = 2
    else:
        scale = 1
    if h > 2500*scale:
        return True
    return False


# 为ppn 的模糊匹配，进行变换
def ppn_checkChange(ppn: str):
    result = ppn.upper()
    result = result.replace('0', 'O')
    # result = result.replace('0', 'Q')
    result = result.replace('1', 'L')
    # result = result.replace('1', 'I')
    # result = result.replace('1', 'T')

    result = result.replace('2', 'Z')
    result = result.replace('3', 'S')
    result = result.replace('4', 'A')
    result = result.replace('5', 'S')
    # result = result.replace('6', '8')
    result = result.replace('6', 'G')
    # result = result.replace('6', 'E')
    # result = result.replace('6', '0')
    # result = result.replace('7', 'Z')
    # result = result.replace('7', 'T')
    result = result.replace('7', 'L')
    #result = result.replace('8', 'E')
    result = result.replace('8', 'B')
    #result = result.replace('8', 'S')
    # result = result.replace('9', 'S')
    result = result.replace('9', 'O')
    #result = result.replace('9', 'I')
    #result = result.replace('I', 'L')
    result = result.replace('V', 'U')
    result = result.replace('I', 'J')
    result = result.replace(')', 'J')
    result = result.replace('[', 'I')
    result = result.replace('-IR', '-TR')
    # result = result.replace('£', 'E')
    return result


# 修改图片名称错误的情况
def change_error_image_name(fold_path):
    file_name_list = os.listdir(fold_path)
    file_name_list.sort()
    T55H_ppn = ExcelHelp.read_col_content(file_name='/Users/liuhe/Desktop/progress/TInfineon/55H/TInfenion_55H.xlsx', sheet_name='ppn', col_index=1)
    TNV_ppn = ExcelHelp.read_col_content(file_name=PathHelp.get_file_path('TSumNvmNdt', 'Task.xlsx'), sheet_name='ppn', col_index=1)
    for temp in file_name_list:
        if temp.endswith('.png'):
            error_ppn = temp[0:-6]
            right_index = T55H_ppn.index(error_ppn)
            new_ppn = TNV_ppn[right_index]
            if temp.endswith('_M.png'):
                imageName_new = new_ppn + "_M.png"
                os.rename(fold_path + '/' + temp, fold_path + '/' + imageName_new)
            elif temp.endswith('_W.png'):
                imageName_new = new_ppn + "_W.png"
                os.rename(fold_path + '/' + temp, fold_path + '/' + imageName_new)


#  删除没有热度数据的图片
def filert_useless_image(fold_path):
    file_name_list = os.listdir(fold_path)
    for (index, temp) in enumerate(file_name_list):
        if temp.endswith('.png'):
            # 打开一张图
            img = Image.open(fold_path + '/' + temp)
            # 图片尺寸
            img_size = img.size
            h = img_size[1]  # 图片高度
            w = img_size[0]  # 图片高度
            if h/w < 0.63:
                os.remove(fold_path + '/' + temp)


# 识别IC——hot 图片里的热度信息并保存到数据库
def rec_image(fold_path):
    filert_useless_image(fold_path)
    source_file = PathHelp.get_file_path('TSkyworksP1', 'Task.xlsx')
    file_name_list = os.listdir(fold_path)
    file_name_list.sort()
    print(f"file count is: {file_name_list.__len__()}")
    for (index, temp) in enumerate(file_name_list):
        if index in range(0, 10000):
            print(f"index is:{index} , image is: {temp}")
            ppn = temp[0:-6]
            ppn = ppn.replace('%2F', '/')
            if temp.endswith('_M.png'):
                image_hot_data = ChracterReconition.SplitPic_month(fold_path + '/' + temp)
                image_hot_data.insert(0, ppn)
                ExcelHelp.add_arr_to_sheet(file_name=source_file, sheet_name='IC_hot_month', dim_arr=[image_hot_data])
            elif temp.endswith('_W.png'):
                image_hot_data = ChracterReconition.SplitPic_week(fold_path + '/' + temp)
                image_hot_data.insert(0, ppn)
                ExcelHelp.add_arr_to_sheet(file_name=source_file, sheet_name='IC_hot_week', dim_arr=[image_hot_data])


if __name__ == "__main__":
    rec_image(fold_path='/Users/liuhe/Desktop/progress/TSkyworks/discontiue/TSkyworksP1/04/IC_hot_images')
    time.sleep(2.0)
    rec_image(fold_path='/Users/liuhe/Desktop/progress/TSkyworks/discontiue/TSkyworksP1/11/IC_hot_images')
    time.sleep(2.0)
    rec_image(fold_path='/Users/liuhe/Desktop/progress/TSkyworks/discontiue/TSkyworksP1/sz/IC_hot_images')
    time.sleep(2.0)
    rec_image(fold_path=PathHelp.get_IC_hot_image_fold('TSkyworksP1'))



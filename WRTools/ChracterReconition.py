# 图片识别
from PIL import Image, ImageGrab
from _cffi_backend import string
from pytesseract import *
import cv2
from io import BytesIO
import re
import os
from WRTools import LogHelper, PathHelp, DDDDOCR

corp_path = PathHelp.get_file_path('IC_Search', 'CroppedImages')


# 是否是mac 高清图
def get_image_scale(image_name):
    # 打开一张图
    img = Image.open(image_name)
    # 图片尺寸
    img_size = img.size
    w = img_size[0]  # 图片宽度
    if w > 2800:
        return 2
    return 1


def SplitPic_week(source_pic: str):
    scale = get_image_scale(source_pic)
    # 打开一张图
    img = Image.open(source_pic)
    # 图片尺寸
    img_size = img.size
    wid = img_size[0]  # 图片宽度
    hei = img_size[1]  # 图片高度
    # mac
    if True:
        x = wid / 2 - 216 * scale
        y = (988 * scale) if hei > (3160.0 * scale) else (980 * scale)
        w = 116 * scale
        h = 30 * scale
        space = 36 * scale
    else:
        x = wid / 2 - 216 * scale + 20 * scale
        y = (988 * scale) if hei > (3160.0 * scale) else ((980-99) * scale)
        w = 116 * scale
        h = 30 * scale
        space = 32.55 * scale
    search_record = []
    for index in range(0, 52):
        # 开始截取
        region = img.crop((x, y+space*index, x + w, y+space*index + h))
        # 保存图片
        region.save(f'{corp_path}/w_{index+1}.png')
        reco_value = DDDDOCR.reco(f'{corp_path}/w_{index + 1}.png')
        search_record.append(reco_value)
    return search_record


def SplitPic_month(source_pic: str):
    # 打开一张图
    scale = get_image_scale(source_pic)
    img = Image.open(source_pic)
    # 图片尺寸
    img_size = img.size
    wid = img_size[0]  # 图片宽度
    hei = img_size[1]  # 图片高度
    if True:
        x = wid / 2 - 216 * scale
        y = (988 * scale) if hei > (1720.0 * scale) else (980 * scale)
        w = 116 * scale
        h = 30 * scale
        space = 36 * scale
    else:
        x = wid / 2 - 216 * scale + 20 * scale
        y = (988 * scale) if hei > (1720.0 * scale) else (980 - 99)
        w = 116 * scale
        h = 29 * scale
        space = 32.55 * scale
    search_record = []
    for index in range(0, 12):

        # 开始截取
        region = img.crop((x, y+space*index, x + w, y+space*index + h))
        # 保存图片
        region.save(f'{corp_path}/M_{index+1}.png')
        rec_value = DDDDOCR.reco(f'{corp_path}/M_{index+1}.png')
        search_record.append(rec_value)
    return search_record


def test_hot_value(fold_path: str):
     # temp = 'R5F10BGELFB#H5_M.png' # 1911×1724
    temp = 'R5F10RLCAFB#30_M.png' # 1911×3164
    if temp.endswith('_M.png'):
        image_hot_data = SplitPic_month(fold_path + '/' + temp)
    elif temp.endswith('_W.png'):
        image_hot_data = SplitPic_week(fold_path + '/' + temp)
    return image_hot_data


if __name__ == "__main__":
    result = test_hot_value(fold_path='/Users/liuhe/Desktop/progress/TRenesas_MCU/Renesas_MCU_115H/04/IC_hot_images')
    print(result)
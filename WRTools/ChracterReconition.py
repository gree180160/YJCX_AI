# 图片识别
from PIL import Image, ImageGrab
from _cffi_backend import string
from pytesseract import *
import cv2
from io import BytesIO
import re
import os
from WRTools import LogHelper, PathHelp



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


# 获取ppn_name
def get_ppn(fold_path, image_name):
    scale = get_image_scale(image_name)
    # 打开一张图
    page_image = Image.open(image_name)
    # 图片尺寸
    img_size = page_image.size
    # 图片中间有效，两边的空白部分是无效的，所以从图片中间开始，计算x
    wid = img_size[0]
    w = 343*scale
    x = wid/2 - 98.6*scale - 343*scale
    y = 252*scale
    h = 30*scale
    # 04
    # w = 343*scale
    # x = wid/2 - 68*scale - 343*scale
    # y = 222*scale
    # # y = 222 * scale # TODO wr for 04
    # h = 30*scale

    # 开始截取
    ppn_area = page_image.crop((x, y, x+w, y+h))
    ppn_area.save(fold_path + '/ppn_name.png')

    # 1.原始
    threshold = 127  # to be determined
    ppn_image = cv2.imread(fold_path + '/ppn_name.png', 1)
    _, img_binarized = cv2.threshold(ppn_image, threshold, 255, cv2.THRESH_BINARY_INV)
    pil_img = Image.fromarray(img_binarized)
    # pil_img.show()
    try:
        config = '--psm 6'
        reco_result = pytesseract.image_to_string(pil_img, lang='eng', config=config)
        if ': ' in reco_result:
            index = reco_result.index(': ')
            result_str = reco_result[index+2:]
        elif 'WS:' in reco_result:
            index = reco_result.index('WS:')
            result_str = reco_result[index + 3:]
        result_str = result_str.replace('\n', '')
    except:
        result_str = "--"
    return result_str


# 获取图片文字,return hot value arr
def getHotValue(sourceImage, row_image_name, index):
    img = cv2.imread(row_image_name, 1)
    # 1.原始
    threshold = 180  # to be determined
    # _, img_binarized = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    min_value = 127
    # THRESH_BINARY_INV 4 ok, 51 bad
    _, img_binarized = cv2.threshold(gray, min_value, 255, cv2.THRESH_BINARY_INV)
    pil_img = Image.fromarray(img_binarized)
    config = '--psm 6 digitsdot'
    #1
    try:
        result_str1 = pytesseract.image_to_string(pil_img, lang='eng', config=config)
        result_str1 = result_str1.replace(",", '')
        int1 = int(result_str1)
    except:
        result_str1 = ""
        int1 = 0
    # 2
    _, img_binarized2 = cv2.threshold(gray, min_value, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    pil_img2 = Image.fromarray(img_binarized2)
    try:
        result_str2 = pytesseract.image_to_string(pil_img2, lang='eng', config=config)
        result_str2 = result_str2.replace(",", '')
        int2 = int(result_str2)
    except:
        result_str2 = ""
        int2 = 0
    # 3
    _, img_binarized3 = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    pil_img3 = Image.fromarray(img_binarized3)
    try:
        result_str3 = pytesseract.image_to_string(pil_img3, lang='eng', config=config)
        result_str3 = result_str3.replace(",", '')
        int3 = int(result_str3)
    except:
        result_str3 = ""
        int3 = 0
    # 4
    _, img_binarized4 = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    pil_img2 = Image.fromarray(img_binarized4)
    try:
        result_str4 = pytesseract.image_to_string(pil_img2, lang='eng', config=config)
        result_str4 = result_str4.replace(",", '')
        int4 = int(result_str4)
    except:
        result_str4 = ""
        int4 = 0
    des_str = sourceImage + "  " + str(index) + 'th---  ' + "1: " + result_str1 + "2: " + result_str2 + "3: " + result_str3 + "4: " + result_str4
    # print(f'结果{index + 1}:  {des_str}')
    may_result = [int1, int2, int3, int4]
    may_result.sort()
    search_num = ''
    if may_result[2] > 0 and may_result[3] > 0:
        if may_result[2] != may_result[3] and str(may_result[2]).__len__() == str(may_result[3]).__len__():
            search_num = f'{may_result[2]} ? {may_result[3]}'
            log_file = PathHelp.get_file_path(super_path='IC_Search', file_name='IC_search_Image_log.txt')
            LogHelper.write_log(log_file, des_str)
        else:
            search_num = str(may_result[0])
    else:
        search_num = str(may_result[0])
    return search_num


def SplitPic_week(source_pic: str):
    scale = get_image_scale(source_pic)
    # 打开一张图
    img = Image.open(source_pic)
    # 图片尺寸
    img_size = img.size
    wid = img_size[0]  # 图片宽度
    hei = img_size[1]  # 图片高度
    # mac
    if hei < 3200:
        # wid ，标准1312， x 440
        x = wid/2 - 100 - 116
        y = 982 * scale
        w = 116 * scale
        h = 30 * scale
        space = 36 * scale
    else:
        x = 533 * scale
        y = 978 * scale
        w = 116 * scale
        h = 30 * scale
        space = 36 * scale
    # #11&SZ-02
    # x = wid / 2 - 100 - 116
    # y = 978 * scale
    # w = 116 * scale
    # h = 30 * scale
    # space = 36 * scale
    # 04
    # x = wid / 2 - 80 - 116
    # y = 890 * scale - (2852*scale - hei)
    # w = 116 * scale
    # h = 26.5 * scale
    # space = 32.5 * scale
    # after 0215
    # x = wid / 2 - 100 - 116
    # y = 978 * scale
    # w = 116 * scale
    # h = 30 * scale
    # space = 36 * scale
    search_record = []
    for index in range(0, 52):
        # 开始截取
        region = img.crop((x, y+space*index, x + w, y+space*index + h))
        # 保存图片
        region.save(f'/Users/liuhe/Desktop/识图test/w_{index+1}.png')
        reco_value = getHotValue(sourceImage=source_pic, row_image_name=f'/Users/liuhe/Desktop/识图test/w_{index+1}.png', index=index)
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
    # mac 高清
    if 3400 <= hei:
        x = 532.735 * scale
        y = 982 * scale
        w = 116 * scale
        h = 30 * scale
        space = 36 * scale
    elif 1730 <= hei <= 3400:
        x = 420.9
        y = 979.7
        w = 116 * scale
        h = 30 * scale
        space = 36 * scale
    else:
        x = wid / 2 - 100 - 116
        y = 981.446 * scale
        w = 116 * scale
        h = 30 * scale
        space = 36 * scale
    # 11-01,sz
    # x = wid/2 - 100.00 - 116
    # y = 978 * scale
    # w = 116 * scale
    # h = 30 * scale
    # space = 36 * scale

    # 04
    # x = wid/2 - 200*scale
    # y = 889.2 * scale - (1553*scale - hei)
    # w = 116 * scale
    # h = 26.5 * scale
    # space = 32.5 * scale
    # after 0215
    # x = wid/2 - 100.00 - 116
    # y = 980 * scale
    # w = 116 * scale
    # h = 30 * scale
    # space = 36 * scale
    search_record = []
    for index in range(0, 12):
        # 开始截取
        region = img.crop((x, y+space*index, x + w, y+space*index + h))
        # 保存图片
        region.save(f'/Users/liuhe/Desktop/识图test/M_{index+1}.png')
        rec_value = getHotValue(sourceImage=source_pic, row_image_name=f'/Users/liuhe/Desktop/识图test/M_{index+1}.png', index=index)
        search_record.append(rec_value)
    return search_record


def test_ppn_value(fold_path: str):
    temp = '火狐截图_2023-02-11T07-17-21.748Z.png'
    # temp = 'TLE493DW2B6A0HTSA1_M.png'
    return get_ppn(fold_path=fold_path, image_name=fold_path + '/' + temp)


def test_hot_value(fold_path: str):
    temp = 'CY7C1312KV18-250BZI_M.png' # 1911×1724
    #temp = 'CY7C1312KV18-250BZI_W.png' # 1911×3164
    if temp.endswith('_M.png'):
        image_hot_data = SplitPic_month(fold_path + '/' + temp)
    elif temp.endswith('_W.png'):
        image_hot_data = SplitPic_week(fold_path + '/' + temp)
    return image_hot_data


if __name__ == "__main__":
    # result = test_ppn_value(fold_path='/Users/liuhe/Desktop/progress/TSemiStar/IC_hot/TInfineionAgencyStock2_SemiStart_IC_hot')
    # useFold('/Users/liuhe/Desktop/hot_img')
    # print(result_str)
    # SplitPic('/Users/liuhe/Desktop/识图test/88.png')
    result = test_hot_value(fold_path='/Users/liuhe/Desktop/progress/TInfineon/10H/hot_images/mac')
    print(result)
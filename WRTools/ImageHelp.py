import base64
from WRTools import PathHelp, DDDDOCR
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, UnidentifiedImageError
import os
import cv2
import numpy as np


def canvasToImage_color(canvas_base64, path, bgColor):
    # 将Base64数据解码为图像

    image_data = base64.b64decode(canvas_base64)
    image = Image.open(BytesIO(image_data))
    image = image.convert("RGBA")
    if bgColor:
        new_image = Image.new("RGBA", (int(image.width + 10), int(image.height + 2)), bgColor)
        new_image.paste(image, (5, 1), image)
        # 保存图像为.png文件
        new_image.save(path)
    else:
        image.save(path)


def canvasToImage_1(canvas_base64, path):
    # 将Base64数据解码为图像
    image_data = base64.b64decode(canvas_base64)
    image = Image.open(BytesIO(image_data))
    # image = image.convert("1")
    new_image = Image.new("1", (int(image.width + 10), int(image.height + 2)))
    new_image.paste(image, (5, 1), image)
    new_image.save(path)


def canvasToImage_l(canvas_base64, path):
    # 将Base64数据解码为图像
    image_data = base64.b64decode(canvas_base64)
    image = Image.open(BytesIO(image_data))
    # image = image.convert("L")
    new_image = Image.new("F", (int(image.width + 10), int(image.height + 2)))
    new_image.paste(image, (5, 1), image)
    new_image.save(path)


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode('utf-8')


def adjust_image():
    path0 = PathHelp.get_file_path('IC_Search', 'ca.png')
    ba64 = image_to_base64(path0)

    path1 = PathHelp.get_file_path('IC_Search', 'ca1.png')
    canvasToImage_color(ba64, path1, '#66ffff')
    result1 = DDDDOCR.reco(path1)

    path2 = PathHelp.get_file_path('IC_Search', 'ca2.png')
    canvasToImage_1(ba64, path2)
    result2 = DDDDOCR.reco(path2)

    path3 = PathHelp.get_file_path('IC_Search', 'ca3.png')
    canvasToImage_1(ba64, path3)
    result3 = DDDDOCR.reco(path3)

    print(f'{result1} ; {result2} ; {result3}')


def water_mark():
    # 设置水印文字和字体
    text = "   深圳市风菱电子有限责任公司   "
    font_path = "/Library/Fonts/AlibabaHealthFont2.0CN-85B.ttf"  # 修改为系统自带的字体路径
    font_size = 12  # 设置字号
    text_color = (73, 160, 45, 30)
    font = ImageFont.truetype(font_path, font_size)

    # 遍历文件夹里的所有图片
    folder_path = "/Users/liuhe/Desktop/产品照片/私印/"
    for filename in os.listdir(folder_path):
        if filename.endswith(".HEIC") or filename.endswith(".png") or filename.endswith(".jpeg"):
            image_path = os.path.join(folder_path, filename)
            # once_add_mark(image_path, text, text_color, font)
            add_watermark_repeat(image_path, text, text_color)
    print("水印添加完成！")


# 1. 添加水印，只加一次
def once_add_mark(image_path, text, color, font):
    # 打开图片
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    draw.text((120, 220), text, fill=color, font=font)
    img.save(image_path)


def add_watermark_repeat(image_path, text, text_color):
    # 打开原始图片
    try:
        original = Image.open(image_path).convert("RGBA")
        original.show()
    except UnidentifiedImageError:
        print("Error: The image file could not be identified. Please check the file format and path.")
    except FileNotFoundError:
        print("Error: The file was not found. Please check the file path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    width, height = original.size

    # 创建透明背景的水印图片
    watermark = Image.new("RGBA", original.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)

    # 设置水印字体和大小
    font_size = int(min(width, height) / 40)
    font_path = "/Library/Fonts/AlibabaHealthFont2.0CN-85B.ttf"
    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = draw.textsize(text, font)

    # 创建倾斜45度的水印
    angle = 45
    rotated_text = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    draw_rotated = ImageDraw.Draw(rotated_text)
    draw_rotated.text((0, 0), text, font=font, fill=(73, 160, 45, 80))
    rotated_text = rotated_text.rotate(angle, expand=1)
    # 计算重复水印的数量
    repeat_x = int(np.ceil(width / rotated_text.width)) + 1
    repeat_y = int(np.ceil(height / rotated_text.height)) + 1

    # 在水印图像上重复水印
    for i in range(repeat_x):
        for j in range(repeat_y):
            watermark.paste(rotated_text, (i * rotated_text.width, j * rotated_text.height), rotated_text)

    # 合并水印和原始图像
    watermark = ImageEnhance.Brightness(watermark).enhance(0.5)  # 调整透明度
    combined = Image.alpha_composite(original, watermark)

    # 保存合并后的图像
    combined = combined.convert("RGB")  # 转换为RGB模式以保存为JPEG
    combined.save(image_path, "JPEG")

def remove_black():
    # 读取图像
    image = cv2.imread('/Users/liuhe/PycharmProjects/YJCX_AI/WRTools/zz.png')

    # 获取图像的高度和宽度
    height, width, channels = image.shape

    # 遍历每个像素
    for i in range(height):
        for j in range(width):
            # 获取当前像素的RGB值
            b, g, r = image[i, j]

            # 检查是否是相同的RGB值
            if b == g == r:  # 如果RGB三个值相同
                # 将该颜色点设置为纯白色
                image[i, j] = [255, 255, 255]  # OpenCV中顺序是BGR

    # 确保背景是白色
    # 将所有接近白色的背景（，例如 RGB < 255 - tolerance）也设为白色
    tolerance = 10  # 可调容差
    for i in range(height):
        for j in range(width):
            b, g, r = image[i, j]
            avg = (b + g + r) / 3
            if (abs(avg - b) <= 20) and (abs(avg - g) <= 20) and (abs(avg - r) <= 20):
                # 将该颜色点设置为纯白色
                image[i, j] = [255, 255, 255]  # OpenCV中顺序是BGR
            if r < 200:
                image[i, j] = [255, 255, 255]

                # 保存处理后的图像
    cv2.imwrite('output_image.png', image)

    # 显示处理结果
    cv2.imshow('Processed Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    water_mark()

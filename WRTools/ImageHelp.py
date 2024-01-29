import base64
from WRTools import PathHelp, DDDDOCR
from PIL import Image, ImageDraw, ImageFont
import os


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
    text = "Kyent Industrial"
    font_path = "/Library/Fonts/Times New Roman.ttf"  # 修改为系统自带的字体路径
    font_size = 24  # 设置字号
    font = ImageFont.truetype(font_path, font_size)

    # 遍历文件夹里的所有图片
    folder_path = "/Users/liuhe/Desktop/宝塔/kyent/images/product/product/"
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            # 打开图片
            image_path = os.path.join(folder_path, filename)
            img = Image.open(image_path)

            # 添加水印
            draw = ImageDraw.Draw(img)
            draw.text((120, 220), text, fill="white", font=font)

            # 保存图片
            img.save(os.path.join(folder_path, f"{filename}"))
    print("水印添加完成！")


if __name__ == "__main__":
    # canvasToImage_color()
    water_mark()

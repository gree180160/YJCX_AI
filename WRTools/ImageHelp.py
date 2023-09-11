import base64
from WRTools import PathHelp, DDDDOCR
from PIL import Image
from io import BytesIO


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


if __name__ == "__main__":
    # canvasToImage_color()
    adjust_image()

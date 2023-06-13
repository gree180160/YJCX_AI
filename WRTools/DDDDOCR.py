import ddddocr
import re
from WRTools import LogHelper, PathHelp

ocr = ddddocr.DdddOcr(show_ad=False)


def reco(source_image) -> int:
    try:
        with open(source_image, 'rb') as f:
            img_bytes = f.read()
        ocr_result = ocr.classification(img_bytes)
        ocr_result = re.sub('[^0-9]', '', ocr_result)
        ocr_result = ocr_result.replace('o', '0' )
        ocr_result = ocr_result.replace('O', '0')
        if ocr_result.__len__() > 0:
            ocr_result = int(ocr_result)
        else:
            # print(ocr_result)
            ocr_result = 0
    except Exception as e:
        LogHelper.write_log(PathHelp.get_file_path('WRTools', 'DDOCRLog.txt'), e)
        ocr_result = 0
    return ocr_result


def test():
    for i in range(1, 12):
        with open(f'/Users/liuhe/PycharmProjects/YJCX_AI/IC_Search/CroppedImages/M_{i}.png', 'rb') as f:
            img_bytes = f.read()
        result = ocr.classification(img_bytes)
        print(result)


if __name__ == "__main__":
    a = reco("/Users/liuhe/PycharmProjects/YJCX_AI/IC_Search/CroppedImages/M_1.png")



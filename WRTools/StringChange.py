import requests
from WRTools import ExcelHelp
import time


# zh -> english
def translateZh_En(chineseSource):
    if chineseSource:
        if chineseSource.__len__() > 0:
            return requests.post("https://hf.space/embed/mikeee/gradio-gtr/+/api/predict", json={"data": [chineseSource, "zh", "en"]}).json()[
        "data"][0]
    else:
        return ''
 
    
# ru -> zh
def translateRu_Zh(ruSource):
    if ruSource:
        if ruSource.__len__() > 0:
            zhStr = requests.post("https://hf.space/embed/mikeee/gradio-gtr/+/api/predict", json={"data": [ruSource, "ru", "zh"]}).json()[
        "data"][0]
    else:
        return ''
    print(zhStr)
    return zhStr


def trans_des():
    source_file = '/Users/liuhe/Desktop/TJDMC.xlsx'
    sheetContent = ExcelHelp.read_sheet_content_by_name(file_name=source_file, sheet_name='ppn')
    for (row_index, tempRow) in enumerate(sheetContent):
        print(row_index)
       

if __name__ == "__main__":
    # translateRu_Zh('ДОВЕРЯЕТ ГОСУДАРСТВО')
    translateZh_En('你好')
import requests
from WRTools import ExcelHelp
import time

# zh -> english
def translate(chineseSource):
    if chineseSource:
        if chineseSource.__len__() > 0:
            return requests.post("https://hf.space/embed/mikeee/gradio-gtr/+/api/predict", json={"data": [chineseSource, "zh", "en"]}).json()[
        "data"][0]
    else:
        return ''


def trans_des():
    source_file = '/Users/liuhe/Desktop/TJDMC.xlsx'
    sheetContent = ExcelHelp.read_sheet_content_by_name(file_name=source_file, sheet_name='ppn')
    for (row_index, tempRow) in enumerate(sheetContent):
        print(row_index)
        if tempRow and row_index >=235:
            chinese_des = tempRow[4]
            english_des = translate(chinese_des)
            ExcelHelp.write_cell(file_name=source_file, sheet_name='ppn', row=row_index+1, col=6, value=english_des)

            chinese_tec = tempRow[6]
            if chinese_tec.startswith('订货号'):
                ExcelHelp.write_cell(file_name=source_file, sheet_name='ppn', row=row_index + 1, col=7,
                                     value='')
                # ExcelHelp.write_cell(file_name=source_file, sheet_name='ppn', row=row_index + 1, col=8,
                #                      value='')
            # else:
            #     english_tec = translate(chinese_tec)
            #     ExcelHelp.write_cell(file_name=source_file, sheet_name='ppn', row=row_index + 1, col=8,
            #                      value=english_tec)



if __name__ == "__main__":
    trans_des()
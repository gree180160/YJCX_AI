from WRTools import PathHelp, ExcelHelp, StringHelp


# ['6', '订货号：HDR-100-24', '台', '明纬 超薄导轨电源,48台/箱；HDR-100-24', 'None', '起订量： 1台批量：1台', '188.79', '¥119.00/台', '删除']
def formBomToExcel():
    source_file = PathHelp.get_file_path(None, 'TICHot.xlsx')
    sheet_content = ExcelHelp.read_sheet_content_by_name(source_file, 'jdmc0')
    result = []
    for (index, content) in enumerate(sheet_content):
        if index % 2 == 0:
            one_content = [str(content[1]).replace('订货号：', ''),str(content[5]), StringHelp.strToPrice(str(content[7]))]
            result.append(one_content)
    ExcelHelp.add_arr_to_sheet(source_file, 'jdmc', result)


if __name__ == "__main__":
    formBomToExcel()
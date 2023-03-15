# 计算cate
# 输入型号，爬取现货排名和ICCP和SSCP的库存数据，输出两个字段：
# （1） 靠谱供应商数量（ICCP+SSCP）
# （2） 靠谱库存数量（[现货排名库存总量+非现货排名ICCP库存总量+非现货排名SSCP库存总量]/6)

from openpyxl import workbook, load_workbook, Workbook
import base64
import IC_stock.IC_Stock_Info
import time
from WRTools import PathHelp, ExcelHelp


cate_source_file = PathHelp.get_file_path("TInfenion_55H", 'Task.xlsx')
result_save_file = cate_source_file
ICStock_file_arr = ['/Users/liuhe/Desktop/progress/TInfineon/55H/11/IC_stock.xlsx',
                '/Users/liuhe/Desktop/progress/TInfineon/55H/04/IC_stock.xlsx',
                '/Users/liuhe/Desktop/progress/TInfineon/55H/sz/IC_stock.xlsx',
                '/Users/liuhe/PycharmProjects/SeleniumDemo/TInfenion_55H/IC_stock.xlsx']




# 根据file_index, sheet_index 获取cate 在IC 中的记录, [cate_name, manu, valid_supplier, valid_stock]
def get_cate_stock(source_files, file_index, sheet_index, cate_name, manu) -> list:
    # 获取工作簿对象
    valid_supplier_sum = 0
    valid_stock_sum = 0
    file_name = source_files[file_index]
    wb = load_workbook(filename=file_name)
    sheet = wb.worksheets[sheet_index]
    used_supplier_arr = []
    min_row = sheet.min_row
    max_row = sheet.max_row
    search_date = "--"
    # 遍历sheet
    for row in range(min_row, max_row + 1):
        supplier = sheet.cell(row, 1).value
        if not (supplier is None or supplier == "--" or (supplier in used_supplier_arr)):
            used_supplier_arr.append(supplier)
            iccp_str = sheet.cell(row, 2).value
            isICCP = "notICCP" not in iccp_str
            sscp_str = sheet.cell(row, 3).value
            isSSCP = "notSSCP" not in sscp_str
            model = sheet.cell(row, 4).value
            isSpotRanking = "notSpotRanking" not in sheet.cell(row, 5).value
            isHotSell = "notHotSell" not in sheet.cell(row, 6).value
            manufacturer = sheet.cell(row, 7).value
            stock_num = sheet.cell(row, 8).value
            search_date = sheet.cell(row, 9).value
            ic_Stock_Info = IC_stock.IC_Stock_Info.IC_Stock_Info(supplier=supplier, isICCP=isICCP, isSSCP=isSSCP,
                                                        model=model,
                                                        isSpotRanking=isSpotRanking, isHotSell=isHotSell,
                                                        manufacturer=manufacturer, stock_num=stock_num,
                                                        search_date=search_date)
            if ic_Stock_Info.is_valid_supplier():
                valid_supplier_sum += 1
                valid_stock_sum += ic_Stock_Info.get_valid_stock_num()
    result = [cate_name, manu, valid_supplier_sum, int(valid_stock_sum/6), search_date]
    return result

'''
def save_ic_stock(file_name, ele_sheet_name, valid_supplier, valid_stock):
    cate_sheet_info_arr = get_cate_by_sheet_name(ele_sheet_name)
    if len(cate_sheet_info_arr) >= 2:
        row_content = [cate_sheet_info_arr[0], cate_sheet_info_arr[1], valid_supplier, valid_stock, time.strftime('%Y-%m-%d', time.localtime())]
        book = load_workbook(file_name)
        sheet = book.get_sheet_by_name("stock")
        sheet.append(row_content)
        book.save(filename=file_name)
        book.close()


# result [model, manufacture]
def get_cate_by_sheet_name(sheet_name):
    # 获取工作簿对象
    wb = load_workbook(filename=cate_source_file)
    # 获取sheet
    ws = wb.get_sheet_by_name("all")
    # 根据单元格名称获取单元格对象
    # result [model, manufacture]
    result = []
    if sheet_name == 'Sheet1':
        return result
    try:
        cate_name = str(base64.b64decode(sheet_name), 'utf-8')
    except:
        temp_cate_name = sheet_name
        missing_padding = 4 - len(temp_cate_name) % 4
        if missing_padding:
            temp_cate_name += '=' * missing_padding
        cate_name = str(base64.b64decode(temp_cate_name),
                        encoding='utf-8')
    for i in range(ws.min_row, ws.max_row + 1):
        index_str = ws.cell(i, 1).value
        if index_str == cate_name:
            result.append(ws.cell(i, 1).value)
            result.append(ws.cell(i, 2).value)
    return result

'''


# 获取ICStock_file_arr 中的所有sheet
def get_ICStock_sheets(source_files):
    result = []
    for file in source_files:
        # 获取工作簿对象
        wb = load_workbook(filename=file)
        # 获取sheet
        sheets_arr = wb.sheetnames
        result.append(sheets_arr)
    return result


# 通过sheets 的二维数组，获取文件index， sheet index
def get_indexs(source_arr, cate_name) -> list:
    sheet_name_base64str = str(base64.b64encode(cate_name.encode('utf-8')), 'utf-8')
    for (file_index, file_sheets) in enumerate(source_arr):
        for (sheet_index, sheet_name) in enumerate(file_sheets):
            if sheet_name == sheet_name_base64str:
                return [file_index, sheet_index]
    return None


#  统计ppn的IC stock info
def staticstic_IC_stock(source_files:list, aim_file:str):
    all_cates = ExcelHelp.read_col_content(file_name=aim_file, sheet_name='ppn', col_index=1)
    sub_cates = all_cates[0:]
    all_ic_sheets = get_ICStock_sheets(source_files)
    for (cate_index, cate_name) in enumerate(sub_cates):
        if cate_name is None:
            continue
        print(f'index is: {cate_index}, pn is :{cate_name}')
        ic_index_arr = get_indexs(all_ic_sheets, str(cate_name))
        manu_name = ExcelHelp.read_cell_content(file_name=aim_file, sheet_name='ppn',
                                                         row=cate_index + 1, col=2)
        if ic_index_arr is not None:
            ic_info_arr = get_cate_stock(source_files=source_files, file_index=ic_index_arr[0], sheet_index=ic_index_arr[1], cate_name=str(cate_name), manu=manu_name)
        else:
            ic_info_arr = [str(cate_name), manu_name, '--', '--', time.strftime('%Y-%m-%d', time.localtime())]
        row_arr = [ic_info_arr]
        ExcelHelp.add_arr_to_sheet(file_name=aim_file, sheet_name='IC_Stock', dim_arr=row_arr)


if __name__ == "__main__":
    staticstic_IC_stock(source_files=ICStock_file_arr, aim_file=cate_source_file)




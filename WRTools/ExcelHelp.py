from openpyxl import load_workbook, Workbook
import os
import base64


# READ
# 获取某一列的内容返回cate list
def read_col_content(file_name: object, sheet_name: object, col_index: int) -> list:
    # 获取工作簿对象
    wb = load_workbook(filename=file_name)
    # 获取sheet
    ws = wb[sheet_name]
    # 根据单元格名称获取单元格对象
    result = []
    for i in range(ws.min_row, ws.max_row + 1):
        cate = ws.cell(i, col_index).value
        if not cate == "--":
            result.append(str(cate))
    # print("result is:", result)
    wb.save(filename=file_name)
    wb.close()
    return result


# 获取某一cell的内容 返回str
def read_cell_content(file_name, sheet_name, col, row) -> str:
    # 获取工作簿对象
    wb = load_workbook(filename=file_name)
    # 获取sheet
    ws = wb[sheet_name]
    # 根据单元格名称获取单元格对象
    cell_content = ws.cell(row=row, column=col).value
    return str(cell_content)


# 根据sheet_name 获取sheet 中到内容，返回二维数组
def read_sheet_content_by_name(file_name, sheet_name):
    wb = load_workbook(file_name)
    ws = wb[sheet_name]
    # 获取所有行所有列
    content_list = []
    for row in ws.iter_rows():
        row_list = []
        for cell in row:
            cell_value = str(cell.value)
            row_list.append(cell_value)
        if len(row_list) > 0:
            content_list.append(row_list)
    return content_list


# 根据sheet_index 获取sheet 中到内容，返回二维数组
def read_sheet_content_by_index(file_name, sheet_index):
    wb = load_workbook(file_name)
    ws = wb.worksheets[sheet_index]
    # 获取所有行所有列
    content_list = []
    for row in ws.iter_rows():
        row_list = []
        for cell in row:
            cell_value = str(cell.value)
            row_list.append(cell_value)
        if len(row_list) > 0:
            content_list.append(row_list)
    return content_list


#WRITE
def create_sheet(sheet_name, wb):
    print(f'add sheet : {sheet_name}')
    wb.create_sheet(sheet_name)


def isSheetExist(sheet_name, wb):
    old_sheet_names = wb.sheetnames
    if old_sheet_names.__contains__(sheet_name):
        return True
    else:
        return False


# 将库存数据保存到sheet 中
# sheet_name: 由cate_name base64加密得到
# arr 是二维数组[[cate1_name, cate1_supplier], [cate2_name, cate2_supplier]]
def add_arr_to_sheet(file_name, sheet_name: object, dim_arr: object):
    
    print('arr is:', dim_arr)
    if os.path.exists(file_name):
        wb = load_workbook(file_name)
    else:
        wb = Workbook()
    if not isSheetExist(sheet_name, wb):
        create_sheet(sheet_name, wb)
    sheet = wb[sheet_name]
    for ele in dim_arr:
        sheet.append(ele)
    wb.save(file_name)
    wb.close()


# 把一个数组保存到某一列中
def save_one_col(file_name:str, sheet_name: str, col_index: int, dim_arr: list):
    
    print('arr is:', dim_arr)
    if os.path.exists(file_name):
        wb = load_workbook(file_name)
    else:
        wb = Workbook()
    if not isSheetExist(sheet_name, wb):
        create_sheet(sheet_name, wb)
    sheet = wb[sheet_name]
    for (ele_index, ele) in enumerate(dim_arr):
        try:
            if ele and len(ele) > 0:
                sheet.cell(row=ele_index+1, column=col_index).value = ele
        except:
            print(f'{ele_index}th ele: {ele} set is err')
    wb.save(file_name)
    wb.close()


def set_col_width(sheet_name, wb):
    sheet = wb[sheet_name]
    sheet.column_dimensions["A"].width = 36.0


# 在单元格中写入内容
def write_cell(file_name, sheet_name, row, col, value):
    
    if os.path.exists(file_name):
        wb = load_workbook(file_name)
    else:
        wb = Workbook()
    sheet = wb[sheet_name]
    sheet.cell(row=row, column=col).value = value
    wb.save(file_name)
    wb.close()


# 写入自己创建的sheet 即可避免sheets 为空的问题
def active_excel(file_name, sheet_name):
    
    wb = load_workbook(file_name)
    wb.create_sheet(sheet_name)
    wb.save(file_name)
    wb.close()


# 将Excel 除第一个sheet 外的所哟sheet 删除
def remove_sheets(file_name):
    wb = load_workbook(file_name)
    for (index, sheet) in enumerate(wb.worksheets):
        if index == 0:
            continue
        else:
            wb.remove(sheet)
    wb.save(file_name)
    wb.close()


# 读取某个sheet 内容，然后写到另一个sheet 中，可以用于多个sheet 合并到同一个sheet 中
def move_sheet_to_row(source_file_list, source_sheet_name, aim_file, aim_sheet):
    for source_file in source_file_list:
        source_wb = load_workbook(source_file)
        source_sheet_names = source_wb.sheetnames
        for (sheet_index, sheet_name) in enumerate(source_sheet_names):
            sheet_name_base64str = source_sheet_name
            if sheet_name_base64str == sheet_name:
                source_list = read_sheet_content_by_name(file_name=source_file, sheet_name=sheet_name)
                add_arr_to_sheet(file_name=aim_file, sheet_name=aim_sheet, dim_arr=source_list)
                return


if __name__ == "__main__":
    # active_excel('/Users/liuhe/PycharmProjects/SeleniumDemo/T0921.xlsx', "Sheet2")
    remove_sheets('/Users/liuhe/PycharmProjects/SeleniumDemo/Octopart_price/octopart_price_cate_E01.xlsx')

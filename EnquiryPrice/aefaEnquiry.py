from WRTools import ExcelHelp, PandasHelp
import time


# 临时询价
def enquiry():
    source_file = '/Users/liuhe/Desktop/询价/询价2023-10-19.xlsx'
    source_sheet = 'Sheet1'
    source_list = ExcelHelp.read_sheet_content_by_name(source_file, source_sheet)[1:]
    result = []
    today = time.strftime('%Y-%m-%d', time.localtime())

    for temp in source_list:
        row = [temp[0], temp[7], temp[1], temp[6], "  ", temp[5], "  ", temp[10], temp[9], temp[4], "  ", "  ", temp[2],
               temp[13], "  ", "  ", "  ", "  ", "  ", "  ", "  ", "  ", "  ", temp[3], "  ",
               temp[17] if (temp[17].__len__() > 0) else '国内贸易商',
               temp[16], "  ", temp[15], "  ", "  ", temp[18] if (temp[18].__len__() > 0) else today, "  ",
               temp[19],
               temp[8], "  ", "  ", temp[11], temp[12], temp[14]]
        result.append(row)
    std_sheet = 'aim'
    # 型号	数量	厂商	批号	封装	品名	成本价	报价	客接受价	联系人	电话	手机	客户名称	税点	新旧程度	单位	币种	起订量	标准包装	利润率%	客户要求	QQ	Email	地址	客户料号	客户类型	来源	重要程度	备注1	备注2	分支机构	询价日期	产品编码	拥有人	货期	供应商名称	采购币种	自定义列1	自定义列2	自定义列3
    if result.__len__() > 0:
        ExcelHelp.add_arr_to_sheet(source_file, std_sheet, result)


if __name__ == "__main__":
    enquiry()
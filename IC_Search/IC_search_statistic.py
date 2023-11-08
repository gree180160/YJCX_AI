# 统计pn 在IC 交谊网的热度
from WRTools import ExcelHelp, PathHelp, MySqlHelp_recommanded
import base64

pn_file = PathHelp.get_file_path(super_path=None, file_name='TRuStock.xlsx')

def get_price_level(pn) ->str:
    result = ""
    pn_stock_info_arr = ExcelHelp.read_sheet_content_by_name(file_name=pn_file, sheet_name='priceAll')
    for tempPN_info in pn_stock_info_arr:
        if tempPN_info:
            if pn == tempPN_info[0]:
                result = tempPN_info[5]
                break;
    return result

# [max, max2, min]
def get_search_data(isWeek, pn) ->list:
    result = []
    if isWeek:
        # 1.确定sheet， 2.确定在哪一列 3.找出排除空和'/' 4.找出max，max2，min
        pns = ExcelHelp.read_row_content(file_name=pn_file, sheet_name='hot_week', row_index=1)
    else:
        pns = ExcelHelp.read_row_content(file_name=pn_file, sheet_name='hot_month', row_index=1)
    index = pns.index(pn) if (pn in pns) else -1
    print(f'find index is:{index}')
    if index > 0:
       search_num_arr = ExcelHelp.get_search_num(file_name=pn_file, sheet_name='hot_week' if isWeek else 'hot_month', col_index=index+1)
       search_num_arr = list(filter(None, search_num_arr))
       search_num_arr.sort()
       if search_num_arr and search_num_arr.__len__() > 0:
           result = [search_num_arr[search_num_arr.__len__() - 1], search_num_arr[search_num_arr.__len__() - 2], search_num_arr[0]]
    if result.__len__() > 0:
        return result
    else:
        return ["/", "/", "/"]


# 返回靠谱的供应商数量和w库存
def get_stockInfo(pn) ->list:
    result = ["--", "--"]
    pn_stock_info_arr = ExcelHelp.read_sheet_content_by_name(file_name=pn_file, sheet_name='IC_Stock')
    for tempPN_info in pn_stock_info_arr:
        if tempPN_info:
            if pn == tempPN_info[0]:
                supllier = tempPN_info[2]
                stock = tempPN_info[3]
                result = [str(supllier), str(stock)]
                break;
    return result


def statistic_all():
    pnsinfo = ExcelHelp.read_sheet_content_by_name(file_name=pn_file, sheet_name='ppn')
    sub_pns = pnsinfo[0:]
    search_statistic_arr = []
    for (index, tempInfo) in enumerate(sub_pns):
        pn = tempInfo[0]
        print(f'index is:{index} pn is: {pn}')
        manu = tempInfo[1]
        price_level = get_price_level(pn=pn)
        week_search = get_search_data(isWeek=True, pn=pn)
        month_search = get_search_data(isWeek=False, pn=pn)
        supplier_Num = get_stockInfo(pn)
        statistic_info = [pn, manu, price_level, str(supplier_Num[0]), str(supplier_Num[1]), str(week_search[0]), str(week_search[1]),
                          str(week_search[2]), str(month_search[0]), str(month_search[1]), str(month_search[2])]
        search_statistic_arr.append(statistic_info)
    ExcelHelp.add_arr_to_sheet(file_name=pn_file, sheet_name='IC_statistic', dim_arr=search_statistic_arr)


# 只统计搜索热度
def statistic_simple():
    pnsinfo = ExcelHelp.read_sheet_content_by_name(file_name=pn_file, sheet_name='ppn')
    sub_pns = pnsinfo[0:]
    search_statistic_arr = []
    for (index, tempInfo) in enumerate(sub_pns):
        pn = tempInfo[0]
        print(f'index is:{index} pn is: {pn}')
        manu = tempInfo[1]
        week_search = get_search_data(isWeek=True, pn=pn)
        month_search = get_search_data(isWeek=False, pn=pn)
        statistic_info = [pn, manu, str(week_search[0]), str(week_search[1]),
                          str(week_search[2]), str(month_search[0]), str(month_search[1]), str(month_search[2])]
        search_statistic_arr.append(statistic_info)
    ExcelHelp.add_arr_to_sheet(file_name=pn_file, sheet_name='IC_search', dim_arr=search_statistic_arr)


############################   DB    #####################################################
def getDBData_m():
    # IC_hot_m_read
    IC_Search_list_m = MySqlHelp_recommanded.DBRecommandChip().IC_hot_m_read("update_time > '2023/10/08'")
    result_m = []
    for temp in IC_Search_list_m:
        search_num_arr = [temp[2], temp[3], temp[4], temp[5], temp[6], temp[7], temp[8], temp[9], temp[10], temp[11], temp[12], temp[13]]
        first_value = temp[2]
        search_num_arr.sort()
        if search_num_arr and search_num_arr.__len__() > 0:
            ppnInfo = [temp[0], temp[1], search_num_arr[search_num_arr.__len__() - 1], search_num_arr[search_num_arr.__len__() - 2], first_value]
        result_m.append(ppnInfo)
    ExcelHelp.add_arr_to_sheet(pn_file, 'IC_search_m', result_m)


def getDBData_w():
    IC_Search_list_w = MySqlHelp_recommanded.DBRecommandChip().IC_hot_w_read("update_time > '2023/10/08'")
    result_w = []
    for temp in IC_Search_list_w:
        search_num_arr = [temp[2], temp[3], temp[4], temp[5], temp[6], temp[7], temp[8], temp[9], temp[10],
                          temp[11],temp[12], temp[13], temp[14], temp[15], temp[16], temp[17], temp[18], temp[19], temp[20],
                          temp[21], temp[22], temp[23], temp[24], temp[25], temp[26], temp[27], temp[28], temp[29],temp[30],
                          temp[31], temp[32], temp[33], temp[34], temp[35], temp[36], temp[37], temp[38], temp[39],temp[40],
                          temp[41], temp[42], temp[43], temp[44], temp[45], temp[46], temp[47], temp[48], temp[49],temp[50],
                          temp[51], temp[52], temp[53]
                          ]
        first_value = temp[2]
        search_num_arr.sort()
        if search_num_arr and search_num_arr.__len__() > 0:
            ppnInfo = [temp[0], temp[1], search_num_arr[search_num_arr.__len__() - 1], search_num_arr[search_num_arr.__len__() - 2], first_value]
        result_w.append(ppnInfo)
    ExcelHelp.add_arr_to_sheet(pn_file, 'IC_search_w', result_w)


if __name__ == "__main__":
    getDBData_m()
    getDBData_w()
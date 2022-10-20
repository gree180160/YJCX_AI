from WRTools import ExcelHelp


def get_zmz_cate():
    # want add
    source_file_arr = ["/Users/liuhe/Desktop/zmz/商友库存整理2022.09.20.xlsx",
                       "/Users/liuhe/Desktop/zmz/商友库存整理2022.09.22.xlsx",
                       "/Users/liuhe/Desktop/zmz/商友库存整理2022.09.26.xlsx"]
    all_lists = []
    for temp_file in source_file_arr:
        file_cates = ExcelHelp.read_col_content(file_name=temp_file, sheet_name='型号明细', col_index=2)[1:]
        all_lists = list(set(all_lists).union(set(file_cates)))
    all_lists = list(filter(None, all_lists))
    all_lists.sort()
    # used
    used_cate_files = ["/Users/liuhe/PycharmProjects/SeleniumDemo/T0806.xlsx",
                      "/Users/liuhe/PycharmProjects/SeleniumDemo/T0815.xlsx",
                      "/Users/liuhe/PycharmProjects/SeleniumDemo/T0829zmz.xlsx",
                      "/Users/liuhe/PycharmProjects/SeleniumDemo/T0907zmz.xlsx",
                      "/Users/liuhe/PycharmProjects/SeleniumDemo/T0909.xlsx",
                      "/Users/liuhe/PycharmProjects/SeleniumDemo/T0921.xlsx"
                      ]
    used_lists = []
    for temp_file in used_cate_files:
        file_cates = ExcelHelp.read_col_content(file_name=temp_file, sheet_name='all', col_index=1)
        used_lists = list(set(all_lists).union(set(file_cates)))
    used_lists = list(filter(None, used_lists))
    used_lists.sort()
    # valid
    result_list = list(set(all_lists).difference(set(used_lists)))
    ExcelHelp.save_one_col(file_name= '/Users/liuhe/PycharmProjects/SeleniumDemo/T0927.xlsx', sheet_name='all', col_index=1, dim_arr=result_list)


if __name__ == "__main__":
    get_zmz_cate()
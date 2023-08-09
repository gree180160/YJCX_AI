import pandas as pd


def csv_to_xlsx_pd(file):
    csv = pd.read_csv(file + '.cvs', encoding='utf-8')
    csv.to_excel(file + ".xlsx", sheet_name='data')


def read_sheet_content(file_name):
    source_data = pd.read_csv(file_name)
    list2 = source_data.values.tolist()
    return list2


if __name__ == '__main__':
   result = read_sheet_content("/Users/liuhe/Downloads/js/_____ - 2023-08-02T160045.150.csv")
   print(result)
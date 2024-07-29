from translatepy import Translator
import re


def trans2():
    trans = Translator()
    a = trans.translate('hello', 'zh')
    print(a)


def IC_batch(source:str):
    #停产，批次无法匹配，显示问题数据 ， 没停产批次无法匹配，显示21
    result = source
    if source.isdigit():
        if len(source) == 4: #1236
            return source
        elif len(source) == 2: #22
            result = source+"+"
    else:
        if re.match(r'\d+[+/]/\d+', source): #21+/30
            result = source.replace("+/", '+,')
            result = result + "+"
        elif re.match(r'\d{4}/\d{1,2}', source): # 2325/2
            result = source[0:2]+'+'
        elif re.match(r'\d+\+\d+', source): # 22+21
            result = source.replace("+", '+,')
            result = result + "+"
        elif re.match(r'\d+/\d+\+', source): # 19/20+
            result = source.replace("/", '+,')
        else:
            result = source
        if result.startswith('0'):
            result = "20" + result
    return result


# 将价格描述，转成纯数字 ¥119.00/台
def strToPrice(source_str):
    try:
        if len(source_str) == 0:
            return "0.00"
        price_str = source_str
        price_value = re.search(r'\d+\.\d+', price_str).group()
        price_float = float(price_value)
        price_rounded = round(price_float, 2)
        return str(price_rounded)
    except Exception as e :
        print(f'{source_str} has exceptio: {e}')
        return "0.00"


if __name__ == "__main__":
    # print( IC_batch("21+/30"), IC_batch("19/20+"), IC_batch("2325/2"),   IC_batch("22+21"))
    aa = strToPrice('¥1028.50/台')
    print(aa)





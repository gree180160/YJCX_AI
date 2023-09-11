import requests

# 发送API请求获取汇率数据


def EURtoRUB(source_amount):
    response = requests.get("https://api.exchangerate-api.com/v4/latest/EUR")
    data = response.json()
    # 获取欧元兑卢布的汇率
    exchange_rate = data["rates"]["RUB"]
    # 进行欧元到卢布的转换
    euro_amount = source_amount
    rub_amount = euro_amount * exchange_rate
    print(rub_amount)
    return rub_amount


def USDtoRUB(source_amount):
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    data = response.json()
    # 获取欧元兑卢布的汇率
    exchange_rate = data["rates"]["RUB"]
    # 进行欧元到卢布的转换
    euro_amount = source_amount
    rub_amount = euro_amount * exchange_rate
    print(rub_amount)
    return rub_amount


if __name__ == "__main__":
    EURtoRUB(100)
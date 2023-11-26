import time
import random
from datetime import datetime


# 普通website等待时间，load new page -> 70s; else 20s
def waitfor(is_load_page, isDebug):
    if isDebug:
        time.sleep(5 + random.randint(1, 3))
    else:
        # load new page
        if is_load_page:
            time.sleep(100 + random.randint(5, 55))
        else:
            time.sleep(20 + random.randint(2, 22))


# test ， for octopart
def waitfor_octopart(is_load_page, isDebug):
    if isDebug:
        time.sleep(5 + random.randint(1, 3))
    else:
        # load new page
        if is_load_page:
            time.sleep(150 + random.randint(5, 55))
        else:
            time.sleep(15 + random.randint(2, 22))


# test ， for octopart
def waitfor_ICHot(is_load_page, isDebug):
    if isDebug:
        time.sleep(5 + random.randint(1, 3))
    else:
        # load new page
        if is_load_page:
            time.sleep(130 + random.randint(10, 50))
        else:
            time.sleep(15 + random.randint(2, 22))


# 适用于不需要账号，有隧道代理，load new page -> 60; else 5s
def waitfor_auto_proxy(is_load_page, isDebug):
    if isDebug:
        time.sleep(5 + random.randint(1, 3))
    else:
        if is_load_page:
            time.sleep(60 + random.randint(1, 20))
        else:
            time.sleep(5 + random.randint(1, 5))


# 账号较为重要，不能被封，等待时间，load new page -> 150s; else 5s
def waitfor_account_import(is_load_page, isDebug):
    if isDebug:
        time.sleep(5 + random.randint(1, 3))
    else:
        if is_load_page:
            time.sleep(160 + random.randint(1, 120))
        else:
            time.sleep(5 + random.randint(1, 10))


# 计算过了多少天
def daysPassed(thatDay: str) -> int:
    try:
        now = datetime.now()
        past = thatDay
        past = list(map(int, past.split('/')))
        if past.__len__() == 2:
            past = datetime(past[0], past[1], 1)
        else:
            past = datetime(past[0], past[1], past[1])
        delta = now - past
        result = delta.days
    except:
        result = 99999
    return result


# wait_time_kind, -1-> waitfor_octopart, 0 -> waitfor, 1 ->waitfor_account_import
def waitfor_kind(kind:int, is_load_page, isDebug):
    if kind == -1:
        waitfor_octopart(is_load_page=is_load_page, isDebug=isDebug)
    elif kind == 1:
        waitfor_account_import(is_load_page=is_load_page, isDebug=isDebug)
    else:
        waitfor(is_load_page=is_load_page, isDebug=isDebug)


if __name__ == "__main__":
    result = daysPassed('2023/08')
    print(result)
import random
import datetime
import time


# 普通website等待时间，load new page -> 70s; else 20s
def waitfor(is_load_page, isDebug):
    if isDebug:
        time.sleep(5 + random.randint(1, 3))
    else:
        # load new page
        if is_load_page:
            time.sleep(120 + random.randint(5, 80))
        else:
            time.sleep(20 + random.randint(2, 22))


# test ， for octopart
def waitfor_octopart(is_load_page, isDebug):
    if isDebug:
        time.sleep(5 + random.randint(1, 3))
    else:
        # load new page
        if is_load_page:
            time.sleep(180 + random.randint(10, 55))
        else:
            time.sleep(30 + random.randint(2, 22))


# test ， for octopart
def waitfor_ICHot(is_load_page, isDebug):
    if isDebug:
        time.sleep(5 + random.randint(1, 3))
    else:
        # load new page
        if is_load_page:
            time.sleep(120 + random.randint(10, 200))
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


def isSleep_time():
    current_time = datetime.datetime.now().time()
    if current_time < datetime.time(8, 0) or (datetime.time(11, 50) <= current_time <= datetime.time(13, 30)) or (datetime.time(17, 50) <= current_time <= datetime.time(18, 30)) or current_time >= datetime.time(20, 30):
        return True
    else:
        return False


if __name__ == "__main__":
    # result = daysPassed('2023/08')
    result = isSleep_time()
    if isSleep_time():
        print("进入休眠状态")
        time.sleep(60)  # 每隔60秒检查一次时间
    else:
        print("程序继续运行")
        time.sleep(60)
    print(result)
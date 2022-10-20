import time
import random


# 普通website等待时间，load new page -> 70s; else 20s
def waitfor(is_load_page, isDebug):
    if isDebug:
        time.sleep(5 + random.randint(1, 3))
    else:
        # load new page
        if is_load_page:
            time.sleep(70 + random.randint(5, 55))
        else:
            time.sleep(20 + random.randint(2, 22))


# test ， for octopart
def waitfor_octopart(is_load_page, isDebug):
    if isDebug:
        time.sleep(5 + random.randint(1, 3))
    else:
        # load new page
        if is_load_page:
            time.sleep(180 + random.randint(5, 55))
        else:
            time.sleep(20 + random.randint(2, 22))


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
            time.sleep(150 + random.randint(1, 120))
        else:
            time.sleep(5 + random.randint(1, 10))


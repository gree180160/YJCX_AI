from pykeyboard import PyKeyboard
from pymouse import PyMouse
from WRTools import WaitHelp
import pyperclip
import webbrowser

import time

m = PyMouse()
k = PyKeyboard()


#  for test
def testMouse():
    x_dim, y_dim = m.screen_size()
    time.sleep(5)
    print(m.position())


# 测试键盘key 名称
def testKeyboard():
    k.press_keys(['control', 'Tab'])

# ------------------octopart---------------------------
# 先现实页面源码，在保存显示源码的页面
def saveWebpagePage():
    time.sleep(5)
    for i in range(0, 4):
        print(f'index is:{i}')
        #   load current page
        time.sleep(5.0)
        # 显示源码
        k.press_keys(['command', 'u'])
        time.sleep(20.5)
        # 保存
        k.press_keys(['command', 's'])
        time.sleep(2.0)
        k.press_key('Return')
        time.sleep(0.5)
        # 预防保存按钮反应迟钝
        k.press_key('Return')
        # 翻页
        time.sleep(2.0)
        k.press_keys(['control', 'Tab'])
        k.release_key('command')


# wait_time_kind, -1-> waitfor_octopart, 0 -> waitfor, 1 ->waitfor_account_import
def input_url(url, wait_time_kind: int):
    # 帮助火狐拿回系统的焦点
    webbrowser.open(
        'http://localhost:63342/SeleniumDemo/Octopart_category/octopart_key_cate.html')
    time.sleep(2.0)
    # 浏览器必须位于屏幕左上角
    m.click(463.171875, 105.9609375, 1)
    # 将url copy 到粘贴板
    pyperclip.copy(url)
    time.sleep(0.5)
    # 复制粘贴板
    k.press_keys(['command', 'v'])
    k.release_key('command')
    time.sleep(2.0)
    k.tap_key('Return')
    # load html code
    WaitHelp.waitfor_kind(kind=wait_time_kind, is_load_page=True, isDebug=False)


def webpage_saveAndClose():
    # 保存
    k.press_keys(['command', 's'])
    k.release_key('command')
    time.sleep(2.0)
    k.tap_key('Return')
    time.sleep(0.5)
    # 预防保存按钮反应迟钝
    k.tap_key('Return')
    # 关闭页面
    time.sleep(2.0)
    k.press_keys(['command', 'w'])
    k.release_key('command')


# -------IC_Hot----------------------------------------
# 保存页面的长截图
def screenShot_saveAndClose():
    # 保存
    k.press_keys(['Alternate', 'a'])
    k.release_key('Alternate')
    time.sleep(5.0)
    k.tap_key('s')
    time.sleep(2.0)


def test_open_save():
    time.sleep(4)
    arr = ['view-source:https://octopart.com/search?q=A3212&currency=USD&specs=0&start=680',
           'view-source:https://octopart.com/search?q=A3212&currency=USD&specs=0&start=640',
           'view-source:https://octopart.com/search?q=A3212&currency=USD&specs=0&start=930']
    for (index, tempURL) in  enumerate(arr):
        print(f'index is : {index}')
        input_url(url=tempURL)
        webpage_saveAndClose()


if __name__ == "__main__":
    # test_open_save()
    time.sleep(3)
    screenShot_saveAndClose()


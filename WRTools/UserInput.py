from pykeyboard import PyKeyboard
from pymouse import PyMouse
from WRTools import WaitHelp
import pyperclip
import webbrowser
from sys import platform
import time
import re

m = PyMouse()
k = PyKeyboard()


# ------------------octopart---------------------------
# wait_time_kind, -1-> waitfor_octopart, 0 -> waitfor, 1 ->waitfor_account_import
def input_url(url, wait_time_kind: int):
    # 帮助火狐拿回系统的焦点
    if platform.startswith('win'):
        webbrowser.open('https://www.baidu.com')
        time.sleep(2.0)
        m.click(350, 60)  # 浏览器必须位于屏幕左上角
        pyperclip.copy(url)
        time.sleep(0.5)
        k.press_keys([k.control_key, 'v'])
        k.release_key(k.control_key)
        time.sleep(2.0)
        k.tap_key(k.enter_key)
        # load html code
        WaitHelp.waitfor_kind(kind=wait_time_kind, is_load_page=True, isDebug=False)
    else:
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
    if platform.startswith('win'):
        k.press_keys([k.control_key, 's'])
        k.release_key(k.control_key)
        time.sleep(2.0)
        k.tap_key(k.enter_key)
        time.sleep(0.5)
        # 无差别替换旧html 文件
        k.tap_key(k.left_key)
        # 预防保存按钮反应迟钝
        k.tap_key(k.enter_key)
        # 关闭页面
        time.sleep(2.0)
        k.press_keys([k.control_key, 'w'])
        k.release_key(k.control_key)
    else:
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
    if platform.startswith('win'):
        k.press_keys([k.control_key, 'q'])
        k.release_key(k.control_key)
        time.sleep(2.0)
        k.tap_key('s')
        time.sleep(2.0)
    else:
        k.press_keys(['Alternate', 'a'])
        k.release_key('Alternate')
        time.sleep(2.0)
        k.tap_key('s')
        time.sleep(2.0)


def test_open_save():
    time.sleep(4)
    arr = ['view-source:https://octopart.com/search?q=A3212&currency=USD&specs=0&start=680',
           'view-source:https://octopart.com/search?q=A3212&currency=USD&specs=0&start=640',
           'view-source:https://octopart.com/search?q=A3212&currency=USD&specs=0&start=930']
    for (index, tempURL) in enumerate(arr):
        print(f'index is : {index}')
        input_url(url=tempURL)
        webpage_saveAndClose()


def save_firfox_image(count: int):
    if platform.startswith('win'):
        time.sleep(3)
        k.press_keys([k.control_key, k.tab_key])
        k.release_key(k.control_key)
        for index in range(0, count):
            print(f'index is: {index}')
            time.sleep(2.0)
            k.press_keys([k.control_key, 'q'])
            k.release_key(k.control_key)
            time.sleep(3.0)
            k.tap_key('s')
            time.sleep(3.0)
            m.click(350, 160)
            time.sleep(2.0)
            k.press_keys([k.control_key, k.tab_key])
            k.release_key(k.control_key)
    else:
        time.sleep(3)
        k.press_keys(['control', 'tab'])
        k.release_key('control')
        for index in range(0, count):
            print(f'index is: {index}')
            time.sleep(2.0)
            k.press_keys(['Alternate', 'a'])
            k.release_key('Alternate')
            time.sleep(3.0)
            k.tap_key('s')
            time.sleep(3.0)
            m.click(463.171875, 305.9609375, 1)
            time.sleep(1.0)
            k.press_keys(['control', 'tab'])
            k.release_key('control')


if __name__ == "__main__":
    # test_open_save()
    # time.sleep(3)
    # screenShot_saveAndClose()
    save_firfox_image(125)
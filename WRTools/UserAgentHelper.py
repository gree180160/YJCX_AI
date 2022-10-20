import random
from WRTools import ExcelHelp


user_agent_arr = ExcelHelp.read_col_content(file_name='/Users/liuhe/PycharmProjects/SeleniumDemo/WRTools/IP&UA.xlsx', sheet_name="UA", col_index=1)


def getRandowUA() -> str:
    return random.choice(user_agent_arr)


def getRandowUA_windows() -> str:
    windows_list = [x for x in user_agent_arr if x.__contains__('Windows')]
    return random.choice(windows_list)


def getRandowUA_Mac() -> str:
    mac_list = [x for x in user_agent_arr if x.__contains__('Macintosh')]
    return random.choice(mac_list)


def driver_update_UA(webdriver):
    webdriver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": getRandowUA_Mac(),
        "platform": "Macintosh"})




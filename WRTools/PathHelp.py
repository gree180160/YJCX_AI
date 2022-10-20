from sys import platform


def get_file_path(super_path, file_name) -> str:
    result = root_path = ''
    if platform.startswith('linux'):
        root_path = ''
        tail = ''
    elif platform.startswith('win'):
        root_path = 'C:\\Users\\14592\\Desktop\\SeleniumDemo\\'
        tail = f'{super_path}\\{file_name}' if super_path else f'{file_name}'
    else:
        root_path = '/Users/liuhe/PycharmProjects/SeleniumDemo/'
        tail = f'{super_path}/{file_name}' if super_path else f'{file_name}'
    result = root_path + tail
    return result


if __name__ == "__main__":
    keyword_source_file = get_file_path(super_path=None, file_name='TKeywords.xlsx')
    log_file = get_file_path(super_path='Octopart_category', file_name='octopart_key_cate_log.txt')
    print(keyword_source_file)
    print(log_file)


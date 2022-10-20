# 写入日志内容
import string
import time


# 写入日志
def write_log(log_file_name, content):
    print(content)
    save_content = befor_anchor(content, 'Stacktrace:')
    save_content = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + save_content
    file = open(log_file_name, 'a+')
    file.write(save_content + "\n")
    file.close()


def befor_anchor(source, anchor) -> string:
    result = source
    index = source.find(anchor)
    if index >= 0:
        result = source[0: index]
    return result


if __name__ == '__main__':
    write_log("", '')

from translatepy import Translator


def trans2():
    trans = Translator()
    a = trans.translate('hello', 'zh')
    print(a)


if __name__ == "__main__":
    trans2()


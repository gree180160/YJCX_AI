from PyPDF2 import PdfReader, PdfWriter

# 1.打开需要添加封面的PDF文件
files1 = PdfReader('/Users/liuhe/Library/Containers/com.hp.SmartMac/Data/Documents/14.pdf')
# 获取总页数
count = files1.pages.__len__()

# 创建空的PDF
file2 = PdfWriter()

# 将第一个pdf的页面（除去第一页）加进来
for x in range(count):
    if x != 1:
        page = files1.pages[x]
        file2.add_page(page)
#把第二个pdf的最后一页加进来
last_page = PdfReader('/Users/liuhe/Library/Containers/com.hp.SmartMac/Data/Documents/5.pdf').pages[-1]
file2.add_page(last_page)
#保存文件
file2.write('/Users/liuhe/Library/Containers/com.hp.SmartMac/Data/Documents/result.pdf')
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

my_sender = '2147770436@qq.com'  # 发件人邮箱账号
my_pass = 'hfkletvsoglvdjbg'  # 发件人邮箱授权码，第一步得到的
my_user = '1103385722@qq.com'  # 收件人邮箱账号，可以发送给自己


def mail_TI(cate_name, stock_num, detail_data):
    ret = True
    try:
        # msg=MIMEText('填写邮件内容','plain','utf-8')
        mail_msg = f'<h2><center>Ti</center></h2> 以下型号有库存:  {cate_name}  <br>   limit数量是: {str(stock_num)} <br> distributorsList 信息: {detail_data}'
        msg = MIMEText(mail_msg, 'html', 'utf-8')
        msg['From'] = formataddr(["From Ti buy", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["Jason", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "发现目标TI"  # 邮件的主题，也可以说是标题
        #  user email
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, [my_user, my_sender], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as err:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret


#  supplier_list-> [[supplier, cate_name, stock_num]]
def mail_Findchips(supplier_list):
    ret = True
    try:
        # msg=MIMEText('填写邮件内容','plain','utf-8')
        mail_msg = '<h2><center>findchips</center></h2>'
        for temp_supplier in supplier_list:
            mail_msg = mail_msg + f'在平台: {temp_supplier[0]}  <br> 以下型号有库存:  {temp_supplier[1]}  <br> 数量为: {str(temp_supplier[2])}  <br> #################### <br>'
        msg = MIMEText(mail_msg, 'html', 'utf-8')
        msg['From'] = formataddr(["From Findchips buy", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["Jason", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "发现目标Findchips"  # 邮件的主题，也可以说是标题
        #  user email
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, [my_user, my_sender], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as err:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret


# IC 交易网查库存，出现验证码
def mail_IC_Stock(device):
    ret = True
    try:
        new_user = '1459287460@qq.com'
        # msg=MIMEText('填写邮件内容','plain','utf-8')
        mail_msg = f'<h2><center>IC_stock</center></h2> 设备: {device} 出现check code'
        msg = MIMEText(mail_msg, 'html', 'utf-8')
        msg['From'] = formataddr(["From Ti buy", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["river", new_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "IC_Stock"  # 邮件的主题，也可以说是标题
        #  user email
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, [new_user, my_sender], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as err:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret


def mail_ip_error(device):
    ret = True
    try:
        new_user = '1459287460@qq.com'
        # msg=MIMEText('填写邮件内容','plain','utf-8')
        mail_msg = f'<h2><center>Octopart</center></h2> 设备: {device} 出现security check'
        msg = MIMEText(mail_msg, 'html', 'utf-8')
        msg['From'] = formataddr(["From Ti buy", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["river", new_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "Octopart"  # 邮件的主题，也可以说是标题
        #  user email
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, [new_user, my_sender], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as err:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret


if __name__ == '__main__':
    ret = mail_TI('test ', 666)
    if ret:
        print("邮件发送成功")
    else:
        print("邮件发送失败")


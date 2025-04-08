import smtplib
import time
from email.mime.text import MIMEText
from email.utils import formataddr
from email.mime.application import MIMEApplication
from WRTools import PathHelp
from email.mime.multipart import MIMEMultipart
import random
import os

my_sender = '2147770436@qq.com'  # 发件人邮箱账号
my_pass = 'ewmnwpveacoyeagh'  # 发件人邮箱授权码，第一步得到的


def sendWho(device):
    river = '1459287460@qq.com'  # 收件人邮箱账号，可以发送给自己
    alex = 'alex@calcitrapa.com'
    if device == 'AOC':
        return [river, alex]
    else:
        return [river]


def mail_TI(cate_name, stock_num, detail_data):
    ret = True
    try:
        # msg=MIMEText('填写邮件内容','plain','utf-8')
        mail_msg = f'<h2><center>Ti</center></h2> 以下型号有库存:  {cate_name}  <br>   limit数量是: {str(stock_num)} <br> distributorsList 信息: {detail_data}'
        msg = MIMEText(mail_msg, 'html', 'utf-8')
        msg['From'] = formataddr(["From Ti buy", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        receives = sendWho("")
        msg['To'] = ', '.join(receives)  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "发现目标TI"  # 邮件的主题，也可以说是标题
        #  user email
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, receives, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
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
        receives = sendWho("")
        msg['To'] =', '.join(receives)  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "发现目标Findchips"  # 邮件的主题，也可以说是标题
        #  user email
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, receives, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
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
        msg['From'] = formataddr(["From IC Stock", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        receives = sendWho(device)
        msg['To'] = ', '.join(receives)
        msg['Subject'] = "IC_Stock"  # 邮件的主题，也可以说是标题
        #  user email
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, receives, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as err:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret


# IC 交易网查库存，出现验证码
def mail_HQ_hot(device):
    ret = True
    try:
        new_user = '1459287460@qq.com'
        # msg=MIMEText('填写邮件内容','plain','utf-8')
        mail_msg = f'<h2><center>HQ hot</center></h2> 设备: {device} 出现check code'
        msg = MIMEText(mail_msg, 'html', 'utf-8')
        msg['From'] = formataddr(["From HQ hot", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        receives = sendWho(device)
        msg['To'] = ', '.join(receives)
        msg['Subject'] = "HQ hot"  # 邮件的主题，也可以说是标题
        #  user email
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, receives, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as err:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret


# IC 交易网查库存，出现验证码
def mail_IC_Hot(device):
    ret = True
    try:
        new_user = '1459287460@qq.com'
        # msg=MIMEText('填写邮件内容','plain','utf-8')
        mail_msg = f'<h2><center>IC_Hot</center></h2> 设备: {device} 出现check code'
        msg = MIMEText(mail_msg, 'html', 'utf-8')
        msg['From'] = formataddr(["From IC_hot", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        receives = sendWho(device)
        msg['To'] = ', '.join(receives)
        msg['Subject'] = "IC_Hot"  # 邮件的主题，也可以说是标题
        #  user email
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, receives, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as err:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret


def mail_ip_error(device):
    ret = True
    try:
        # msg=MIMEText('填写邮件内容','plain','utf-8')
        mail_msg = f'<h2><center>Octopart</center></h2> 设备: {device} 出现security check'
        msg = MIMEText(mail_msg, 'html', 'utf-8')
        msg['From'] = formataddr(["octopart security check", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        receives = sendWho("")
        msg['To'] = ', '.join(receives)  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "Octopart"  # 邮件的主题，也可以说是标题
        #  user email
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, receives, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as err:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret


# russian tender
def sendAttachment(result_save_file, theme):
    ret = True
    try:
        # new_user_list = ['river@omni-electronics.com', 'river@szyjcx.cn']
        new_user_list = ['jason@omni-electronics.com', 'tim@omni-electronics.com', 'sofia@omni-electronics.com', 'river@omni-electronics.com']
        mail_msg = f'<h2><center> {theme} </center></h2>'
        mail_content_list = ["Hard work pays off.（努力工作会有回报。）",
        "No pain, no gain.（不劳无获。）",
        "Work hard in silence, let success make the noise.（默默努力，让成功发出声音。）",
        "Жизнь это не конец, а новое начало.(Life is not the end, but a new beginning.)"
        ]
        html = mail_msg + f'{random.choice(mail_content_list)} <br> '
        part1 = MIMEText(html, "html")

        # 将MIMEText对象添加到邮件对象中
        msg = MIMEMultipart()
        msg['From'] = formataddr([f"From {theme}", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = ','.join(new_user_list)  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "rts-tender"  # 邮件的主题，也可以说是标题

        with open(result_save_file, 'rb') as f:
            attachment = MIMEApplication(f.read())
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(result_save_file))
            msg.attach(attachment)
        msg.attach(part1)

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, new_user_list, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as e:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        print(e)
        ret = False
    if ret:
        print("邮件发送成功")
    else:
        print("邮件发送失败")
    return ret


def stock_chang_alert(result_save_file, ppnInfo):
    ret = True
    try:
        new_user_list = ['river@calcitrapa.com']
        mail_msg = f'<h2><center> ppn change check </center></h2>'
        html = mail_msg + f'<div>{ppnInfo}</div>'
        part1 = MIMEText(html, "html")
        # 将MIMEText对象添加到邮件对象中
        msg = MIMEMultipart()
        msg['From'] = formataddr([f"From ppn change check", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = ',\n'.join(new_user_list)  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "风菱库存——IC stock 变化"  # 邮件的主题，也可以说是标题

        with open(result_save_file, 'rb') as f:
            attachment = MIMEApplication(f.read())
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(result_save_file))
            msg.attach(attachment)
        msg.attach(part1)

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, new_user_list, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as e:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        print(e)
        ret = False
    if ret:
        print("邮件发送成功")
    else:
        print("邮件发送失败")
    return ret


if __name__ == '__main__':
    sendAttachment(PathHelp.get_file_path('Tender', 'tender_info_2023-09-12_A.xlsx'), 'Tender_info_A')
    time.sleep(15.0)
    sendAttachment(PathHelp.get_file_path('Tender', 'tender_info_2023-09-12_B.xlsx'), 'Tender_info_B')


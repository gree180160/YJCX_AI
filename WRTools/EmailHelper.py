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
        server.sendmail(my_sender, [my_user], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
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
        server.sendmail(my_sender, [my_user], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
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
        msg['To'] = formataddr(["river", new_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "IC_Stock"  # 邮件的主题，也可以说是标题
        #  user email
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, [new_user], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
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
        msg['To'] = formataddr(["river", new_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "IC_Hot"  # 邮件的主题，也可以说是标题
        #  user email
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465，固定的，不能更改
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.set_debuglevel(1)
        server.sendmail(my_sender, [new_user], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
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
        server.sendmail(my_sender, [new_user], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
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
        "The harder you work, the luckier you get.（你工作越努力，运气就越好。）",
        "Success is the result of hard work, determination, and perseverance.（成功是努力工作、决心和毅力的结果。）",
        "Dream big, work hard, stay focused, and surround yourself with good people.（追求大梦想，努力工作，保持专注，并与优秀的人为伍。）",
        "Work hard, stay humble.（努力工作，保持谦逊。）",
        "The only way to do great work is to love what you do.（做出伟大的工作的唯一途径是热爱自己的工作。）",
        "Success is not the key to happiness. Happiness is the key to success. If you love what you are doing, you will be successful.（成功不是幸福的关键，幸福才是成功的关键。如果你热爱自己所做的事情，你将会成功。）",
        "Don't watch the clock; do what it does. Keep going.（不要盯着时钟看，做时钟所做的事情，继续前进）。",
        "Life is either a daring adventure or nothing at all. - Helen Keller（生活要么是一次大胆的冒险，要么一无所有。）",
        "Live life to the fullest.（活出精彩人生。）",
        "Enjoy the little things in life, for one day you may look back and realize they were the big things.（享受生活中的小事情，因为总有一天你回首过去会发现它们才是最重要的。）",
        "Life is too short to be anything but happy.（生命太短暂，只应追求快乐。）",
        "The purpose of life is not to be happy. It is to be useful, to be honorable, to be compassionate, to have it make some difference that you have lived and lived well. - Ralph Waldo Emerson（生活的目的不是追求快乐，而是有用、光荣、有同情心，并且让你的存在有所不同。）",
        "Life isn't about waiting for the storm to pass, it's about learning to dance in the rain.（生活不是等待风暴过去，而是学会在雨中跳舞。）",
        "Life is 10% what happens to us and 90% how we react to it. - Charles R.Swindoll（生活中有10 % 是我们所发生的事情，90 % 是我们对它们的反应。）",
        "Life is a journey, not a destination. - Ralph Waldo Emerson（生活是一段旅程，而不是一个目的地。）",
        "The best way to predict the future is to create it.（预测未来的最好方式就是创造它。）",
        "Life is like a camera. Focus on the good times, develop from the negatives, and if things don't work out, take another shot.（生活就像一台相机。专注于美好时光，从负面经历中成长，如果事情不顺利，就再拍一张。）",
        "Живи, как будто сегодня твой последний день.(Live as if today is your last day.)",
        "Жизнь дается один раз, поэтому живи ее на полную.(Life is given only once, so live it to the fullest.)",
        "Жизнь полна возможностей, нужно только уметь их видеть.(Life is full of opportunities, we just need to know how to see them.)",
        "Жизнь это не количество вдохов, а количество моментов, которые заставляют сердце замирать.(Life is not about the number of breaths you take, but the moments that take your breath away.)",
        "Жизнь это путешествие, наслаждайся каждым шагом.(Life is a journey, enjoy every step.)",
        "Жизнь это драгоценный дар, не трать его на пустые дела.(Life is a precious gift, don't waste it on empty things.)",
        "Жизнь прекрасна, когда ты делаешь то, что любишь.(Life is beautiful when you do what you love.)",
        "Жизнь это не ожидание, а осуществление мечт.(Life is not about waiting, but about fulfilling dreams.)",
        "Жизнь это то, что происходит, пока ты строишь планы.(Life is what happens while you are making plans.)",
        "Жизнь это не только дождь, но и радуга после него.(Life is not only about the rain, but also about the rainbow after it.)",
        "Жизнь это не проблемы, а уроки, которые помогают нам расти.(Life is not about problems, but lessons that help us grow.)",
        "Жизнь это не ожидание счастья, а создание его самому.(Life is not about waiting for happiness, but creating it yourself.)",
        "Жизнь это не оглядываться назад, а двигаться вперед.(Life is not about looking back, but moving forward.)",
        "Жизнь это не успехи, а опыт, который делает нас сильнее.(Life is not about successes, but the experience that makes us stronger.)",
        "Жизнь это не место, а путешествие.(Life is not a place, but a journey.)",
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


if __name__ == '__main__':
    sendAttachment(PathHelp.get_file_path('Tender', 'tender_info_2023-09-11_A.xlsx'), 'Tender_info_A')
    time.sleep(15.0)
    sendAttachment(PathHelp.get_file_path('Tender', 'tender_info_2023-09-11_B.xlsx'), 'Tender_info_B')


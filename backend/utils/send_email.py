import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(smtp_server, smtp_port, from_email, password, to_list, subject, content, attachment=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = Header("Leo API Auto Test", 'utf-8')
        msg['To'] = ";".join(to_list)
        msg['Subject'] = Header(subject, 'utf-8')
        txt = MIMEText(content, 'html', 'utf-8')
        msg.attach(txt)
        if attachment:
            # 添加附件
            part = MIMEApplication(open(attachment, 'rb').read())
            part.add_header('Content-Disposition', 'attachment', filename=attachment)
            msg.attach(part)

        # 设置服务器、端口
        s = smtplib.SMTP_SSL(smtp_server, int(smtp_port))
        # 登录邮箱
        s.login(from_email, password)
        # 发送邮件
        s.send_message(msg, from_email, to_list)
        s.quit()
        return True, 'email send successfully'
    except smtplib.SMTPException as e:
        return False, 'SMTPException : %s' % str(e)
    except BaseException as e:
        return False, 'Exception : %s' % str(e)


if __name__ == '__main__':
    pass

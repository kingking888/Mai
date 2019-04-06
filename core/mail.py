from email.message import EmailMessage
import smtplib
import os
import logging

def sendmail(spiderName, stats, logPath):
    FROM = os.getenv('email.from')
    TO = os.getenv('email.to')
    # TO = ['to@qq.com']
    passwd = os.getenv('email.passwd')
    if not FROM or not TO or not passwd:
        logging.warning('邮件发送取消：请设置相关环境变量')
        return          
    # 构建邮件体
    msg = EmailMessage()
    msg['Subject'] = f'爬虫 - {spiderName} - 采集情况'
    msg['From'] = FROM
    msg['To'] = TO
    # msg['To'] = ', '.join(TO)
    msg.set_content('\n'.join([f'{k}: {v}' for k, v in stats.items()]))
    # 添加附件
    if os.path.exists(logPath):
        with open(logPath, 'rb') as fp:
            msg.add_attachment(
                fp.read(), 
                maintype='application', 
                subtype='octet-stream',
                filename=os.path.basename(logPath),
                ) 
    # 发送邮件
    with smtplib.SMTP_SSL('smtp.qq.com', 465, timeout=5) as client:
        client.ehlo()
        client.login(FROM, passwd)
        failList = client.sendmail(FROM, TO, msg.as_string())
        if failList:
            logging.warnings(f'无法发送邮件到以下联系人：{failList}')
        else:
            logging.info('邮件发送成功')

if __name__ == "__main__":
    with open('test.txt', 'w', encoding='utf-8') as fp:
        fp.write('send email test')
    stats = {
        'batchId': 'test',
        'total': 1000,
    }
    sendmail(stats, os.path.join('.', 'test.txt'))
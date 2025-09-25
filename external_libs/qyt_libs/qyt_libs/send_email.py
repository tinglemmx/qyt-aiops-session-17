import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import List, Dict
from pathlib import Path

def send_report(
    subject: str,
    sender: str,
    recipients: List[str],
    html_content: str,
    image_files: Dict[str, Path],
    smtp_host: str,
    smtp_port: int = 587,
    username: str = None,
    password: str = None
):
    """
    发送包含 HTML 和嵌入图片的邮件

    :param subject: 邮件主题
    :param sender: 发件人
    :param recipients: 收件人列表
    :param html_content: 渲染好的 HTML 字符串
    :param image_files: CID 对应的图片路径，格式 {"cid_name": Path("xxx.png")}
    :param smtp_host: SMTP 主机
    :param smtp_port: SMTP 端口
    :param username: SMTP 登录用户名
    :param password: SMTP 登录密码
    """
    # 构造邮件主体
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    # HTML 部分
    msg_alt = MIMEMultipart("alternative")
    msg_alt.attach(MIMEText(html_content, "html"))
    msg.attach(msg_alt)

    # 嵌入图片
    for cid, path in image_files.items():
        if not path.exists():
            print(f"[WARNING] 图片文件不存在: {path}")
            continue
        with open(path, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header("Content-ID", f"<{cid}>")  # 对应 HTML 中 cid
            img.add_header("Content-Disposition", "inline", filename=path.name)
            msg.attach(img)

    # 发送邮件
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            if username and password:
                server.login(username, password)
                print("Logged in")
            server.send_message(msg)
    except smtplib.SMTPResponseException as e:
        if e.smtp_code == -1 and e.smtp_error == b'\x00\x00\x00':
            print("邮件已发送，但退出SMTP时收到非标准响应，已忽略")
        else:
            raise

    print("[INFO] 邮件已发送")


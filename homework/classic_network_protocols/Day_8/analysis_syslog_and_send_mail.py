from pathlib import Path
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from SQLiteSyslogServer import Log
import matplotlib.pyplot as plt
from matplotlib import rcParams
from jinja2 import Environment, FileSystemLoader
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import List, Dict

# 指定中文字体文件路径
rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
# 解决坐标轴负号显示问题
rcParams['axes.unicode_minus'] = False


BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
Path.mkdir(REPORTS_DIR, exist_ok=True)
TEMPLATES_DIR = BASE_DIR / "templates"
Path.mkdir(TEMPLATES_DIR, exist_ok=True)
DB_DIR = BASE_DIR / "db"
Path.mkdir(DB_DIR, exist_ok=True)
DB_PATH = DB_DIR / "syslog.db"

DB_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)


def analyze_severity(session):
    total_count = session.query(func.count(Log.id)).scalar()
    severity_counts = (
        session.query(Log.severity, Log.severity_name, func.count(Log.id))
        .group_by(Log.severity)
        .all()
    )
    result = []
    for sev, name, count in severity_counts:
        percent = round(count / total_count * 100, 2)
        result.append({
            "name": name,
            "log_count": count,
            "percent": percent
        })
    return result


def analyze_hosts(session):
    total_count = session.query(func.count(Log.id)).scalar()
    device_counts = (
        session.query(Log.host, func.count(Log.id))
        .group_by(Log.host)
        .all()
    )
    result = []
    for host, count in device_counts:
        percent = round(count / total_count * 100, 2)
        result.append({
            "ip": host,
            "log_count": count,
            "percent": percent
        })
    return result


def generate_pie_chart(data_list, key_label, key_value, filename, title, figsize=(4, 4),):
    labels = [d[key_label] for d in data_list]
    sizes = [d[key_value] for d in data_list]
    plt.figure(figsize=figsize)
    plt.pie(sizes, labels=labels, autopct="%1.1f%%")
    plt.title(title)
    plt.savefig(str(REPORTS_DIR / filename))
    plt.close()


def render_template(template_file, output_file, **context):
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template(template_file)
    rendered_html = template.render(**context)
    file = REPORTS_DIR / output_file
    with open(file, "w", encoding="utf-8") as f:
        f.write(rendered_html)
    return rendered_html


def send_syslog_report(
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


def main():
    severity_level_png_filename = "severity_pie.png"
    device_ip_png_filename = "device_ip_pie.png"
    report_name = "syslog_report_rendered.html"
    with Session() as session:
        severity_data = analyze_severity(session)
        host_data = analyze_hosts(session)

    generate_pie_chart(severity_data, "name", "log_count",
                       "severity_pie.png", 'SYSLOG严重级别分布图')
    generate_pie_chart(host_data, "ip", "log_count",
                       "device_ip_pie.png", "SYSLOG设备分布图")

    rendered_html = render_template(
        "syslog_email.j2",
        report_name,
        severity_level_count_html_list=severity_data,
        device_ip_count_html_list=host_data,
        severity_level_filename=severity_level_png_filename,
        device_ip_filename=device_ip_png_filename
    )
    print("[INFO] 报告生成完成！")
    html_content = rendered_html
    image_files = {
        "severity_pie": REPORTS_DIR / severity_level_png_filename,
        "host_pie": REPORTS_DIR / device_ip_png_filename
    }
     # https://wx.mail.qq.com/list/readtemplate?name=app_intro.html#/agreement/authorizationCode
    send_syslog_report(
        subject="乾颐堂NetDevOps课程Syslog分析",
*sender="**REMOVED***",
recipients=["***REMOVED***"],
        html_content=html_content,
        image_files=image_files,
        smtp_host="smtp.qq.com",
        smtp_port=587,
username="***REMOVED***",
password="***REMOVED***"
    )


if __name__ == "__main__":
    main()

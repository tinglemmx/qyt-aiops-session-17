# 环境搭建

## 概述
本项目已经包含了.vscode/launch.json 如果是vscode的ide可以通过`run and debug`进行运行
支持两种运行方式：
- Run Django with Gunicorn
- Python Debugger: Django

## 快速上手笔记
> 已经操作过了不需要再做一遍了

```
# 新目录
mkdir mysite && cd mysite

# 建虚拟环境并激活
python3 -m venv .venv
source .venv/bin/activate

# 安装 Django
pip install --upgrade pip
pip install django

# 新项目
django-admin startproject mysite .



# 迁移并建管理员
python manage.py migrate
这里会应用一堆的授权
python manage.py createsuperuser   # 按提示输入用户名/邮箱/密码

# 运行开发服务器（本机访问）
python manage.py runserver 127.0.0.1:8000

# 如果想让局域网其他主机访问（注意防火墙）
python manage.py runserver 0.0.0.0:8000

```
## 命令的方式启动服务的方法
gunicorn --bind 0.0.0.0:8000 mysite.wsgi:application --log-level debug
python -u manage.py runserver 0.0.0.0:8000  # -u 表示无缓冲
gunicorn --bind 0.0.0.0:8000 mysite.wsgi:application --worker-class gthread --log-level notification

gunicorn --bind 0.0.0.0:8000 mysite.wsgi:application \
  --worker-class gthread \
  --log-level info \
  --access-logfile -


 ##  uwsgi + NGINX
### 准备工作
安装 uwsgi：
pip install uwsgi

安装 Nginx：
sudo apt install nginx


收集静态文件：
python manage.py collectstatic


 ### uwsgi 的配置文件

 ```shell
❯ cat /home/tingle/myProject/qyt-aiops-session-17/homework/Django/mysite/myproject_uwsgi.ini
[uwsgi]
chdir = /home/tingle/myProject/qyt-aiops-session-17/homework/Django/mysite
module = mysite.wsgi:application

home = /home/tingle/myProject/qyt-aiops-session-17/.venv
static-map = /static=/home/tingle/myProject/qyt-aiops-session-17/homework/Django/mysite/staticfiles

socket = /tmp/myproject.sock
chmod-socket = 666
vacuum = true

master = true
processes = 3
threads = 2

buffer-size = 65535#  
 ```


 ### uwsgi systemd 的服务单元文件

 ```shell 
 ❯ cat /etc/systemd/system/myproject.service
[Unit]
Description=uWSGI service for myproject
After=network.target

[Service]
# 运行用户，推荐不要用 root
User=tingle
Group=tingle

# 启动命令：指定你的 ini 配置
ExecStart=/home/tingle/myProject/qyt-aiops-session-17/.venv/bin/uwsgi \
    --ini /home/tingle/myProject/qyt-aiops-session-17/homework/Django/mysite/myproject_uwsgi.ini

# 建议设置工作目录（你的 Django 项目根目录）
WorkingDirectory=/home/tingle/myProject/qyt-aiops-session-17/homework/Django/mysite

# 确保 systemd 自动重启
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
 ```

 ### NGINX 的配置文件

 ```shell
 root in /etc/nginx/sites-available 
❯ cat myproject 
server {
    listen 80;
    server_name djg.mingjiao.org;

    # 静态文件
    location /static/ {
        alias /home/tingle/myProject/qyt-aiops-session-17/homework/Django/mysite/staticfiles/;
    }

    # 媒体文件（可选）
    location /media/ {
        alias /home/tingle/myProject/qyt-aiops-session-17/homework/Django/mysite/media/;
    }

    # 反向代理到 uWSGI
    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/myproject.sock;
    }
}
```

###启动命令
```shell
sudo systemctl start myproject.service 
sudo systemctl status myproject.service 
sudo nginx -t 
sudo systemctl start nginx
sudo systemctl status nginx 
```

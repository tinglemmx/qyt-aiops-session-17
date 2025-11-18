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
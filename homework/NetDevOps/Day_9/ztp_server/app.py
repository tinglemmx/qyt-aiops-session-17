#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Simple ZTP server for lab:
- /download/<filename>  -> 提供设备端脚本下载
- /ztp/get_config       -> POST: 设备上报 { "uuid": "...", "model": "C8000v" } 返回渲染后的 CLI 文本
- device configs in device_config.yaml keyed by UUID
"""
from flask import Flask, request, send_from_directory, jsonify
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import yaml

BASE = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE / "templates"
STATIC_DIR = BASE / "static"
CONFIG_DIR = BASE / "configs"

app = Flask(__name__)
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

def load_db():
    data_file = CONFIG_DIR / "device_config.yaml"
    if not data_file.exists():
        return {}
    with open(data_file, "r") as f:
        return yaml.safe_load(f) or {}

@app.route("/download/<path:filename>")
def download(filename):
    return send_from_directory(str(STATIC_DIR), filename, as_attachment=False)

@app.route("/ztp/get_config", methods=["POST"])
def get_config():
    """
    设备上报 JSON: {"uuid": "...", "model": "C8000v"}
    返回: {"status":"ok","config":"...cli commands..."}
    """
    data = request.get_json(force=True)
    if not data:
        return jsonify({"status":"error","msg":"no json"}), 400
    else:
        print(data)

    uuid = data.get("uuid")
    model = data.get("model", "")

    if not uuid:
        return jsonify({"status":"error","msg":"no uuid"}), 400

    db = load_db()
    dev = db.get(uuid)
    print("Device data:", dev)
    if not dev:
        # 可选择基于 model 动态生成，也可以直接返回 404
        return jsonify({"status":"error","msg":"device not found"}), 404

    # 选择模板：优先按 model 小写文件名找模板
    if model == dev.get('model','generic'):
        tpl_name = f"{model}.j2"
    else:
        return jsonify({"status":"error","msg":f"device model {model} not found"}), 404
    try:
        tpl = env.get_template(tpl_name)
    except Exception as e:
        return jsonify({"status":"error","msg":f"template {tpl_name} not found"}), 500

    rendered = tpl.render(**dev)
    print("rendered:",rendered)
    return jsonify({"status":"ok","config": rendered})

if __name__ == "__main__":
    # 开发环境直接启动
    # app.run(host="0.0.0.0", port=8000)
        # 使用 Gunicorn 内嵌启动 Flask
    from gunicorn.app.base import BaseApplication

    class FlaskApplication(BaseApplication):
        def __init__(self, app, options=None):
            self.application = app
            self.options = options or {}
            super().__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items()
                      if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        "bind": "0.0.0.0:8000",
        "workers": 2,   # 根据 CPU 核心数调整
        "threads": 2,
        "accesslog": "-",  # 控制台输出访问日志
        "errorlog": "-",   # 控制台输出错误日志
    }

    FlaskApplication(app, options).run()

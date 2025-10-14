import importlib
from pathlib import Path
from flask import Flask, jsonify
from flask_jsonrpc import JSONRPC
from inspect import signature, _empty
import inspect

app = Flask(__name__)
jsonrpc = JSONRPC(app, '/api')


@app.route("/robots.txt")
def robots():
    return "", 200, {"Content-Type": "text/plain"}


def has_type_annotations(func) -> bool:
    """检查函数是否所有参数和返回值都有类型注解"""
    sig = signature(func)
    for param in sig.parameters.values():
        if param.annotation is _empty:
            return False
    return sig.return_annotation is not _empty


def load_rpc_functions() -> list[tuple[str, str, callable]]:
    """扫描 rpc_methods 下所有函数，返回 [(module_name, func_name, func)]"""
    rpc_dir = Path(__file__).parent / 'rpc_methods'
    funcs = []

    for py_file in rpc_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        module_name = py_file.stem
        module = importlib.import_module(f"rpc_methods.{module_name}")

        for attr_name in dir(module):
            func = getattr(module, attr_name)
            if inspect.isfunction(func) and not attr_name.startswith("_"):
                funcs.append((module_name, attr_name, func))
    return funcs


# 注册 JSON-RPC 方法
for module_name, func_name, func in load_rpc_functions():
    if has_type_annotations(func):
        jsonrpc.method(f"{module_name}.{func_name}")(func)
    else:
        print(f"Skipped {module_name}.{func_name}, missing type annotations")

# Web API 预览


@app.route('/api', methods=['GET'])
def index():
    funcs = load_rpc_functions()
    return jsonify({
        "service": "JSON-RPC Server",
        "available_methods": [
            f"{m}.{f}" for m, f, _ in funcs
        ]
    })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

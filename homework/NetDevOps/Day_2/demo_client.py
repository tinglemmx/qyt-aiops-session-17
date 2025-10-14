import requests
import itertools
import base64
from pathlib import Path


server_ip = "172.17.102.12"
server_port = 5000
url = f"http://{server_ip}:{server_port}/api"
base_dir = Path(__file__).parent

# 自动生成请求 id
_request_id = itertools.count(1)

def jsonrpc_call(url: str, method: str, params: dict = None, timeout: float = 10):
    """
    通用 JSON-RPC 调用函数

    :param url: JSON-RPC 服务器 URL
    :param method: 要调用的 RPC 方法名
    :param params: dict 或 list，RPC 方法参数
    :param timeout: 请求超时时间（秒）
    :return: RPC 返回结果
    :raises Exception: 如果 RPC 返回 error，会抛出异常
    """
    rpc_id = next(_request_id)
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": rpc_id
    }
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        # resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to connect to {url}: {e}")

    data = resp.json()
    if "error" in data:
        return data
    return data.get("result")

def json_rpc_client_exec_cmd(cmd):
    """
    执行命令
    :param cmd:
    :return:
    """
    result = jsonrpc_call(url, "cmd_ops.run", cmd)
    if result.get('error'):
        data = result['error']
        if isinstance(data , dict) and data.get('data'):
            return data['data']['message']
        return data
    elif result.get('returncode') != '0':
        return f"Error executing command: {result['stderr']}"
    return result['stdout']

def json_rpc_client_upload(filename):
    params = {
        "filename": filename,
        "content_b64": get_content_b64(filename)
    }
    result = jsonrpc_call(url, "file_ops.upload", params)
    if result.get('error'):
        data = result['error']
        if isinstance(data , dict) and data.get('data'):
            return data['data']['message']
        return data
    return result

def json_rpc_client_download(filename):
    params = {
        "filename": filename
    }
    result = jsonrpc_call(url, "file_ops.download", params)
    
    if result.get('error'):
        data = result['error']
        if isinstance(data, dict) and data.get('data'):
            return data['data']['message']  # 返回错误信息
        return data  # 返回其他错误
    
    if result.get('content_b64'):
        file_path = base_dir / filename
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(result['content_b64']))
        print(result.get('message'))
    else:
        print(result.get('message'))
    return None

def get_content_b64(filename: str) -> str:
    file = base_dir / filename
    with open(file, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode("utf-8")
    return content_b64


if __name__ == "__main__":
    exec_cmd = {'cmd': 'ifconfig'}
    print(json_rpc_client_exec_cmd(exec_cmd))
    exec_cmd = {'cmd': 'pwd1'}
    print(json_rpc_client_exec_cmd(exec_cmd))
    exec_cmd = {'cmd1': 'pwd'}
    print(json_rpc_client_exec_cmd(exec_cmd))
    print(json_rpc_client_upload('logo.jpg'))
    json_rpc_client_download('logo.png')
    json_rpc_client_download('logo1.png')
    


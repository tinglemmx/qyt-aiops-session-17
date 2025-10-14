# rpc_methods/file_ops.py
from typing import Dict
import base64
from pathlib import Path

UPLOAD_DIR = Path("/tmp/jsonrpc_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def upload(filename: str, content_b64: str) -> Dict[str, str]:
    """
    上传文件
    filename: 保存文件名
    content_b64: base64 编码的文件内容
    """
    file_path = UPLOAD_DIR / filename
    with file_path.open("wb") as f:
        f.write(base64.b64decode(content_b64))
    return {"status": "ok", "message": f"{filename} upload success" , "path": str(file_path)}

def download(filename: str) -> Dict[str, str]:
    """
    下载文件
    返回 Base64 编码内容
    """
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        return {"status": "error", "message": f"download file {filename} not exist"}
    with file_path.open("rb") as f:
        content_b64 = base64.b64encode(f.read()).decode("utf-8")
    return {"status": "ok", "message": f"{filename} download success" ,"content_b64": content_b64}

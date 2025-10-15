from fastapi import FastAPI, HTTPException
from typing import Union
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum
from pathlib import Path
import subprocess
import base64
import zlib

# 请求数据模型
class CommandRequest(BaseModel):
    command: str  # 要执行的命令

# 返回数据模型
class CommandResponse(BaseModel):
    command: str
    output: str
    cmd_result_base64: str = Field(title='命令输出的Base64编码')
    returncode: int

# POST时间的两种类型
class TimeType(str, Enum):
    datetime = 'datetime'
    date = 'date'


# 推送执行时间查询的数据类型
class PostTimeRPC(BaseModel):
    # "..." 表示必填
    time_type: TimeType = Field(...,
                                title='查询时间的类型, 支持 datetime和date两种选项')


# 返回执行时间查询的数据类型
class ReturnTimeRPC(BaseModel):
    # "..." 表示必填
    time_type: TimeType = Field(...,
                                title='查询时间的类型, 支持 datetime和date两种选项')
    result: str = Field(title='时间查询结果')


# Hello返回消息的数据类型
class HelloMessage(BaseModel):
    message: str = Field(title='Hello的返回消息')


# 创建FastAPI实例
app = FastAPI()


# 首页
@app.get("/",
         response_model=HelloMessage,  # Hello消息的返回的数据类型
         summary='首页摘要',
         description='首页描述')
async def root():
    return HelloMessage(message="Hello World")

@app.post("/run_command", response_model=CommandResponse)
async def run_command(req: CommandRequest):
    cmd = req.command.strip()
    try:
        # 执行命令，捕获 stdout/stderr
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        output = result.stdout + result.stderr
        compressed = zlib.compress(output.encode("utf-8"))
        return CommandResponse(command=cmd, 
                               output=output, 
                               cmd_result_base64=base64.b64encode(compressed).decode("utf-8"),
                               returncode=result.returncode)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Command timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# 动态路由测试
@app.get("/hello/{name}",
         response_model=HelloMessage,  # Hello消息的返回的数据类型
         summary='Hello摘要',
         description='Hello描述')
async def say_hello(name: str):
    return HelloMessage(message=f"Hello {name}")


# 执行功能
@app.post("/time_rpc",
          response_model=ReturnTimeRPC,  # 返回的数据类型
          summary='执行时间查询功能的摘要',
          description='执行时间查询功能的描述, 支持 datetime和date两种选项')
async def function(post_time_rpc: PostTimeRPC):  # 接收的数据类型 PostTimeRPC
    # PostTimeRPC: {'time_type': 'datetime'}
    time_type = post_time_rpc.time_type
    if time_type == 'datetime':
        # ReturnTimeRPC: {'time_type': 'datetime', 'result':"格式化的时间"}
        return ReturnTimeRPC(time_type=time_type, result=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    elif time_type == 'date':
        return ReturnTimeRPC(time_type=time_type, result=date.today().strftime('%Y-%m-%d'))
    else:
        # 如果接收到不支持的 time_type，抛出 HTTPException
        raise HTTPException(status_code=422, detail='time type not found!')


if __name__ == "__main__":
    import uvicorn
    base_dir = Path(__file__).parent.parent / "certs"
    server_crt = base_dir / "server.crt"
    server_key = base_dir / "server.key"
    cat_crt = base_dir / "myCA.pem"
    uvicorn.run("main:app", 
                host="0.0.0.0", 
                port=8443,
                ssl_certfile=server_crt,
                ssl_keyfile=server_key,
                ssl_ca_certs=cat_crt,
                ssl_cert_reqs=2,
                reload=True
                )

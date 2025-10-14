import subprocess
from typing import List, Optional, Dict, Union
import shlex


def run(cmd: Union[str, List[str]], timeout: Optional[int] = 5) -> Dict[str, str]:
    """
    安全执行 Linux 命令（不使用 shell），返回 stdout/stderr。
    示例: cmd_ops.run(["ls", "-l"])
    """
    if isinstance(cmd, str):
        # 将字符串拆成安全的参数列表
        cmd_list = shlex.split(cmd)
    elif isinstance(cmd, list):
        cmd_list = cmd
    else:
        raise ValueError("cmd must be a string or list of strings")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,   # ✅ 禁用 shell 以防注入
        )
        return {
            "returncode":  str(result.returncode),
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Command timeout after {timeout}s"}
    except FileNotFoundError:
        return {"error": f"Command not found: {cmd}"}
    except Exception as e:
        return {"error": str(e)}

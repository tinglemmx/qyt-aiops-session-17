from datetime import datetime, timedelta
import pathlib

def get_x_days_ago(days: int) -> object:
    target_date = datetime.now() - timedelta(days=days)
    return target_date

def save_time_to_file(time_str: str,file_prefix:str) -> None:
    script_dir = pathlib.Path(__file__).resolve().parent
    time_tag = time_str.strftime("%Y-%m-%d_%H-%M-%S")
    file = script_dir / f"{file_prefix}_{time_tag}.txt"
    pathlib.Path(file).write_text(str(time_str), encoding="utf-8")
    print(f"已将 {time_str} 写入文件 {file}")

if __name__ == "__main__":
    five_days_ago_obj = get_x_days_ago(5)
    file_prefix = "save_fivedayago_time"
    save_time_to_file(five_days_ago_obj,file_prefix)
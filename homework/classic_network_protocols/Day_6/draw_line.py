import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib import dates, ticker
from pathlib import Path
from sqlalchemy import create_engine, select, Table, MetaData
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
import pandas as pd
from random import choice

# 指定中文字体文件路径
rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
# 解决坐标轴负号显示问题
rcParams['axes.unicode_minus'] = False


base_dir = Path(__file__).resolve().parent
base_dir.mkdir(parents=True, exist_ok=True)
db_path = base_dir / 'db' / "interface_info.db"
engine = create_engine(
    f'sqlite:///{str(db_path)}?check_same_thread=False', echo=False)
Session = sessionmaker(bind=engine)
metadata = MetaData()
metadata.reflect(bind=engine)
router_monitor = metadata.tables['router_monitor']


def get_bandwidth_df(session, table, since_minutes=61, max_gap_seconds=90):
    """
    查询 router_monitor 表最近指定分钟的数据，并计算接口带宽。

    :param session: SQLAlchemy session
    :param table: SQLAlchemy Table 对象
    :param since_minutes: 查询的时间范围，默认 61 分钟
    :param max_gap_seconds: 当 diff_time 超过此值认为数据缺失，bps 置为 NaN
    :return: DataFrame，包含时间、设备、接口、in/out bytes、bps
    """
    one_hour_ago = datetime.now(timezone.utc) - \
        timedelta(minutes=since_minutes)

    stmt = (
        select(table)
        .where(table.c.record_datetime >= one_hour_ago)
        .order_by(table.c.device_ip, table.c.interface_name, table.c.record_datetime)
    )

    rows = session.execute(stmt).fetchall()

    # 转 DataFrame
    df = pd.DataFrame([{
        'time': row.record_datetime,
        'device_ip': row.device_ip,
        'interface_name': row.interface_name,
        'in_bytes': row.in_bytes,
        'out_bytes': row.out_bytes
    } for row in rows])
    df['time'] = pd.to_datetime(df['time'], utc=True)
    df['time_local'] = df['time'].dt.tz_convert('Asia/Shanghai')
    df['is_virtual'] = False

    # 按设备+接口排序
    df.sort_values(['device_ip', 'interface_name', 'time_local'], inplace=True)

    # 标记最早一个时间点 这个是用于计算的过程数据 最后的值需要过滤掉它
    for (dev, iface), group in df.groupby(['device_ip', 'interface_name']):
        last_idx = group.index[0]
        df.loc[last_idx, 'is_virtual'] = True

    # 计算差值
    df[['diff_in_bytes', 'diff_out_bytes', 'diff_time_local']] = df.groupby(['device_ip', 'interface_name'], group_keys=False) \
        .apply(lambda g: pd.DataFrame({
            'diff_in_bytes': g['in_bytes'].diff(),
            'diff_out_bytes': g['out_bytes'].diff(),
            'diff_time_local': g['time_local'].diff().dt.total_seconds()
        }))

    # 计算带宽 bps
    df['bps_in'] = (df['diff_in_bytes'] * 8 / 1000 / df['diff_time_local']
                    ).where(df['diff_time_local'] <= max_gap_seconds)
    df['bps_out'] = (df['diff_out_bytes'] * 8 / 1000 / df['diff_time_local']
                     ).where(df['diff_time_local'] <= max_gap_seconds)

    return df


def prepare_plot_data(df, direction='rx'):
    """
    将 DataFrame 转换为画图用的字典

    :param df: DataFrame，包含 'device_ip', 'interface_name', 'time_local', 'bps_in', 'bps_out'
    :param direction: 'rx' 或 'tx'
    :return: dict，每个 key 对应一条折线的 label，value 包含 x/y/line_style/color
    """
    from matplotlib import pyplot as plt

    line_styles = ['-', '--', '-.', ':']
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

    df_plot = df[df['is_virtual'] != True].copy()

    if direction == 'rx':
        df_plot['label'] = "RX:" + df_plot['device_ip'] + \
            ":" + df_plot['interface_name']
        y_col = 'bps_in'
    elif direction == 'tx':
        df_plot['label'] = "TX:" + df_plot['device_ip'] + \
            ":" + df_plot['interface_name']
        y_col = 'bps_out'
    else:
        raise ValueError("direction must be 'rx' or 'tx'")

    plot_data = {}
    for label, group in df_plot.groupby('label'):
        plot_data[label] = {
            'x': group['time_local'].tolist(),
            'y': group[y_col].tolist(),
            'line_style': choice(line_styles),
            'color': choice(colors),
        }

    return plot_data


def draw_line_chart(
    plot_data,
    x_label: str,
    y_label: str,
    title: str = "折线图"
):
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    fig.autofmt_xdate()

    for label, line_info in plot_data.items():
        ax.plot(line_info['x'], line_info['y'],
                # line_info['line_style'],
                # color=line_info['color'],
                label=label)

    ax.legend(loc='upper left')

    # plt.show()
    # 保存图片
    file = base_dir / f'{title}.png'
    plt.savefig(str(base_dir / file))


if __name__ == '__main__':
    with Session() as session:
        df = get_bandwidth_df(session, router_monitor, since_minutes=61)
    print(df.tail(20))
    lines_data = prepare_plot_data(df, direction='rx')
    draw_line_chart(lines_data, x_label='Time', y_label='kbps', title='入向速率')
    lines_data = prepare_plot_data(df, direction='tx')
    draw_line_chart(lines_data, x_label='Time', y_label='kbps', title='出向速率')

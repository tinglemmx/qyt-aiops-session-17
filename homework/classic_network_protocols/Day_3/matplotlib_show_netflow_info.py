import matplotlib.pyplot as plt
import re
from matplotlib import rcParams
from qyt_libs.qytang_ssh import qytang_ssh


# 指定中文字体文件路径
rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
# 解决坐标轴负号显示问题
rcParams['axes.unicode_minus'] = False

def get_netflow_info():
    result = qytang_ssh('192.168.76.130', 'admin', 'Cisco@1234',cmd = 'show flow monitor name qytang-monitor cach format table')
    print("get netflow info success")
    print(result)
    netflow_info = {}
    pattern = re.compile(r'^(.+?)\s+(\d+)$')
    start_record = False
    for line in result.split('\n'):
        tmp_line = line.strip()
        if tmp_line and "========" not in tmp_line:
            if start_record:
                match = pattern.match(tmp_line)
                if match:
                    netflow_info.update({match.group(1):int(match.group(2))})
            if tmp_line.startswith('APP NAME'):
                start_record = True
    return netflow_info
            
def draw_pie(labels, sizes, title="饼图", figsize=(7,5), shadow=True, colors=None):

    plt.figure(figsize=figsize)
    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        shadow=shadow,
        colors=colors
    )
    
    plt.title(title,pad=30)
    
    plt.legend(
        wedges, labels,
        loc="lower left",
    )
    
    plt.axis("equal")  
    plt.tight_layout() 
    plt.show()


if __name__ == '__main__':
    result = get_netflow_info()
    labels = list(result.keys())
    sizes = list(result.values())
    draw_pie(labels, sizes, title="第三天作业Netflow")
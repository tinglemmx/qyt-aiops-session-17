import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib import dates,ticker
from datetime import datetime,timedelta
from random import random,choice

# 指定中文字体文件路径
rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
# 解决坐标轴负号显示问题
rcParams['axes.unicode_minus'] = False

def draw_line_chart(
                   line_list:list,
                   x_label:str,
                   y_label:str,
                   title:str="折线图"
                   ):
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.xaxis.set_major_formatter(dates.DateFormatter( "%H:%M"))
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%3.1f%%"))
    ax.set_ylim(ymin=0, ymax=100)
    
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    
    fig.autofmt_xdate()
    
    for x_list,y_list,line_style,color,line_name in lines_list:
        ax.plot(x_list, y_list, line_style, color=color, label=line_name)

    ax.legend(loc='upper left')
    
    plt.show()
    
if  __name__ == "__main__":
    title = "CPU利用率"
    x_label = "时间"
    y_label = "利用率(%)"
    line_no = 4
    data_points_count = 10
    colors = ["#FF9999","#FFCC66","#99CC99","#66CCCC"]
    line_style_list = ["-","--","-.",":"]
    now = datetime.now()
    lines_list = []
    for line in range(line_no):
        line_name = f"line{line+1}"
        x_list = [now + timedelta(minutes=i) for i in range(data_points_count)]
        y_list = [random()*100 for i in range(data_points_count)]
        lines_list.append((x_list,y_list,choice(line_style_list),choice(colors),line_name))
    draw_line_chart(lines_list,x_label,y_label,title)
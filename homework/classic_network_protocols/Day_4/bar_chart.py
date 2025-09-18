import matplotlib.pyplot as plt
from matplotlib import rcParams,font_manager
from pathlib import Path

base_dir = Path(__file__).parent

# 指定中文字体文件路径
rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
# 解决坐标轴负号显示问题
rcParams['axes.unicode_minus'] = False


def draw_bar_chart(
                   x_list:list, 
                   y_list:list,
                   x_label:str,
                   y_label:str,
                   title:str="柱状图",
                   color_list:list=None
                   ):
    plt.figure(figsize=(10, 6))   # 宽高
    # 画柱状图
    # plt.barh(x_list, y_list,height=0.5,color=color_list)
    plt.bar(x_list, y_list,width=0.5,color=color_list)

    # 添加标题和坐标轴标签
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    # 保存图片
    plt.savefig(str(base_dir / "result1.png"))
    # 显示图表
    plt.show()

    
if __name__ == '__main__':
    month_list = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月']
    count_list = [123, 555, 354, 888, 666, 777, 999, 1000]
    bar_name = "2025销售状况"
    x_label= '月份'
    y_label= '销售额(万元)'
    colors = ['#FF9999', '#FFCC66', '#99CC99', '#66CCCC', '#FF99FF', '#CCFF99', '#9999FF', '#FFCCCC']
    draw_bar_chart(month_list,count_list,x_label,y_label,bar_name,colors)
import matplotlib.pyplot as plt
from matplotlib import rcParams,font_manager
from matplotlib.font_manager import FontProperties,FontManager


# my_font = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
# font_manager.fontManager.addfont(my_font)

print(sorted(font_manager.get_font_names()))

# 指定中文字体文件路径
rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
# 解决坐标轴负号显示问题
rcParams['axes.unicode_minus'] = False

# --- 数据 ---
sizes = [30, 20, 25, 25]
labels = ["苹果", "香蕉", "橘子", "梨子"]
colors = ["#FF9999","#FFCC66","#99CC99","#66CCCC"]  # 可选配色
explode = (0.05, 0.05, 0.05, 0.05)  # 每块稍微分离一点

# --- 绘制饼图 ---
fig, ax = plt.subplots()
wedges, texts, autotexts = ax.pie(
    sizes,
    labels=labels,
    autopct="%1.1f%%",
    startangle=90,
    shadow=True,
    colors=colors,
    explode=explode,
)

# --- 标题和图例 ---
plt.title("水果销量占比",  fontsize=16)
ax.legend(
    wedges, 
    labels, 
    title="水果",    
    loc="upper left", 
    bbox_to_anchor=(-0.1,1), 
    )

# 保证饼图是圆形
ax.axis("equal")

# --- 显示 ---
plt.show()
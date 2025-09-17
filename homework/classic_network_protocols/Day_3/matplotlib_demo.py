import matplotlib.pyplot as plt

# 设置中文字体和负号正常显示
plt.rcParams['font.sans-serif'] = ['SimHei']   # 黑体
plt.rcParams['axes.unicode_minus'] = False

# 数据
sizes = [30, 20, 25, 25]
labels = ["苹果", "香蕉", "橘子", "梨子"]

# 画饼图
plt.pie(
    sizes,
    labels=labels,
    autopct="%1.1f%%",   # 百分比格式
    startangle=90,       # 起始角度
    shadow=True          # 阴影效果
)

plt.title("水果销量占比")
plt.axis("equal")  # 保证是圆形
plt.show()

from PIL import Image
import pandas as pd
import numpy as np

# 加载图像
image = Image.open(r'G:\blender\output\WALL2\o1\real_shadow0007.png')

# 将图像转换为RGBA模式，以便处理透明度通道
image = image.convert('RGBA')

# 获取图像的像素数据
pixels = image.load()

# 创建一个空的DataFrame来保存RGBA值
rows, cols = image.size
data = np.empty((rows, cols), dtype=object)

# 遍历图像的每个像素
for i in range(rows):
    for j in range(cols):
        # 获取当前像素的RGBA值
        r, g, b, a = pixels[i, j]  # 修改这里的像素访问索引

        # 保存RGBA值
        data[i, j] = f'{(r, g, b, a)}'

# 创建DataFrame
df = pd.DataFrame(data)

# 保存结果为CSV文件
df.to_csv(r'G:\blender\output\WALL2\o1\real_shadow0007.csv', index=False, header=False)
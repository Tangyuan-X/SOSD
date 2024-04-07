from PIL import Image
import os

def getIndexObj(foreground,index,outputUrl):
    # 将图像转换为RGBA模式，以便处理透明度通道
    foreground = foreground.convert('RGBA')

    # 获取图像的像素数据
    # 获取图像的像素数据
    pixels = foreground.load()
    threshold = 0.1

    # 遍历图像的每个像素
    for i in range(foreground.width):
        for j in range(foreground.height):
            # 获取当前像素的RGBA值
            r, g, b, a = pixels[i, j]
            # 接近红色的不变，其他变为透明
            if r > 200 and g < 100 and b < 100:
                pixels[i, j] = (r, g, b, a)
            else:
                pixels[i, j] = (0, 0, 0, 0)
    # 保存结果
    foreground.save(outputUrl + os.sep +f'IndexObj{index:04d}.png')
    return foreground
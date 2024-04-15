from PIL import Image
import colorsys
import os


# 导出阴影
def getShadow(foreground, index, outputUrl, filename="shadow_soft_mask"):
    # 将图像转换为RGBA模式，以便处理透明度通道
    foreground = foreground.convert('RGBA')
    # 获取图像的像素数据
    # 获取图像的像素数据
    pixels = foreground.load()

#     遍历图像的每个像素
#    for i in range(foreground.width):
#        for j in range(foreground.height):
#             获取当前像素的RGBA值
#            r, g, b, a = pixels[i, j]
#             的不变，其他变为透明
#            if r > 200 and g < 100 and b < 100:
#                pixels[i, j] = (0, 0, 0, 0)
#             其他不变
    # 保存结果
    foreground.save(outputUrl + os.sep + filename + f'{index:04d}.png')
    return foreground

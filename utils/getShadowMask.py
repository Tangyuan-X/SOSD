from PIL import Image
import colorsys
import os


# 导出阴影
def getShadowMask(foreground, index, outputUrl, filename="shadow_mask"):
    # 将图像转换为RGBA模式，以便处理透明度通道
    foreground = foreground.convert('RGBA')
    # 获取图像的像素数据
    # 获取图像的像素数据
    pixels = foreground.load()

    # 遍历图像的每个像素
    for i in range(foreground.width):
        for j in range(foreground.height):
            # 获取当前像素的RGBA值
            r, g, b, a = pixels[i, j]
            # 的不变，其他变为透明
            if a <= 6 or (r > 2 and g > 2 and b > 2):
                pixels[i, j] = (0, 0, 0, 0)
            # 其他变为绿色
            else:
                pixels[i, j] = (0, 255, 0, 255)

    ret = foreground.copy()
    ret = ret.convert('RGBA')
    ret_pixels = ret.load()
    delta = [0, 1, -1]
    w = ret.width
    h = ret.height
    for i in range(w):
        for j in range(h):
            cnt = 0
            for di in delta:
                for dj in delta:
                    if j + dj < 0 or j + dj >= h or i + di < 0 or i + di >= w:
                        continue
                    r, g, b, a = pixels[i+di, j+dj]
                    if g == 255:
                        cnt += 1
            if cnt < 3:
                ret_pixels[i, j] = (0, 0, 0, 0)

    # 保存结果
    ret.save(outputUrl + os.sep + filename + f'{index:04d}.png')
    return ret

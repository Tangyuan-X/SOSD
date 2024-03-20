from PIL import Image
import colorsys


# 导出阴影
def getShadowMask(foreground, index, outputUrl):
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
            if (r > 200 and g < 100 and b < 100) or (a <= 3 and (r <= 2 and g <= 2 and b <= 2)):
                pixels[i, j] = (0, 0, 0, 0)
            # 其他变为绿色
            else:
                pixels[i, j] = (0, 255, 0, 255)
    # 保存结果
    foreground.save(outputUrl + f'\\shadow_mask{index:04d}.png')
    return foreground

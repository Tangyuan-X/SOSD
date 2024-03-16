from PIL import Image
import colorsys

# 导出阴影
def getShadow(foreground,index,outputUrl):
    # 将图像转换为RGBA模式，以便处理透明度通道
    foreground = foreground.convert('RGBA')
    # 获取图像的像素数据
    # 获取图像的像素数据
    pixels = foreground.load()
    threshold = 5

    # 遍历图像的每个像素
    for i in range(foreground.width):
        for j in range(foreground.height):
            # 获取当前像素的RGBA值
            r, g, b, a = pixels[i, j]
            # 的不变，其他变为透明
            if 206-threshold < r < 206+threshold and 206-threshold < g < 206+threshold and 206-threshold < b < 206+threshold:
                pixels[i, j] = (0, 0, 0, 0)
            # 其他变为绿色
            else:
                pixels[i, j] = (0, 255, 0, a)
    # 保存结果
    foreground.save(outputUrl + f'\\shadow{index:04d}.png')
    return foreground

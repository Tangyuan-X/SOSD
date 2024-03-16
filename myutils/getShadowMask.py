from PIL import Image
import colorsys


# 导出阴影
def getShadowMask(shadowCache, realShadow, index, outputUrl):
    # 将图像转换为RGBA模式，以便处理透明度通道
    shadowCache = shadowCache.convert('RGBA')
    realShadow = realShadow.convert('RGBA')
    # 将shadowCache中不是206的像素在realShadow中变为透明
    pixels = shadowCache.load()
    pixels2 = realShadow.load()
    threshold = 3
    # 遍历图像的每个像素
    for i in range(shadowCache.width):
        for j in range(shadowCache.height):
            # 获取当前像素的RGBA值
            r, g, b, a = pixels[i, j]
            # 的不变，其他变为透明
            if 206 - threshold < r < 206 + threshold and 206 - threshold < g < 206 + threshold and 206 - threshold < b < 206 + threshold:
                pixels2[i, j] = (206, 206, 206, a)
    # 保存结果
    realShadow.save(outputUrl + f'\\real_shadow{index:04d}.png')
    return realShadow

# if __name__ == '__main__':
#     IndexObj = Image.open(r'G:\blender\output\WALL2\IndexObj0011.png')
#     realShadow = Image.open(r'G:\blender\output\WALL2\real_shadow0012.png')
#     getShadowMask(IndexObj, realShadow, 1)

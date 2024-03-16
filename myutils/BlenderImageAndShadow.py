import os

from PIL import Image
import getShadow as gs
import getIndexObj as gi
import getShadowMask as gsm
import IntegrateResult as ir
def HandleResult(baseUrl, outputUrl):
    if not os.path.exists(outputUrl):
        os.makedirs(outputUrl)

    # 得到所有baseUrl下的png文件个数
    pngNum = len([lists for lists in os.listdir(baseUrl) if os.path.isfile(os.path.join(baseUrl, lists))])
    # 帧长度
    index = 2
    frameLength = pngNum / 4 - 1
    while (index < frameLength):
        # 打开背景图
        background = Image.open(baseUrl + f'\Image{index:04d}.png')
        # background = Image.open(f'../../../blender/output/WALL2/阴影捕捉0000.png')
        # 打开阴影
        shadow = Image.open(baseUrl + f'\阴影捕捉{index + 1:04d}.png')
        new_shadow = gs.getShadow(shadow, index, outputUrl)
        # 打开id
        id = Image.open(baseUrl + f'\IndexObj{index:04d}.png')
        new_id = gi.getIndexObj(id, index, outputUrl)

        # 确保上层图片和背景图片具有相同的尺寸
        foreground = background.copy()
        new_id = id.resize(background.size)

        # 创建一个新的图像，将背景图作为底图
        overlay = foreground.copy()
        # 将阴影图蓝色的部分叠加到背景图上
        overlay = Image.alpha_composite(overlay, new_shadow)
        # 将id图红色的部分叠加到背景图上
        overlay = Image.alpha_composite(overlay, new_id)

        # 获取软阴影
        real_shadow = Image.open(baseUrl + f'\\real_shadow{index + 2:04d}.png')
        realShadow = gsm.getShadowMask(shadow, real_shadow, index, outputUrl)
        # 保存结果
        overlay.save(outputUrl + f'\\result{index:04d}.png')
        index += 4
        # 关闭图像
        background.close()
        shadow.close()
        id.close()
        overlay.close()
        real_shadow.close()
        realShadow.close()

    # 将得到所有baseUrl路径下的png文件移动到outputUrl下的origin文件夹中
    if not os.path.exists(outputUrl + '\\origin'):
        os.makedirs(outputUrl + '\\origin')
    lists = os.listdir(baseUrl)
    for i in lists:
        if i.endswith('.png'):
            oldPath = os.path.join(baseUrl, i)
            newPath = os.path.join(outputUrl + '\\origin', i)
            os.rename(oldPath, newPath)
    ir.integrateResult(outputUrl)
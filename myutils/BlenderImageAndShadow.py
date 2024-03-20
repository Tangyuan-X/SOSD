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
    pngNum = len([lists for lists in os.listdir(baseUrl) if
                  os.path.isfile(os.path.join(baseUrl, lists)) and os.path.join(baseUrl, lists).endswith('.png')])
    # 帧长度
    index = 2
    frameLength = pngNum // 3 - 1
    print("###########frame length:", frameLength)
    while (index <= frameLength):
        # 打开背景图
        background = Image.open(baseUrl + f'\Image{index:04d}.png')
        # 打开id
        id_shadow = Image.open(baseUrl + f'\IndexObj{index + 1:04d}.png')
        id = gi.getIndexObj(id_shadow.copy(), index, outputUrl)
        # 打开阴影mask
        shadow_mask = gsm.getShadowMask(id_shadow.copy(), index, outputUrl)
        # 获取阴影
        realShadow = gs.getShadow(id_shadow.copy(), index, outputUrl)

        # 确保上层图片和背景图片具有相同的尺寸
        id = id.resize(background.size)

        # 创建一个新的图像，将背景图作为底图
        overlay = background.copy()
        # 将阴影图蓝色的部分叠加到背景图上
        overlay = Image.alpha_composite(overlay, realShadow.copy())
        # 将id图红色的部分叠加到背景图上
        overlay = Image.alpha_composite(overlay, id.copy())

        
        # 保存结果
        overlay.save(outputUrl + f'\\result{index:04d}.png')
        index += 4
        # 关闭图像
        background.close()
        shadow_mask.close()
        id.close()
        overlay.close()
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
    
    
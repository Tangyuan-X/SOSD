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
                  
    origin_img = Image.open(baseUrl + '\\Image0000.png')
    shadow_free_img = Image.open(baseUrl + '\\Image0001.png')
    origin_img.save(outputUrl + '\\origin.png')
    shadow_free_img.save(outputUrl + '\\shadow_free.png')
    origin_img.close()
    shadow_free_img.close()
                  
    # 帧长度
    index = 3
    count = 0
    frameLength = pngNum//2-1
    print("###########frame length:", frameLength)
    while (index <= frameLength):
        # 打开背景图
        background = Image.open(baseUrl + f'\\Image{index:04d}.png')
        # 打开id
        id_shadow = Image.open(baseUrl + f'\\IndexObj{index + 1:04d}.png')
        id = gi.getIndexObj(id_shadow.copy(), count, outputUrl)
        # 打开阴影mask
        pure_shadow = Image.open(baseUrl + f'\\Image{index + 4:04d}.png')
        shadow_mask = gsm.getShadowMask(pure_shadow.copy(), count, outputUrl)
        # 获取阴影
        realShadow = gs.getShadow(pure_shadow.copy(), count, outputUrl)
        
        # 保存结果
        index += 6
        count += 1
        # 关闭图像
        background.close()
        shadow_mask.close()
        id_shadow.close()
        id.close()
        pure_shadow.close()
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
    
    
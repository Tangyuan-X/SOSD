import json

from PIL import Image
import colorsys
import os


dataset_path = "D:\\Programming\\python\\SOSD\\output\\test"


# 导出阴影
def getShadowMaskIoU(mask1, mask2):
    # 将图像转换为RGBA模式，以便处理透明度通道
    mask1 = mask1.convert('RGBA')
    mask2 = mask2.convert('RGBA')
    # 获取图像的像素数据
    pixels1 = mask1.load()
    pixels2 = mask2.load()
    assert(mask1.width==mask2.width and mask1.height==mask2.height)

    cnt1 = 0
    cnt2 = 0
    # 遍历图像的每个像素
    for i in range(mask1.width):
        for j in range(mask1.height):
            # 获取当前像素的RGBA值
            r, g1, b, a = pixels1[i, j]
            r, g2, b, a = pixels2[i, j]
            if g1==255 and g2==255:
                cnt1+=1
            if g1==255 or g2==255:
                cnt2+=1

    return cnt1/cnt2


def handleOneData(data_name):
    # 计算阴影相交特殊情况的阴影交叉IOU
    global dataset_path

    with open(os.path.join(dataset_path, data_name+os.sep+data_name+"data.json"), 'r') as f:
        data_json = json.load(f)
    data_json["shadow intersection dataset only"] = True

    mask1 = Image.open(os.path.join(dataset_path, data_name + os.sep + f'shadow_mask{0:04d}.png'))
    mask2 = Image.open(os.path.join(dataset_path, data_name + os.sep + f'shadow_mask{1:04d}.png'))
    data_json["shadow IoU"] = getShadowMaskIoU(mask1, mask2)
    f.close()

    with open(os.path.join(dataset_path, data_name+os.sep+data_name+"data.json"), 'w') as f:
        json.dump(data_json, f, indent=4)


for file in os.listdir(dataset_path):
    file_path = os.path.join(dataset_path, file)
    if os.path.isfile(file_path):
        continue
    elif os.path.isdir(file_path):
        handleOneData(file)

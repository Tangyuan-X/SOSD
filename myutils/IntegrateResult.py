# 构建合成数据集
import os
import PIL


def integrateResult(file_path):
    # 将路径中所有f'IndexObjxxxxx.png'的图片合并成一张图片
    # 获取所有文件名，按照文件名排序
    print("integrateResult file_path:",file_path)
    file_names = sorted(os.listdir(file_path))
    print("file_names", file_names)

    # 获取所有IndexObj的文件名
    index_obj_file_names = [f for f in file_names if f.startswith('IndexObj')]
    # 获取第一张图片
    first_index_obj = PIL.Image.open(os.path.join(file_path, index_obj_file_names[0]))
    # 获取图片的宽度和高度
    width, height = first_index_obj.size
    # 创建一个新的图像，将背景图作为底图
    result = PIL.Image.new('RGBA', (width, height), (0, 0, 0, 0))
    # 遍历所有IndexObj的文件名rgba
    colors = [(230, 126, 34), (46, 204, 113), (52, 152, 219), (155, 89, 182), (192, 57, 43)]
    for index_obj_file_name in index_obj_file_names:
        # 弹出第一个颜色
        curColor = colors.pop(0)
        # 打开IndexObj图片
        index_obj = PIL.Image.open(os.path.join(file_path, index_obj_file_name))
        # 将IndexObj图片的红色部分变为curColor
        index_obj = index_obj.convert('RGBA')
        pixels = index_obj.load()
        for i in range(index_obj.width):
            for j in range(index_obj.height):
                r, g, b, a = pixels[i, j]
                if r > 200 and g < 100 and b < 100:
                    pixels[i, j] = curColor
        # 将IndexObj图片粘贴到result图片上
        result.paste(index_obj, (0, 0), index_obj)
        index_obj.close()
    # 保存结果
    result1 = result.copy()
    pixels = result.load()
    for i in range(result.width):
        for j in range(result.height):
            r, g, b, a = pixels[i, j]
            if a==0:
                pixels[i, j] = (0,0,0,255)
    result.save(os.path.join(file_path, 'object_mask.png'))
    first_index_obj.close()


    # 将路径中所有f'shadowxxxxx.png'的图片合并成一张图片
    # 获取所有shadow的文件名
    shadow_file_names = [f for f in file_names if f.startswith('shadow_mask')]
    # 获取第一张图片
    first_shadow = PIL.Image.open(os.path.join(file_path, shadow_file_names[0]))
    # 获取图片的宽度和高度
    width, height = first_shadow.size
    # 创建一个新的图像，将背景图作为底图
    result = PIL.Image.new('RGBA', (width, height), (0, 0, 0, 0))
    # 遍历所有shadow的文件名
    colors = [(230, 126, 34), (46, 204, 113), (52, 152, 219), (155, 89, 182), (192, 57, 43)]
    for shadow_file_name in shadow_file_names:
        print(shadow_file_name)
        # 弹出第一个颜色
        curColor = colors.pop(0)
        # 打开shadow图片
        shadow = PIL.Image.open(os.path.join(file_path, shadow_file_name))

        # 将shadow图片的红色部分变为curColor
        shadow = shadow.convert('RGBA')
        pixels = shadow.load()
        for i in range(shadow.width):
            for j in range(shadow.height):
                r, g, b, a = pixels[i, j]
                if r == 0 and g == 255 and b == 0:
                    pixels[i, j] = curColor
        # 将shadow图片粘贴到result图片上
        result.paste(shadow, (0, 0), shadow)
        shadow.close()
    # 保存结果
    result2 = result.copy()
    pixels = result.load()
    for i in range(result.width):
        for j in range(result.height):
            r, g, b, a = pixels[i, j]
            if a==0:
                pixels[i, j] = (0,0,0,255)
    result.save(os.path.join(file_path, 'shadow_mask.png'))
    first_shadow.close()

    # 将shadow和result合并
    result1.paste(result2, (0, 0), result2)
    pixels = result1.load()
    for i in range(result1.width):
        for j in range(result1.height):
            r, g, b, a = pixels[i, j]
            if a==0:
                pixels[i, j] = (0,0,0,255)
    result1.save(os.path.join(file_path, 'object_shadow_mask.png'))
    result1.close()
    result2.close()
    result.close()
    
    for index_obj_file_name in index_obj_file_names:
        os.remove(os.path.join(file_path, index_obj_file_name))
    for shadow_file_name in shadow_file_names:
        os.remove(os.path.join(file_path, shadow_file_name))
    
    
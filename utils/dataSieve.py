import json
import os
from PIL import Image


input_path_root = "D:\\Programming\\python\\SOSD_Linux\\output"
output_path_root = "D:\\Programming\\python\\SOSD_Linux\\output"
input_dataset_name = "v3v4"
output_dataset_name = "2024_6_1a1"
input_paths = [
    f"{input_path_root}\\{input_dataset_name}\\train\\cross",
    f"{input_path_root}\\{input_dataset_name}\\train\\indoor",
    f"{input_path_root}\\{input_dataset_name}\\train\\outdoor",
    f"{input_path_root}\\{input_dataset_name}\\test\\cross",
    f"{input_path_root}\\{input_dataset_name}\\test\\indoor",
    f"{input_path_root}\\{input_dataset_name}\\test\\outdoor",
    f"{input_path_root}\\{input_dataset_name}\\val\\cross",
    f"{input_path_root}\\{input_dataset_name}\\val\\indoor",
    f"{input_path_root}\\{input_dataset_name}\\val\\outdoor",
]
output_paths = [
    f"{output_path_root}\\{output_dataset_name}\\train\\cross",
    f"{output_path_root}\\{output_dataset_name}\\train\\indoor",
    f"{output_path_root}\\{output_dataset_name}\\train\\outdoor",
    f"{output_path_root}\\{output_dataset_name}\\test\\cross",
    f"{output_path_root}\\{output_dataset_name}\\test\\indoor",
    f"{output_path_root}\\{output_dataset_name}\\test\\outdoor",
    f"{output_path_root}\\{output_dataset_name}\\val\\cross",
    f"{output_path_root}\\{output_dataset_name}\\val\\indoor",
    f"{output_path_root}\\{output_dataset_name}\\val\\outdoor",
]


def handleOneData(data_path, output_path):
    # 将阴影或者物体完全不在镜头内的数据筛掉
    print("handling " + data_path, flush=True)
    data_name = data_path.split(os.sep)[-1]
    check = True

    if os.path.exists(os.path.join(output_path, data_name)):
        os.system("rm -r " + os.path.join(output_path, data_name))
    os.makedirs(os.path.join(output_path, data_name))
    for file in os.listdir(data_path):
        if file.startswith("IndexObj") or file.startswith("shadow_mask"):
            origin = Image.open(os.path.join(data_path, file))
            cnt = 0
            pixels = origin.load()
            for i in range(origin.width):
                for j in range(origin.height):
                    r, g, b, a = pixels[i, j]
                    if r+g+b+a != 0:
                        cnt += 1
            origin.close()
            if cnt < 1000:
                check = False
                print("ignore " + data_path, flush=True)
                break
            if not os.path.exists(os.path.join(output_path, data_name)):
                os.makedirs(os.path.join(output_path, data_name))
            os.system("cp " + os.path.join(data_path, file) + " " + os.path.join(output_path, data_name, file))
        else:
            if not os.path.exists(os.path.join(output_path, data_name)):
                os.makedirs(os.path.join(output_path, data_name))
            os.system("cp " + os.path.join(data_path, file) + " " + os.path.join(output_path, data_name, file))

    if not check:
        os.system("rm -r " + os.path.join(output_path, data_name))


for i in range(len(input_paths)):
    input_path = input_paths[i]
    output_path = output_paths[i]
    for file in os.listdir(input_path):
        file_path = os.path.join(input_path, file)
        if os.path.isfile(file_path):
            continue
        elif os.path.isdir(file_path):
            handleOneData(file_path, output_path)


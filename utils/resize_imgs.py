import json
import os
from PIL import Image

input_path_root = "D:\\Programming\\python\\SOSD_Linux\\output"
output_path_root = "D:\\Programming\\python\\SOSD_Linux\\output"
input_dataset_name = "2024_7_1_s"
output_dataset_name = "2024_7_1"
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


def handle_one_data(data_path, output_path):
    """
    Resize imgs to (960, 540).
    :param data_path: the init data path
    :param output_path: path the data will be saved
    :return: None
    """
    print("handling " + data_path, flush=True)
    data_name = data_path.split(os.sep)[-1]
    for file in os.listdir(data_path):
        if file.endswith("png"):
            origin = Image.open(os.path.join(data_path, file))
            if origin.width != 960 and origin.height != 540:
                origin = origin.resize((960, 540))
            if not os.path.exists(os.path.join(output_path, data_name)):
                os.makedirs(os.path.join(output_path, data_name))
            origin.save(os.path.join(output_path, data_name, file))
            origin.close()
        else:
            if not os.path.exists(os.path.join(output_path, data_name)):
                os.makedirs(os.path.join(output_path, data_name))
            os.popen("cp "+os.path.join(data_path, file)+" "+os.path.join(output_path, data_name, file))


def main():
    for i in range(len(input_paths)):
        input_path = input_paths[i]
        output_path = output_paths[i]
        for file in os.listdir(input_path):
            file_path = os.path.join(input_path, file)
            if os.path.isfile(file_path):
                continue
            elif os.path.isdir(file_path):
                handle_one_data(file_path, output_path)


if __name__ == '__main__':
    main()

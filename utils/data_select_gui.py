import json
import os
from PIL import Image
import cv2


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
    Get input from terminal and save or delete this data.
    :param data_path: the init data path
    :param output_path: path the data will be saved
    :return: None
    """
    print("handling " + data_path, flush=True)
    data_name = data_path.split(os.sep)[-1]

    with open(data_path+os.sep+data_name+"data.json") as f:
        json_data = json.load(f)
    print("object cnt: ", json_data["object_count"], flush=True)

    origin = cv2.imread(data_path+os.sep+"origin.png")
    cv2.imshow("origin", origin)
    shadow_free = cv2.imread(data_path + os.sep + "shadow_free.png")
    cv2.imshow("shadow free", shadow_free)
    cv2.waitKey(1)

    while True:
        cv2.waitKey(1)
        op = int(input("choose 1(save), 2(delete), 3(open in explorer): "))
        if op == 1:
            os.system("cp -r "+data_path+" "+output_path)
            break
        elif op == 2:
            break
        elif op == 3:
            os.system("explorer \""+data_path+"\"")

    print("########################################\n\n\n", flush=True)


def main():
    cv2.namedWindow("origin")
    cv2.namedWindow("shadow free")

    for i in range(len(input_paths)):
        input_path = input_paths[i]
        output_path = output_paths[i]
        os.system("mkdir " + output_path)

        print(input_path, flush=True)
        fileList = os.listdir(input_path)
        startI = int(input("start index(-1 to skip): "))
        if startI == -1:
            continue

        for i in range(startI, len(fileList)):
            file_path = os.path.join(input_path, fileList[i])
            if os.path.isfile(file_path):
                continue
            elif os.path.isdir(file_path):
                print(f"({i}/{len(fileList)})", end=' ')
                handle_one_data(file_path, output_path)

    cv2.destroyWindow("origin")
    cv2.destroyWindow("shadow free")


if __name__ == '__main__':
    main()

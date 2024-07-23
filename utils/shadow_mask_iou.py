import json

from PIL import Image
import os


def get_shadow_mask_iou(mask1, mask2):
    """
    Get the Intersection over Union of two shadow hard masks
    :param mask1: first shadow hard mask
    :param mask2: second shadow hard mask
    :return:
    """
    mask1 = mask1.convert('RGBA')
    mask2 = mask2.convert('RGBA')
    pixels1 = mask1.load()
    pixels2 = mask2.load()
    assert(mask1.width == mask2.width and mask1.height == mask2.height)

    cnt1 = 0
    cnt2 = 0
    for i in range(mask1.width):
        for j in range(mask1.height):
            r, g1, b, a = pixels1[i, j]
            r, g2, b, a = pixels2[i, j]
            if g1 == 255 and g2 == 255:
                cnt1 += 1
            if g1 == 255 or g2 == 255:
                cnt2 += 1

    return cnt1/cnt2


def handle_one_data(data_name, dataset_path):
    """
    Calculate the IoU of "cross" dataset. Write to xxxdata.json.
    :param data_name: data's id number
    :param dataset_path: the path to "cross" dataset
    :return: None
    """

    with open(os.path.join(dataset_path, data_name+os.sep+data_name+"data.json"), 'r') as f:
        data_json = json.load(f)
    data_json["shadow_intersection_dataset_only"] = True

    mask1 = Image.open(os.path.join(dataset_path, data_name + os.sep + f'shadow_mask{0:04d}.png'))
    mask2 = Image.open(os.path.join(dataset_path, data_name + os.sep + f'shadow_mask{1:04d}.png'))
    data_json["shadow IoU"] = get_shadow_mask_iou(mask1, mask2)
    f.close()

    with open(os.path.join(dataset_path, data_name+os.sep+data_name+"data.json"), 'w') as f:
        json.dump(data_json, f, indent=4)


def main():
    dataset_path = "D:\\Programming\\python\\SOSD\\output\\test"
    for file in os.listdir(dataset_path):
        file_path = os.path.join(dataset_path, file)
        if os.path.isfile(file_path):
            continue
        elif os.path.isdir(file_path):
            handle_one_data(file, dataset_path)


if __name__ == '__main__':
    main()

import json
import pycocotools.mask as mask_util
import time
import os
from PIL import Image
import numpy as np


output_data = {}
image_cnt = 0
annotations_cnt = 0
association_anno_cnt = 0
images = []
annotations = []
association_anno = []

dataset_path_root = "D:\\Programming\\python\\SOSD_Linux\\output"
dataset_name = "v3v4"
dataset_paths = [
    f"{dataset_path_root}\\{dataset_name}\\train",
    f"{dataset_path_root}\\{dataset_name}\\test",
    f"{dataset_path_root}\\{dataset_name}\\val"
]
dataset_types = [
    "indoor",
    "outdoor",
    "cross"
]


def handleOneData(data_name, dataset_path, dtype):
    global image_cnt, annotations_cnt, association_anno_cnt
    global images, annotations, association_anno

    with open(os.path.join(dataset_path, data_name+os.sep+data_name+"data.json"), 'r') as f:
        data_json = json.load(f)
    object_count = data_json["object_count"]

    image_cnt += 1
    print("handling " + data_name + ", No. " + str(image_cnt))
    image_data = {}
    image_data["image_name"] = data_name
    image_data["file_name"] = dtype + "/" + data_name + "/" + "origin.png"
    image_data["shadow_free_path"] = dtype + "/" + data_name + "/" + "shadow_free.png"
    image_data["non_object_shadow"] = False
    image_data["id"] = image_cnt
    image_data["image_id"] = image_cnt
    image_data["data_type"] = dtype

    origin = Image.open(os.path.join(dataset_path, data_name + os.sep + "origin.png"))
    width = origin.width
    height = origin.height
    image_data["height"] = height
    image_data["width"] = width
    images.append(image_data)
    origin.close()

    RLEs = []

    for idx in range(0, object_count):
        annotation_data = {}
        annotations_cnt += 1
        annotation_data["id"] = annotations_cnt
        annotation_data["image_id"] = image_cnt
        annotation_data["category_id"] = 1
        annotation_data["iscrowd"] = 0
        annotation_data["association"] = idx+1
        annotation_data["obj_type"] = data_json["objects"][idx]["obj_type"]
        annotation_data["obj_id"] = data_json["objects"][idx]["obj_id"]


        obj_mask = Image.open(os.path.join(dataset_path, data_name + os.sep + f'IndexObj{idx:04d}.png'))
        annotation_data["width"] = width
        annotation_data["height"] = height

        mask_arr = np.zeros((height, width), dtype=np.uint8)
        obj_mask = obj_mask.convert('RGBA')
        pixels = obj_mask.load()
        for i in range(width):
            for j in range(height):
                r, g, b, a = pixels[i, j]
                if r == 255:
                    mask_arr[j, i] = 1

        rleObj = mask_util.encode(np.asarray(mask_arr, order="F"))
        RLEs.append(rleObj.copy())
        rleObj["counts"] = rleObj["counts"].decode("utf-8")

        annotation_data["area"] = int(mask_util.area(rleObj))
        annotation_data["segmentation"] = rleObj
        annotation_data["bbox"] = mask_util.toBbox(rleObj).tolist()
        annotation_data["soft_shadow"] = dtype + "/" + data_name + '/' + f'shadow_soft_mask{idx:04d}.png'

        annotations.append(annotation_data)
        obj_mask.close()
        # TODO: light字段的含义是什么

    for idx in range(0, object_count):
        annotation_data = {}
        annotations_cnt += 1
        annotation_data["id"] = annotations_cnt
        annotation_data["image_id"] = image_cnt
        annotation_data["category_id"] = 2
        annotation_data["iscrowd"] = 0
        annotation_data["association"] = idx+1
        annotation_data["obj_type"] = data_json["objects"][idx]["obj_type"]
        annotation_data["obj_id"] = data_json["objects"][idx]["obj_id"]

        shadow_mask = Image.open(os.path.join(dataset_path, data_name + os.sep + f'shadow_mask{idx:04d}.png'))
        annotation_data["width"] = width
        annotation_data["height"] = height

        mask_arr = np.zeros((height, width), dtype=np.uint8)
        shadow_mask = shadow_mask.convert('RGBA')
        pixels = shadow_mask.load()
        for i in range(width):
            for j in range(height):
                r, g, b, a = pixels[i, j]
                if g == 255:
                    mask_arr[j, i] = 1

        rleObj = mask_util.encode(np.asarray(mask_arr, order="F"))
        RLEs.append(rleObj.copy())
        rleObj["counts"] = rleObj["counts"].decode("utf-8")

        annotation_data["area"] = int(mask_util.area(rleObj))
        annotation_data["segmentation"] = rleObj
        annotation_data["bbox"] = mask_util.toBbox(rleObj).tolist()

        # annotation_data["soft_shadow"] = data_name + os.sep + f'shadow_soft_mask{idx:04d}.png'
        annotation_data["soft_shadow"] = dtype + '/' + data_name + '/' + f'shadow_soft_mask{idx:04d}.png'

        annotations.append(annotation_data)
        shadow_mask.close()
        # TODO: light字段的含义是什么

    for idx in range(0, object_count):
        association_anno_data = {}
        association_anno_cnt += 1
        association_anno_data["id"] = association_anno_cnt
        association_anno_data["image_id"] = image_cnt
        association_anno_data["category_id"] = 1
        association_anno_data["iscrowd"] = 0
        association_anno_data["association"] = idx+1
        annotation_data["obj_type"] = data_json["objects"][idx]["obj_type"]
        annotation_data["obj_id"] = data_json["objects"][idx]["obj_id"]

        association_anno_data["width"] = width
        association_anno_data["height"] = height

        rleObj = mask_util.merge([RLEs[idx], RLEs[idx+object_count]])
        rleObj["counts"] = rleObj["counts"].decode("utf-8")

        association_anno_data["area"] = int(mask_util.area(rleObj))
        association_anno_data["segmentation"] = rleObj
        association_anno_data["bbox"] = mask_util.toBbox(rleObj).tolist()
        association_anno_data["soft_shadow"] = dtype + '/' + data_name + '/' + f'shadow_soft_mask{idx:04d}.png'

        association_anno.append(association_anno_data)
        bbox1 = mask_util.toBbox(RLEs[idx]).tolist()
        bbox1[2] = bbox1[0]+bbox1[2]
        bbox1[3] = bbox1[1] + bbox1[3]
        bbox2 = mask_util.toBbox(RLEs[idx+object_count]).tolist()
        bbox2[2] = bbox2[0] + bbox2[2]
        bbox2[3] = bbox2[1] + bbox2[3]

        fi = annotations_cnt-object_count*2
        annotations[fi+idx]["relation"] = [bbox2[0]/2+bbox2[2]/2, bbox2[1]/2+bbox2[3]/2]
        annotations[fi+idx+object_count]["relation"] = [bbox1[0] / 2 + bbox1[2] / 2, bbox1[1] / 2 + bbox1[3] / 2]

        # TODO: light字段的含义是什么


for dataset_path in dataset_paths:
    output_data = {
        "info": {
            "description": "SOSD",
            "version": "0.3.0",
            "year": int(time.strftime("%Y", time.localtime())),
            "contributor": "TBD",
            "date_created": str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        },
        "licenses": [
            {
                "id": 1,
                "name": "TBD"
            }
        ],
        "categories": [
            {
                "id": 1,
                "name": "Object",
                "supercategory": "Object"
            },
            {
                "id": 2,
                "name": "Shadow",
                "supercategory": "Shadow"
            }
        ],
        "association": [
            {
                "id": 1,
                "name": "Association",
                "supercategory": "Association"
            }
        ]
    }
    image_cnt = 0
    annotations_cnt = 0
    association_anno_cnt = 0
    images = []
    annotations = []
    association_anno = []

    for dtype in dataset_types:
        dt_path = dataset_path+os.sep+dtype
        for file in os.listdir(dt_path):
            file_path = os.path.join(dt_path, file)
            if os.path.isfile(file_path):
                continue
            elif os.path.isdir(file_path):
                handleOneData(file, dt_path, dtype)

    print(image_cnt)
    output_data["images"] = images
    output_data["annotations"] = annotations
    output_data["association_anno"] = association_anno
    with open(dataset_path+'\\data.json', 'w') as f:
        json.dump(output_data, f, indent=4)

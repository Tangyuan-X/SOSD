import cmath
import random
import os
import time
import pathlib
import math
import sys
import json

# need to use python in blender
import bpy

current_dir = os.path.dirname(os.path.dirname(__file__))
print("current dir: "+current_dir)
sys.path.append(current_dir)
sys.path.append(current_dir+os.sep+"utils")
os.chdir(current_dir)

from utils.blender_image_and_shadow import handle_result
import utils.scene_layout as usl


def main():
    usl.enable_gpus("CUDA")

    # import the generation config
    with open(current_dir + os.sep + 'config.json', 'r') as f:
        config = json.load(f)

    obj_root = config['path']['objects']
    obj_list = usl.load_obj_paths(current_dir, obj_root)

    obj_count_min = config['indoor']['obj_count_min']
    obj_count_max = config['indoor']['obj_count_max']

    times = config["indoor"]['output_amount']

    bpy.context.scene.render.filepath = config["path"]['output'] + os.sep + "tmp" + os.sep
    bpy.context.scene.render.resolution_x = config["resolution"]["x"]
    bpy.context.scene.render.resolution_y = config["resolution"]["y"]
    comp_node = bpy.context.scene.node_tree.nodes["file_output123"]
    comp_node.base_path = config["path"]['output']
    output_path = config["path"]['output']

    for i in range(times):
        # 获得时间戳
        now = int(time.time())
        json_data = {}
        output_path1 = output_path + os.sep + str(now)

        inter_only = config["indoor"]["shadow_intersection_dataset_only"]
        no_overlap = config["indoor"]["no_shadow_overlap"]
        if inter_only and no_overlap:
            raise Exception(
                "shadow intersection dataset only and no shadow overlap should not be true at the same time")

        while True:
            usl.remove_all_objects_from_collection(bpy.data.collections['items'])
            usl.remove_all_obj_materials()

            if inter_only:
                obj_info = usl.obj_layout_shadow_inter_only(obj_list)
            elif no_overlap:
                obj_info = usl.obj_layout_shadow_no_overlap(obj_list, obj_count_min, obj_count_max)
            else:
                obj_info = usl.random_items(obj_list, obj_count_min, obj_count_max)
            if len(obj_info) > 0:
                break

        usl.adjust_obj_dataset(obj_info, json_data)
        usl.obj_info_to_json(obj_info, json_data, obj_root[0][:-len(obj_root[0].split(os.sep)[-1])])

        usl.change_ground_texture(json_data, config)
        usl.remove_all_objects_from_collection(bpy.data.collections['light'])
        usl.remove_all_objects_from_collection(bpy.data.collections['tracked'])
        if inter_only:
            usl.change_light_shadow_inter_only(json_data, obj_info)
            usl.camera_pos_shadow_inter_only(json_data, obj_info)
        elif no_overlap:
            usl.change_light_shadow_no_overlap(json_data, obj_info)
            usl.random_camera_no_overlap(json_data, obj_info, 1.0, 2.0, -math.pi / 6, math.pi / 6)
        else:
            usl.change_light(json_data, config["indoor"]['light_amount'], config["indoor"]["light_types"])
            usl.random_camera(json_data, obj_info)

        if not os.path.exists(output_path1):
            os.makedirs(output_path1)
        if config["indoor"]["save_blend"]:
            bpy.ops.wm.save_as_mainfile(filepath=output_path1 + os.sep + str(now) + '.blend')

        usl.render_animation()
        handle_result(output_path, output_path1)

        with open(output_path1 + os.sep + str(now) + 'data.json', 'w') as f:
            json.dump(json_data, f, indent=4)


if __name__ == '__main__':
    main()

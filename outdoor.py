import random
import os
import time
import pathlib
import sys
import json

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

    with open(current_dir+os.sep+'config.json', 'r') as f:
        config = json.load(f)

    obj_root = config['path']['objects']
    obj_list = usl.load_obj_paths(current_dir, obj_root)

    obj_count_min = config['outdoor']['obj_count_min']
    obj_count_max = config['outdoor']['obj_count_max']

    os.chdir(current_dir)

    times = config["outdoor"]['output_amount']

    bpy.context.scene.render.filepath = config["path"]['output'] + os.sep + "tmp" + os.sep
    bpy.context.scene.render.resolution_x = config["resolution"]["x"]
    bpy.context.scene.render.resolution_y = config["resolution"]["y"]
    comp_node = bpy.context.scene.node_tree.nodes["file_output123"]
    comp_node.base_path = config["path"]['output']
    output_path = config["path"]['output']

    for i in range(times):
        now = int(time.time())
        json_data = {}
        output_path1 = output_path + os.sep + str(now)
        no_overlap = config["outdoor"]["no_shadow_overlap"]

        while True:
            usl.remove_all_objects_from_collection(bpy.data.collections['items'])
            usl.remove_all_obj_materials()

            if no_overlap:
                obj_info = usl.obj_layout_shadow_no_overlap(obj_list, obj_count_min, obj_count_max)
            else:
                obj_info = usl.random_items(obj_list, obj_count_min, obj_count_max)
            if len(obj_info) > 0:
                break

        usl.adjust_obj_dataset(obj_info, json_data)
        usl.obj_info_to_json(obj_info, json_data, obj_root[0][:-len(obj_root[0].split(os.sep)[-1])])
        usl.change_hdri(json_data, config)

        if no_overlap:
            usl.random_camera_no_overlap(json_data, obj_info, 0.1 + 0.2 * len(obj_info) * 0.5, 0.3 + 0.3 * len(obj_info) * 0.5)
        else:
            usl.random_camera(json_data, obj_info, 5.5, 6.5, 1.0, 3.0)

        if not os.path.exists(output_path1):
            os.makedirs(output_path1)
        if config["outdoor"]["save_blend"]:
            bpy.ops.wm.save_as_mainfile(filepath=output_path1 + os.sep + str(now) + '.blend')

        usl.render_animation()
        handle_result(output_path, output_path1)

        with open(output_path1 + os.sep + str(now) + 'data.json', 'w') as f:
            json.dump(json_data, f, indent=4)


if __name__ == '__main__':
    main()

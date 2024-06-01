# 构建合成数据集
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

from utils.BlenderImageAndShadow import HandleResult
import utils.SceneLayout as usl


# 修改地面纹理
def change_hdri(JSONData):
    # 设置纹理文件夹路径
    hdri_folder = config["path"]['hdri texture']
    exr_files = [f for f in os.listdir(hdri_folder) if f.lower().endswith('.exr')]

    if not exr_files:
        raise Exception("No .exr files found in directory")

    selected_file = random.choice(exr_files)
    selected_file_path = os.path.join(hdri_folder, selected_file)
    JSONData["hdri_texture_path"] = str(selected_file)

    # 确保对象存在
    if "ground" not in bpy.data.objects:
        raise Exception("Object 'sphere' not found")

    if "sky" not in bpy.data.objects:
        raise Exception("Object 'sky' not found")

    # 获取对象
    ground = bpy.data.objects['ground']
    sky = bpy.data.objects['sky']

    # 确保对象有材质
    if not ground.data.materials:
        raise Exception("Object 'sphere' has no materials")
    if not sky.data.materials:
        raise Exception("Object 'sphere' has no materials")

    # 只修改第一个材质
    material = ground.data.materials[0]
    material.use_nodes = True
    nodes = material.node_tree.nodes
    # 获取Principled BSDF节点
    texture_node = next((node for node in nodes if node.type == 'TEX_IMAGE'), None)
    if texture_node is None:
        raise Exception("TEX_IMAGE node not found in material of object 'ground'")
    texture_node.image = bpy.data.images.load(selected_file_path)
    print(f"Base color of material '{material.name}' of object 'ground' has been updated with '{selected_file}'")

    material = sky.data.materials[0]
    material.use_nodes = True
    nodes = material.node_tree.nodes
    texture_node = next((node for node in nodes if node.type == 'TEX_IMAGE'), None)
    if texture_node is None:
        raise Exception("TEX_IMAGE node not found in material of object 'sky'")
    texture_node.image = bpy.data.images.load(selected_file_path)
    print(f"Base color of material '{material.name}' of object 'sky' has been updated with '{selected_file}'")

    nodes = bpy.context.scene.world.node_tree.nodes
    texture_node = next((node for node in nodes if node.type == 'TEX_ENVIRONMENT'), None)
    if texture_node is None:
        raise Exception("TEX_ENVIRONMENT node not found in material of 'world'")
    texture_node.image = bpy.data.images.load(selected_file_path)


usl.enable_gpus("CUDA")

# 导入json配置
with open(current_dir+os.sep+'config.json', 'r') as f:
    config = json.load(f)
    
print('Google Scanned Objects dir:', config['path']['scanned objects'])
# obj文件夹路径
obj_root = pathlib.Path(config['path']['scanned objects'])
objList = usl.load_obj_paths(current_dir, obj_root)

# 切换当前工作目录到脚本所在的目录
os.chdir(current_dir)

times = config["outdoor"]['output_amount']

bpy.context.scene.render.filepath = config["path"]['output'] + os.sep + "tmp" + os.sep
bpy.context.scene.render.resolution_x = config["resolution"]["x"]
bpy.context.scene.render.resolution_y = config["resolution"]["y"]
comp_node = bpy.context.scene.node_tree.nodes["file_output123"]
comp_node.base_path = config["path"]['output']
outputUrl = config["path"]['output']

for i in range(times):
    # 获得时间戳
    now = int(time.time())
    JSONData = {}
    outputUrl1 = outputUrl + os.sep + str(now)

    while True:
        usl.remove_all_objects_from_collection(bpy.data.collections['items'])
        usl.remove_all_materials()
        # 随机生成3-5个物体
        objInfo = usl.random3_5items(objList)
        if len(objInfo) > 0:
            break

    usl.objInfo2JSON(objInfo, JSONData, obj_root)
    # 随机修改ground材质、光源
    change_hdri(JSONData)
    usl.randomCamera(JSONData)
    # 保存文件
    if(not os.path.exists(outputUrl1)):
        os.makedirs(outputUrl1)
    if config["outdoor"]["save_blend"]:
        bpy.ops.wm.save_as_mainfile(filepath=outputUrl1 + os.sep + str(now) + '.blend')
    with open(outputUrl1+os.sep+str(now)+'data.json', 'w') as f:
        json.dump(JSONData, f, indent=4)

    # 渲染动画
    usl.render_animation()
    HandleResult(outputUrl, outputUrl1)
    


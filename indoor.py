# 构建合成数据集
import random
import os
import time
import pathlib
import math
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
def change_ground_texture(JSONData):
    # 设置纹理文件夹路径
    texture_folder = config['path']['ground texture']
    # 获取所有的.jpg文件
    jpg_files = [f for f in os.listdir(texture_folder) if f.lower().endswith('.jpg')]

    # 确保至少有一个.jpg文件
    if not jpg_files:
        raise Exception("No .jpg files found in directory")

    # 随机选择一个.jpg文件
    selected_file = random.choice(jpg_files)
    selected_file_path = os.path.join(texture_folder, selected_file)
    JSONData["ground_texture_path"] = str(selected_file)

    # 确保对象存在
    if "ground" not in bpy.data.objects:
        raise Exception("Object 'ground' not found")

    # 获取对象
    ground_object = bpy.data.objects['ground']

    # 确保对象有材质
    if not ground_object.data.materials:
        raise Exception("Object 'ground' has no materials")

    # 只修改第一个材质
    material = ground_object.data.materials[0]

    # 启用使用节点
    material.use_nodes = True
    nodes = material.node_tree.nodes

    # 获取Principled BSDF节点
    principled_bsdf_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
    if principled_bsdf_node is None:
        raise Exception("Principled BSDF node not found in material of object 'ground'")

    # 如果已经有一个贴图链接到基础颜色，我们需要先删除它
    for link in material.node_tree.links:
        if link.to_node == principled_bsdf_node and link.to_socket.name == 'Base Color':
            material.node_tree.links.remove(link)

    # 创建一个新的图片纹理节点
    texture_node = nodes.new('ShaderNodeTexImage')
    texture_node.image = bpy.data.images.load(selected_file_path)

    # 将新的图片纹理节点连接到Principled BSDF节点的基础颜色输入
    material.node_tree.links.new(principled_bsdf_node.inputs['Base Color'], texture_node.outputs['Color'])

    print(f"Base color of material '{material.name}' of object 'ground' has been updated with '{selected_file}'")


# 随机设置灯光
def changeLight(JSONData, max_light=4):
    usl.remove_all_objects_from_collection(bpy.data.collections['light'])
    usl.remove_all_objects_from_collection(bpy.data.collections['tracked'])

    lightNum = random.randint(1, max_light)
    lightTypes = ["POINT", "SPOT", "AREA"]

    infos = []
    for i in range(lightNum):
        ltype = random.choice(lightTypes)
        if max_light == 1:
            ltype = "POINT"
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["light"]
        bpy.ops.object.light_add(type=ltype)
        light = bpy.context.selected_objects[0]
        light.hide_render = False
        light.hide_viewport = False

        tracked = light
        if ltype != "POINT":
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["tracked"]
            bpy.ops.object.add()
            tracked = bpy.context.selected_objects[0]
            tracked.location = random.uniform(-3, 3), random.uniform(-3, 3), 0

        if ltype == "POINT":
            light.data.energy = random.uniform(200, 400)
            light.location = random.uniform(-4.5, 1.5), random.uniform(-2.5, 2.5), random.uniform(0.5, 5)
            light.data.shadow_soft_size = random.uniform(0.1, 0.3)

            info = {}
            x, y, z = light.location
            info["location"] = {"x": x, "y": y, "z": z}
            x, y, z = light.rotation_euler
            info["rotation_euler"] = {"x": x, "y": y, "z": z}
            x, y, z = light.scale
            info["scale"] = {"x": x, "y": y, "z": z}
            info["energy"] = light.data.energy
            info["type"] = light.data.type
            info["shadow_soft_size"] = light.data.shadow_soft_size

            infos.append(info)
        elif ltype == "SPOT":
            light.data.energy = random.uniform(150, 550)
            light.location = random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(0.5, 5)
            light.data.shadow_soft_size = random.uniform(0.1, 0.3)
            light.data.spot_blend = random.uniform(0.1, 0.3)
            light.data.spot_size = random.uniform(0.3, 1.8)
            light.constraints.new("TRACK_TO")
            light.constraints[0].track_axis = "TRACK_NEGATIVE_Z"
            light.constraints[0].up_axis = "UP_Y"
            light.constraints[0].target = tracked

            info = {}
            x, y, z = light.location
            info["location"] = {"x": x, "y": y, "z": z}
            x, y, z = tracked.location
            info["track_to"] = {"x": x, "y": y, "z": z}
            x, y, z = light.scale
            info["scale"] = {"x": x, "y": y, "z": z}
            info["energy"] = light.data.energy
            info["type"] = light.data.type
            info["shadow_soft_size"] = light.data.shadow_soft_size
            info["spot_blend"] = light.data.spot_blend
            info["spot_size"] = light.data.spot_size

            infos.append(info)
        elif ltype == "AREA":
            light.data.shape = 'RECTANGLE'
            light.data.energy = random.uniform(50, 400)
            light.location = random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(0.5, 5)
            light.data.size = random.uniform(0.5, 2.5)
            light.data.size_y = random.uniform(0.5, 2.5)
            light.data.spread = random.uniform(math.pi/3, math.pi)
            light.constraints.new("TRACK_TO")
            light.constraints[0].track_axis = "TRACK_NEGATIVE_Z"
            light.constraints[0].up_axis = "UP_Y"
            light.constraints[0].target = tracked

            info = {}
            x, y, z = light.location
            info["location"] = {"x": x, "y": y, "z": z}
            x, y, z = tracked.location
            info["track_to"] = {"x": x, "y": y, "z": z}
            x, y, z = light.scale
            info["scale"] = {"x": x, "y": y, "z": z}
            info["energy"] = light.data.energy
            info["type"] = light.data.type
            info["size"] = light.data.size
            info["size_y"] = light.data.size_y
            info["spread"] = light.data.spread

            infos.append(info)

    JSONData["light"] = infos


####################################################################################
# 程序开始
####################################################################################

usl.enable_gpus("CUDA")

# 导入json配置
with open(current_dir+os.sep+'config.json', 'r') as f:
    config = json.load(f)
    
print('Google Scanned Objects dir:', config['path']['scanned objects'])
# obj文件夹路径
obj_root = pathlib.Path(config['path']['scanned objects'])
objList = usl.load_obj_paths(current_dir, obj_root)

times = config["indoor"]['output_amount']

bpy.context.scene.render.filepath = config["path"]['output'] + os.sep + "tmp" + os.sep
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
    change_ground_texture(JSONData)
    changeLight(JSONData, config["indoor"]['light_amount'])
    usl.randomCamera(JSONData)
    # 保存文件
    if(not os.path.exists(outputUrl1)):
        os.makedirs(outputUrl1)
    if config["indoor"]["save_blend"]:
        bpy.ops.wm.save_as_mainfile(filepath=outputUrl1+os.sep+str(now)+'.blend')
    with open(outputUrl1+os.sep+str(now)+'data.json', 'w') as f:
        json.dump(JSONData, f, indent=4)

    # 渲染动画
    usl.render_animation()
    HandleResult(outputUrl, outputUrl1)
    


# 构建合成数据集
import cmath
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

    lightNum = random.randint(1, max_light)
    global lightTypes

    infos = []
    for i in range(lightNum):
        ltype = random.choice(lightTypes)
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
            light.data.shadow_soft_size = random.uniform(0, 0.2)

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
            light.data.shadow_soft_size = random.uniform(0.0, 0.1)
            light.data.spot_blend = random.uniform(0.1, 0.3)
            light.data.spot_size = random.uniform(math.pi/2, math.pi*2/3)
            light.constraints.clear()
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
            light.data.energy = random.uniform(200, 400)
            cn = cmath.rect(random.uniform(3, 4), random.uniform(0, 2*math.pi))
            light.location = cn.real, cn.imag, random.uniform(0.5, 5)
            light.data.size = random.uniform(10, 12.5)
            light.data.size_y = random.uniform(10, 12.5)
            light.data.spread = random.uniform(math.pi/180, math.pi/18)
            light.constraints.clear()
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
        elif ltype == "SUN":
            light.data.energy = random.uniform(3, 8)
            cn = cmath.rect(random.uniform(1, 3), random.uniform(0, 2 * math.pi))
            light.location = cn.real, cn.imag, random.uniform(1, 5)
            light.data.angle = random.uniform(0, math.pi*5/180)
            light.constraints.clear()
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
            info["light_angle"] = light.data.angle

            infos.append(info)

    JSONData["light"] = infos


def objLayout_shadow_inter_only(objList):
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["items"]
    objRet = []

    obj_info = random.choice(list(objList))
    obj_fname = obj_info[0]
    bpy.ops.import_scene.obj(filepath=str(obj_fname))
    # 选中导入的物体
    obj = bpy.context.selected_objects[0]

    # 高光归零，防止阴影带有物体材质
    material = obj.data.materials[0]
    nodes = material.node_tree.nodes
    principled_bsdf_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
    principled_bsdf_node.inputs['Specular'].default_value = 0.0

    cn = cmath.rect(random.uniform(0.3, 0.8), random.uniform(math.pi*2/3, math.pi) + random.randint(0,1)*math.pi)
    randomX = cn.real
    randomY = cn.imag
    # 设置obj坐标
    obj.location = (randomX, randomY, 0)
    # 设置物体的缩放
    scale_size = random.uniform(0.3, 1.5)
    usl.set_obj_scale_to_max_size(obj, max_size=scale_size)
    # 随机设置物体的旋转
    rotate = random.uniform(0, 2 * math.pi)
    obj.rotation_euler = 0, 0, rotate

    objRet.append([obj_fname, obj, obj_info[1], obj_info[2]])

    # 以下是一模一样的第二个物体
    bpy.ops.import_scene.obj(filepath=str(obj_fname))
    obj = bpy.context.selected_objects[0]
    obj.location = (randomX, randomY, 0)
    usl.set_obj_scale_to_max_size(obj, max_size=scale_size)
    obj.rotation_euler = 0, 0, rotate
    objRet.append([obj_fname, obj, obj_info[1], obj_info[2]])

    # 设置第二个模型，与第一个模型成一定的夹角，方便构建阴影交叉
    cn = complex(randomX, randomY)
    radius, deg = cmath.polar(cn)
    cn1 = cmath.rect(radius+random.uniform(-0.2, 0.2), deg+random.uniform(math.pi/3, math.pi/2))
    obj_info = random.choice(list(objList))
    obj_fname = obj_info[0]
    bpy.ops.import_scene.obj(filepath=str(obj_fname))
    # 选中导入的物体
    obj = bpy.context.selected_objects[0]

    # 高光归零，防止阴影带有物体材质
    material = obj.data.materials[0]
    nodes = material.node_tree.nodes
    principled_bsdf_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
    principled_bsdf_node.inputs['Specular'].default_value = 0.0

    randomX = cn1.real
    randomY = cn1.imag
    # 设置obj坐标
    obj.location = (randomX, randomY, 0)
    # 设置物体的缩放
    scale_size = random.uniform(0.3, 1.5)
    usl.set_obj_scale_to_max_size(obj, max_size=scale_size)
    # 随机设置物体的旋转
    rotate = random.uniform(0, 2 * math.pi)
    obj.rotation_euler = 0, 0, rotate

    objRet.append([obj_fname, obj, obj_info[1], obj_info[2]])

    # 以下是一模一样的第二个物体
    bpy.ops.import_scene.obj(filepath=str(obj_fname))
    obj = bpy.context.selected_objects[0]
    obj.location = (randomX, randomY, 0)
    usl.set_obj_scale_to_max_size(obj, max_size=scale_size)
    obj.rotation_euler = 0, 0, rotate
    objRet.append([obj_fname, obj, obj_info[1], obj_info[2]])

    usl.addRenderFrame(objRet)

    for i in range(0, len(objRet), 2):
        if obj.dimensions[2] < 0.3:
            # 物体太矮则阴影不够长无法交叉
            return []
        for j in range(i + 2, len(objRet), 2):
            if usl.objectsOverlap(objRet[i][1], objRet[j][1]):
                return []

    return objRet


def objLayout_shadow_no_overlap(objList):
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["items"]
    objNum = random.randint(3, 5)
    objRet = []

    deg = random.uniform(0, 2*math.pi)

    for i in range(objNum):
        # 随机选取1个obj文件
        obj_info = random.choice(list(objList))
        obj_fname = obj_info[0]
        bpy.ops.import_scene.obj(filepath=str(obj_fname))
        # 选中导入的物体
        obj = bpy.context.selected_objects[0]

        # 高光归零，防止阴影带有物体材质
        material = obj.data.materials[0]
        nodes = material.node_tree.nodes
        principled_bsdf_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
        principled_bsdf_node.inputs['Specular'].default_value = 0.0

        cn = cmath.rect(random.uniform(-1.5, 1.5), deg+random.uniform(-math.pi/24, math.pi/24))
        randomX = cn.real
        randomY = cn.imag
        # 设置obj坐标
        obj.location = (randomX, randomY, 0)
        # 设置物体的缩放
        scale_size = random.uniform(0.4, 0.8)
        usl.set_obj_scale_to_max_size(obj, max_size=scale_size)
        # 随机设置物体的旋转
        rotate = random.uniform(0, 2 * math.pi)
        obj.rotation_euler = 0, 0, rotate

        objRet.append([obj_fname, obj, obj_info[1], obj_info[2]])

        # 以下是一模一样的第二个物体
        bpy.ops.import_scene.obj(filepath=str(obj_fname))
        obj = bpy.context.selected_objects[0]
        obj.location = (randomX, randomY, 0)
        usl.set_obj_scale_to_max_size(obj, max_size=scale_size)
        obj.rotation_euler = 0, 0, rotate
        objRet.append([obj_fname, obj, obj_info[1], obj_info[2]])

    usl.addRenderFrame(objRet)

    for i in range(0, len(objRet), 2):
        for j in range(i + 2, len(objRet), 2):
            if usl.objectsOverlap(objRet[i][1], objRet[j][1]):
                return []

    return objRet


def changeLight_shadow_inter_only(JSONData, objInfo):

    lightNum = 2

    infos = []
    for i in range(lightNum):
        ltype = "POINT"
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["light"]
        bpy.ops.object.light_add(type=ltype)
        light = bpy.context.selected_objects[0]
        light.hide_render = False
        light.hide_viewport = False

        light.data.energy = random.uniform(300, 350)
        obj = objInfo[i*2][1]
        cn = complex(obj.location[0], obj.location[1])
        radius, deg = cmath.polar(cn)
        cn1 = cmath.rect(radius + random.uniform(1.5, 2.5), deg + random.uniform(-math.pi / 24, math.pi / 24))

        light.location = cn1.real, cn1.imag, random.uniform(0.5, 1.0)
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

    JSONData["light"] = infos


def changeLight_shadow_no_overlap(JSONData, objInfo):
    lightNum = 1
    infos = []

    ltype = "SUN"
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["light"]
    bpy.ops.object.light_add(type=ltype)
    light = bpy.context.selected_objects[0]
    light.hide_render = False
    light.hide_viewport = False

    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["tracked"]
    bpy.ops.object.add()
    tracked = bpy.context.selected_objects[0]

    obj = objInfo[0][1]
    cn = complex(obj.location[0], obj.location[1])
    radius, deg = cmath.polar(cn)
    radius = random.uniform(-3, 3)
    deg = deg + math.pi/2 + random.uniform(-math.pi / 24, math.pi / 24)
    cn1 = cmath.rect(radius, deg)
    tracked.location = cn1.real, cn1.imag, 0
    cn1 = cmath.rect(-radius, deg)

    light.data.energy = random.uniform(3, 8)
    light.location = cn1.real, cn1.imag, random.uniform(1, 5)
    light.data.angle = random.uniform(0, math.pi * 5 / 180)
    light.constraints.clear()
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
    info["light_angle"] = light.data.angle

    infos.append(info)

    JSONData["light"] = infos

def cameraPos_shadow_inter_only(JSONData, objInfo):
    camera = bpy.data.objects['Camera1']
    bpy.context.scene.camera = camera

    cn1 = complex(objInfo[0][1].location[0], objInfo[0][1].location[1])
    cn2 = complex(objInfo[2][1].location[0], objInfo[2][1].location[1])
    deg = (cmath.polar(cn1)[1]+cmath.polar(cn2)[1])/2.0
    deg += random.uniform(-math.pi/12, math.pi/12)
    cn3 = cmath.rect(random.uniform(3, 5), deg)
    camera.location = cn3.real, cn3.imag, random.uniform(0.3, 3)

    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["tracked"]
    bpy.ops.object.add()
    tracked = bpy.context.selected_objects[0]
    tracked.location = random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), 0

    camera.constraints.clear()
    camera.constraints.new("TRACK_TO")
    camera.constraints[0].track_axis = "TRACK_NEGATIVE_Z"
    camera.constraints[0].up_axis = "UP_Y"
    camera.constraints[0].target = tracked

    info = {}
    x, y, z = camera.location
    info["location"] = {"x": x, "y": y, "z": z}
    x, y, z = tracked.location
    info["track_to"] = {"x": x, "y": y, "z": z}  # track_to的时候，欧拉角不可用
    x, y, z = camera.rotation_euler
    info["rotation_euler"] = {"x": x, "y": y, "z": z}
    x, y, z = camera.scale
    info["scale"] = {"x": x, "y": y, "z": z}

    info["clip"] = {"start": camera.data.clip_start, "end": camera.data.clip_end}
    info["lens"] = camera.data.lens

    JSONData["camera"] = info


####################################################################################
# 程序开始
####################################################################################

usl.enable_gpus("CUDA")

# 导入json配置
with open(current_dir+os.sep+'config.json', 'r') as f:
    config = json.load(f)

# obj文件夹路径
obj_root = config['path']['objects']
objList = usl.load_obj_paths(current_dir, obj_root)

times = config["indoor"]['output_amount']
# lightTypes = ["POINT", "SPOT", "AREA", "SUN"]
lightTypes = config["indoor"]["light types"]

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

    interOnly = config["indoor"]["shadow intersection dataset only"]
    noOverlap = config["indoor"]["no shadow overlap"]
    if interOnly and noOverlap:
        raise Exception("shadow intersection dataset only and no shadow overlap should not be true at the same time")

    while True:
        usl.remove_all_objects_from_collection(bpy.data.collections['items'])
        usl.remove_all_materials()
        # 随机生成3-5个物体

        if interOnly:
            objInfo = objLayout_shadow_inter_only(objList)
        elif noOverlap:
            objInfo = objLayout_shadow_no_overlap(objList)
        else:
            objInfo = usl.random3_5items(objList)
        if len(objInfo) > 0:
            break

    usl.objInfo2JSON(objInfo, JSONData, obj_root[0][:-len(obj_root[0].split("\\")[-1])])
    # 随机修改ground材质、光源
    change_ground_texture(JSONData)
    usl.remove_all_objects_from_collection(bpy.data.collections['light'])
    usl.remove_all_objects_from_collection(bpy.data.collections['tracked'])
    if interOnly:
        changeLight_shadow_inter_only(JSONData, objInfo)
        cameraPos_shadow_inter_only(JSONData, objInfo)
    elif noOverlap:
        changeLight_shadow_no_overlap(JSONData, objInfo)
        usl.randomCamera(JSONData)
    else:
        changeLight(JSONData, config["indoor"]['light_amount'])
        usl.randomCamera(JSONData)

    # 保存文件
    if not os.path.exists(outputUrl1):
        os.makedirs(outputUrl1)
    if config["indoor"]["save_blend"]:
        bpy.ops.wm.save_as_mainfile(filepath=outputUrl1+os.sep+str(now)+'.blend')

    # 渲染动画
    usl.render_animation()
    HandleResult(outputUrl, outputUrl1)

    usl.getCamMatrix(JSONData)
    with open(outputUrl1+os.sep+str(now)+'data.json', 'w') as f:
        json.dump(JSONData, f, indent=4)

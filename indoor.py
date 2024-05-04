# 构建合成数据集
import random
import os
import time
import pickle
import pathlib
import math
import sys
import json

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# 获取 main.py 的目录
current_dir = os.path.dirname(os.path.dirname(__file__))
print("current dir: "+current_dir)
sys.path.append(current_dir+os.sep+"utils")

from BlenderImageAndShadow import HandleResult

####################################################################################
# 函数定义
####################################################################################

# 读取模型目录
def load_obj_paths(obj_root):
    # 缓存obj文件夹路径
    if not os.path.exists(current_dir+os.sep+'obj_paths.pkl'):
        objList = list(obj_root.glob('**/*.obj'))
        print(objList)
        with open(current_dir+os.sep+'obj_paths.pkl', 'wb') as f:
            pickle.dump(objList, f)
    else:
        with open(current_dir+os.sep+'obj_paths.pkl', 'rb') as f:
            objList = pickle.load(f)
    return objList


# 删除某一集合中的所有物体
def remove_all_objects_from_collection(collection):
    # 遍历集合中的所有物体
    for obj in collection.objects:
        # 删除物体
        bpy.data.objects.remove(obj, do_unlink=True)


def remove_all_materials():
    for mat in bpy.data.materials:
        if mat.name.endswith("floor"):
            continue
        bpy.data.materials.remove(mat)


# 模型按最大比例缩放
def set_obj_scale_to_max_size(obj, max_size=1.0):
    # 获取物体边界框的尺寸
    dimensions = obj.dimensions
    # 计算最大维度
    max_dimension = max(dimensions)
    # 计算缩放比例
    scale_factor = max_size / max_dimension
    # 设置物体的缩放
    obj.scale = (scale_factor, scale_factor, scale_factor)


def worldBoundingBox(obj):
    """returns the corners of the bounding box of an object in world coordinates"""
    return [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]


def objectsOverlap(obj1, obj2):
    """returns True if the object's bounding boxes are overlapping"""
    vert1 = worldBoundingBox(obj1)
    vert2 = worldBoundingBox(obj2)
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7)]

    bvh1 = BVHTree.FromPolygons(vert1, faces)
    bvh2 = BVHTree.FromPolygons(vert2, faces)
    return bool(bvh1.overlap(bvh2))

# 随机选择3-5个模型，由于生成自阴影的方法需要同一个物体的两个一样的模型，所以数量翻倍
# objRet中，第n个（从0开始计数）物体的模型下标为2n和2n+1
def random3_5items(objList):
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["items"]
    objNum = random.randint(3, 5)
    objRet = []

    for i in range(objNum):
        # 随机选取1个obj文件
        obj_fname = random.choice(list(objList))
        bpy.ops.import_scene.obj(filepath=str(obj_fname))
        # 选中导入的物体
        obj = bpy.context.selected_objects[0]

        randomX = random.uniform(-1.5, 1.5)
        randomY = random.uniform(-1.5, 1.5)
        # 设置obj坐标
        obj.location = (randomX, randomY, 0)
        # 设置物体的缩放
        scale_size = random.uniform(0.3, 1.5)
        set_obj_scale_to_max_size(obj, max_size=scale_size)
        # 随机设置物体的旋转
        rotate = random.uniform(0, 2 * math.pi)
        obj.rotation_euler = 0, 0, rotate

        objRet.append([obj_fname, obj])

        # 以下是一模一样的第二个物体
        bpy.ops.import_scene.obj(filepath=str(obj_fname))
        obj = bpy.context.selected_objects[0]
        obj.location = (randomX, randomY, 0)
        set_obj_scale_to_max_size(obj, max_size=scale_size)
        obj.rotation_euler = 0, 0, rotate
        objRet.append([obj_fname, obj])

    addRenderFrame(objRet)

    for i in range(0, len(objRet), 2):
        for j in range(i+2, len(objRet), 2):
            if objectsOverlap(objRet[i][1], objRet[j][1]):
                return []

    return objRet


# 修改地面纹理
def change_ground_texture(JSONData):
    # 设置纹理文件夹路径
    texture_folder = config['texture_folder']
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


# 随机设置相机位置
def randomCamera(JSONData):
    # 随机选择Camera，Camera1，Camera2中的一个相机
    camera = random.choice([bpy.data.objects['Camera'], bpy.data.objects['Camera1'], bpy.data.objects['Camera2']])
    bpy.context.scene.camera = camera

    info = {}
    x, y, z = camera.location
    info["location"] = {"x": x, "y": y, "z": z}
    x, y, z = camera.rotation_euler
    info["rotation_euler"] = {"x": x, "y": y, "z": z}
    x, y, z = camera.scale
    info["scale"] = {"x": x, "y": y, "z": z}

    info["clip"] = {"start": camera.data.clip_start, "end": camera.data.clip_end}
    info["lens"] = camera.data.lens

    JSONData["camera"] = info


# 随机设置灯光
def changeLight(JSONData, max_light=4):
    remove_all_objects_from_collection(bpy.data.collections['light'])
    remove_all_objects_from_collection(bpy.data.collections['tracked'])

    lightNum = random.randint(1, max_light)
    lightTypes = ["POINT", "SPOT", "AREA"]
    hasSun = False

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


# 制作渲染帧，使得可以获得每个物体的阴影
def addRenderFrame(objInfo):
    ground = bpy.data.objects['ground']
    # 清除ground的动画
    ground.animation_data_clear()
    # 创建动画序列
    bpy.context.scene.render.fps = 1
    # 第0帧所有物体可见
    ground.is_shadow_catcher = False
    ground.visible_camera = True
    ground.visible_shadow = True
    ground.keyframe_insert(data_path="is_shadow_catcher", frame=0)
    ground.keyframe_insert(data_path="visible_camera", frame=0)
    ground.keyframe_insert(data_path="visible_shadow", frame=0)
    for obj in bpy.data.collections['items'].objects:
        obj.animation_data_clear()
        obj.visible_camera = True
        obj.visible_shadow = True
        obj.visible_diffuse = False
        obj.visible_glossy = False
        obj.pass_index = 1
        obj.is_holdout = False
        obj.is_shadow_catcher = False
        obj.keyframe_insert(data_path="visible_diffuse", frame=0)
        obj.keyframe_insert(data_path="visible_glossy", frame=0)
        obj.keyframe_insert(data_path="is_shadow_catcher", frame=0)
        obj.keyframe_insert(data_path="pass_index", frame=0)
        obj.keyframe_insert(data_path="visible_camera", frame=0)
        obj.keyframe_insert(data_path="visible_shadow", frame=0)
        obj.keyframe_insert(data_path="is_holdout", frame=0)
    for idx in range(1, len(objInfo), 2):
        [fname, obj] = objInfo[idx]
        obj.visible_camera = False
        obj.visible_shadow = False
        obj.pass_index = 0
        obj.keyframe_insert(data_path="visible_camera", frame=0)
        obj.keyframe_insert(data_path="visible_shadow", frame=0)
        obj.keyframe_insert(data_path="pass_index", frame=0)
    # 第1帧所有物体阴影消除
    for obj in bpy.data.collections['items'].objects:
        obj.visible_shadow = False
        obj.keyframe_insert(data_path="visible_shadow", frame=1)
    # 第2帧所有物体不可见
    for idx in range(0, len(objInfo), 2):
        [fname, obj] = objInfo[idx]
        obj.is_shadow_catcher = True
        obj.pass_index = 0
        obj.keyframe_insert(data_path="pass_index", frame=2)
        obj.keyframe_insert(data_path="is_shadow_catcher", frame=2)
    # 循环items集合中的所有物体，每隔一秒可见一个物体
    i = 3
    for idx in range(0, len(objInfo), 2):
        [fname, obj] = objInfo[idx]
        obj.pass_index = 1
        obj.keyframe_insert(data_path="pass_index", frame=i)
        obj.is_shadow_catcher = False
        obj.visible_shadow = True
        obj.keyframe_insert(data_path="is_shadow_catcher", frame=i)
        obj.keyframe_insert(data_path="visible_shadow", frame=i)
        ground.is_shadow_catcher = True
        ground.keyframe_insert(data_path="is_shadow_catcher", frame=i)
        
        obj.is_holdout = True
        obj.keyframe_insert(data_path="is_holdout", frame=i + 1)

        # 渲染自阴影
        [fname, obj2] = objInfo[idx+1]
        for idx_other in range(0, len(objInfo), 2):
            if idx_other == idx:
                continue
            # 防止自阴影被其他物体catch
            [fname, obj_other] = objInfo[idx_other]
            obj_other.is_shadow_catcher = False
            obj_other.is_holdout = True
            obj_other.keyframe_insert(data_path="is_shadow_catcher", frame=i + 2)
            obj_other.keyframe_insert(data_path="is_holdout", frame=i + 2)
        obj.is_shadow_catcher = True
        obj.is_holdout = False
        obj.keyframe_insert(data_path="is_shadow_catcher", frame=i + 2)
        obj.keyframe_insert(data_path="is_holdout", frame=i + 2)
        obj2.is_holdout = True
        obj2.visible_diffuse = True
        obj2.keyframe_insert(data_path="is_holdout", frame=i + 2)
        obj2.keyframe_insert(data_path="visible_diffuse", frame=i + 2)
        ground.is_shadow_catcher = False
        ground.visible_camera = False
        ground.visible_shadow = False
        ground.keyframe_insert(data_path="is_shadow_catcher", frame=i + 2)
        ground.keyframe_insert(data_path="visible_camera", frame=i + 2)
        ground.keyframe_insert(data_path="visible_shadow", frame=i + 2)

        # 设置本次的物体不可见，为下一个物体的渲染扫清障碍
        obj.is_shadow_catcher = True
        obj.visible_shadow = False
        obj.pass_index = 0
        ground.visible_camera = True
        ground.visible_shadow = True
        obj.keyframe_insert(data_path="pass_index", frame=i + 3)
        obj.keyframe_insert(data_path="is_shadow_catcher", frame=i + 3)
        obj.keyframe_insert(data_path="visible_shadow", frame=i + 3)
        ground.keyframe_insert(data_path="visible_camera", frame=i + 3)
        ground.keyframe_insert(data_path="visible_shadow", frame=i + 3)
        obj2.is_holdout = False
        obj2.visible_diffuse = False
        obj2.keyframe_insert(data_path="is_holdout", frame=i + 3)
        obj2.keyframe_insert(data_path="visible_diffuse", frame=i + 3)
        for idx_other in range(0, len(objInfo), 2):
            if idx_other == idx:
                continue
            [fname, obj_other] = objInfo[idx_other]
            obj_other.is_shadow_catcher = True
            obj_other.is_holdout = False
            obj_other.keyframe_insert(data_path="is_shadow_catcher", frame=i + 3)
            obj_other.keyframe_insert(data_path="is_holdout", frame=i + 3)

        i += 3

    fcurves = ground.animation_data.action.fcurves
    for fcurve in fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'CONSTANT'
    for obj in bpy.data.collections['items'].objects:
        fcurves = obj.animation_data.action.fcurves
        for fcurve in fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'CONSTANT'

    i -= 1
    bpy.context.scene.frame_end = i
    
    
# 渲染动画
def render_animation():
    # 渲染动画
    bpy.ops.render.render(animation=True)    


def objInfo2JSON(objInfo, JSONData, objRoot):
    infoList = []
    cnt = 0
    sz = len(objInfo)
    for idx in range(0, sz, 2):
        fname, obj = objInfo[idx]
        cnt += 1
        singleInfo = {}
        obj_path = str(fname)[len(str(objRoot)):]
        singleInfo["obj_path"] = obj_path

        # TODO: 硬编码nodes序号，可能会有错误，待观察
        tex_path = obj.active_material.node_tree.nodes[2].image.filepath
        tex_path = tex_path[tex_path.find(obj_path[:7]):]
        singleInfo["texture_path"] = tex_path

        x, y, z = obj.location
        singleInfo["location"] = {"x": x, "y": y, "z": z}
        x, y, z = obj.rotation_euler
        singleInfo["rotation_euler"] = {"x": x, "y": y, "z": z}
        x, y, z = obj.scale
        singleInfo["scale"] = {"x": x, "y": y, "z": z}
        x, y, z = obj.dimensions
        singleInfo["dimensions"] = {"x": x, "y": y, "z": z}
        infoList.append(singleInfo)

    JSONData["object_count"] = cnt
    JSONData["objects"] = infoList


def enable_gpus(device_type, use_cpus=False):
    preferences = bpy.context.preferences
    cycles_preferences = preferences.addons["cycles"].preferences
    cycles_preferences.refresh_devices()
    devices = cycles_preferences.devices

    if not devices:
        raise RuntimeError("Unsupported device type")

    activated_gpus = []
    for device in devices:
        if device.type == "CPU":
            device.use = use_cpus
        else:
            device.use = True
            activated_gpus.append(device.name)
            print('activated gpu', device.name)

    cycles_preferences.compute_device_type = device_type
    bpy.context.scene.cycles.device = "GPU"

    return activated_gpus


####################################################################################
# 程序开始
####################################################################################

enable_gpus("CUDA")

# 导入json配置
with open(current_dir+os.sep+'config.json', 'r') as f:
    config = json.load(f)
    
print('Google Scanned Objects dir:', config['google_research_url'])
# obj文件夹路径
obj_root = pathlib.Path(config['google_research_url'])
objList = load_obj_paths(obj_root)

# 切换当前工作目录到脚本所在的目录
os.chdir(current_dir)

times = config['output_amount']
# baseUrl
baseUrl = config['baseUrl']
bpy.context.scene.render.filepath = config['baseUrl'] + os.sep + "tmp" + os.sep
comp_node = bpy.context.scene.node_tree.nodes["file_output123"]
comp_node.base_path = config['baseUrl']
# outputUrl
outputUrl = config['outputUrl']
for i in range(times):
    # 获得时间戳
    now = int(time.time())
    JSONData = {}
    outputUrl1 = outputUrl + os.sep + str(now)
    print('baseUrl and outputUrl1:', baseUrl, outputUrl1, flush=True)

    while True:
        remove_all_objects_from_collection(bpy.data.collections['items'])
        remove_all_materials()
        # 随机生成3-5个物体
        objInfo = random3_5items(objList)
        if len(objInfo) > 0:
            break

    objInfo2JSON(objInfo, JSONData, obj_root)
    # 随机修改ground材质、光源
    change_ground_texture(JSONData)
    changeLight(JSONData, config['light_amount'])
    randomCamera(JSONData)
    # 保存文件
    if(not os.path.exists(outputUrl1)):
        os.makedirs(outputUrl1)
    if config["save_blend"]:
        bpy.ops.wm.save_as_mainfile(filepath=outputUrl1+os.sep+str(now)+'.blend')
    with open(outputUrl1+os.sep+str(now)+'data.json', 'w') as f:
        json.dump(JSONData, f, indent=4)

    # 渲染动画
    render_animation()
    HandleResult(baseUrl, outputUrl1)
    


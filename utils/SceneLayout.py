import pickle
import os
import random
import math
import cmath
import pathlib

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


# 读取模型目录
def load_obj_paths(project_root, obj_root):
    # 缓存obj文件夹路径
    if not os.path.exists(project_root+os.sep+'obj_paths.pkl'):
        objList = []
        cnt = 0
        for obj_path in obj_root:
            obj_type = obj_path.split("\\")[-1]
            objs = list(pathlib.Path(obj_path).glob('**/*.obj'))
            for obj in objs:
                objList.append([obj, obj_type, cnt]) # 路径，类型，id号
                cnt += 1
        print(objList)
        with open(project_root+os.sep+'obj_paths.pkl', 'wb') as f:
            pickle.dump(objList, f)
    else:
        with open(project_root+os.sep+'obj_paths.pkl', 'rb') as f:
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
        if mat.name.endswith("floor") or mat.name.endswith("ground") or mat.name.endswith("sky"):
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

        objRet.append([obj_fname, obj, obj_info[1], obj_info[2]])

        # 以下是一模一样的第二个物体
        bpy.ops.import_scene.obj(filepath=str(obj_fname))
        obj = bpy.context.selected_objects[0]
        obj.location = (randomX, randomY, 0)
        set_obj_scale_to_max_size(obj, max_size=scale_size)
        obj.rotation_euler = 0, 0, rotate
        objRet.append([obj_fname, obj, obj_info[1], obj_info[2]])

    addRenderFrame(objRet)

    for i in range(0, len(objRet), 2):
        for j in range(i+2, len(objRet), 2):
            if objectsOverlap(objRet[i][1], objRet[j][1]):
                return []

    return objRet


# 随机设置相机位置
def randomCamera(JSONData):

    camera = bpy.data.objects['Camera1']
    bpy.context.scene.camera = camera

    deg = random.uniform(-math.pi / 2, math.pi / 2)
    cn3 = cmath.rect(random.uniform(3.5, 5), deg)
    camera.location = cn3.real, cn3.imag, random.uniform(1, 5)

    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["tracked"]
    bpy.ops.object.add()
    tracked = bpy.context.selected_objects[0]
    tracked.location = random.uniform(-1, 1), random.uniform(-1, 1), 0

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


def getCamMatrix(JSONData):
    camera = bpy.context.scene.camera
    mat_list = []
    mat = camera.matrix_basis
    for i in range(4):
        lis = []
        for j in range(4):
            lis.append(mat[i][j])
        mat_list.append(lis)
    JSONData["camera"]["matrix_basis"] = mat_list

    mat_list = []
    mat = camera.matrix_local
    for i in range(4):
        lis = []
        for j in range(4):
            lis.append(mat[i][j])
        mat_list.append(lis)
    JSONData["camera"]["matrix_local"] = mat_list

    mat_list = []
    mat = camera.matrix_parent_inverse
    for i in range(4):
        lis = []
        for j in range(4):
            lis.append(mat[i][j])
        mat_list.append(lis)
    JSONData["camera"]["matrix_parent_inverse"] = mat_list

    mat_list = []
    mat = camera.matrix_world
    for i in range(4):
        lis = []
        for j in range(4):
            lis.append(mat[i][j])
        mat_list.append(lis)
    JSONData["camera"]["matrix_world"] = mat_list


# 制作渲染帧，使得可以获得每个物体的阴影
def addRenderFrame(objInfo):
    # 清除ground的动画
    for background in bpy.data.collections['Collection'].objects:
        background.animation_data_clear()
    # 创建动画序列
    bpy.context.scene.render.fps = 1
    # 第0帧所有物体可见
    for background in bpy.data.collections['Collection'].objects:
        background.is_shadow_catcher = False
        background.visible_camera = True
        background.visible_shadow = False
        if background.name_full == 'sky':
            background.visible_shadow = False
            background.visible_diffuse = False
            background.visible_glossy = False
            background.visible_transmission = False
            background.visible_volume_scatter = False
            background.keyframe_insert(data_path="visible_diffuse", frame=0)
            background.keyframe_insert(data_path="visible_glossy", frame=0)
            background.keyframe_insert(data_path="visible_transmission", frame=0)
            background.keyframe_insert(data_path="visible_volume_scatter", frame=0)
        background.keyframe_insert(data_path="is_shadow_catcher", frame=0)
        background.keyframe_insert(data_path="visible_camera", frame=0)
        background.keyframe_insert(data_path="visible_shadow", frame=0)
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
        [fname, obj] = objInfo[idx][:2]
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
        [fname, obj] = objInfo[idx][:2]
        obj.is_shadow_catcher = True
        obj.pass_index = 0
        obj.keyframe_insert(data_path="pass_index", frame=2)
        obj.keyframe_insert(data_path="is_shadow_catcher", frame=2)
    # 循环items集合中的所有物体，每隔一秒可见一个物体
    i = 3
    for idx in range(0, len(objInfo), 2):
        [fname, obj] = objInfo[idx][:2]
        obj.pass_index = 1
        obj.keyframe_insert(data_path="pass_index", frame=i)
        obj.is_shadow_catcher = False
        obj.visible_shadow = True
        obj.keyframe_insert(data_path="is_shadow_catcher", frame=i)
        obj.keyframe_insert(data_path="visible_shadow", frame=i)
        for background in bpy.data.collections['Collection'].objects:
            background.is_shadow_catcher = True
            background.keyframe_insert(data_path="is_shadow_catcher", frame=i)

        obj.is_holdout = True
        obj.keyframe_insert(data_path="is_holdout", frame=i + 1)

        # 渲染自阴影
        [fname, obj2] = objInfo[idx + 1][:2]
        for idx_other in range(0, len(objInfo), 2):
            if idx_other == idx:
                continue
            # 防止自阴影被其他物体catch
            [fname, obj_other] = objInfo[idx_other][:2]
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
        for background in bpy.data.collections['Collection'].objects:
            background.is_shadow_catcher = False
            background.visible_camera = False
            background.visible_shadow = False
            background.keyframe_insert(data_path="is_shadow_catcher", frame=i + 2)
            background.keyframe_insert(data_path="visible_camera", frame=i + 2)
            background.keyframe_insert(data_path="visible_shadow", frame=i + 2)

        # 设置本次的物体不可见，为下一个物体的渲染扫清障碍
        obj.is_shadow_catcher = True
        obj.visible_shadow = False
        obj.pass_index = 0
        obj.keyframe_insert(data_path="pass_index", frame=i + 3)
        obj.keyframe_insert(data_path="is_shadow_catcher", frame=i + 3)
        obj.keyframe_insert(data_path="visible_shadow", frame=i + 3)
        for background in bpy.data.collections['Collection'].objects:
            background.visible_camera = True
            background.visible_shadow = False
            if background.name_full == 'sky':
                background.visible_shadow = False
            background.keyframe_insert(data_path="visible_camera", frame=i + 3)
            background.keyframe_insert(data_path="visible_shadow", frame=i + 3)
        obj2.is_holdout = False
        obj2.visible_diffuse = False
        obj2.keyframe_insert(data_path="is_holdout", frame=i + 3)
        obj2.keyframe_insert(data_path="visible_diffuse", frame=i + 3)
        for idx_other in range(0, len(objInfo), 2):
            if idx_other == idx:
                continue
            [fname, obj_other] = objInfo[idx_other][:2]
            obj_other.is_shadow_catcher = True
            obj_other.is_holdout = False
            obj_other.keyframe_insert(data_path="is_shadow_catcher", frame=i + 3)
            obj_other.keyframe_insert(data_path="is_holdout", frame=i + 3)

        i += 3

    for background in bpy.data.collections['Collection'].objects:
        fcurves = background.animation_data.action.fcurves
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
        fname, obj, obj_type, obj_id = objInfo[idx]
        cnt += 1
        singleInfo = {}
        obj_path = str(fname)[len(str(objRoot)):]
        singleInfo["obj_path"] = obj_path

        # TODO: 硬编码nodes序号，可能会有错误，待观察
        tex_path = obj.active_material.node_tree.nodes[2].image.filepath
        tex_path = tex_path[tex_path.find(obj_path[:7]):]
        singleInfo["texture_path"] = tex_path
        singleInfo["obj_type"] = obj_type
        singleInfo["obj_id"] = obj_id

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


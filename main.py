# 构建合成数据集
import random
import os

import time
import bpy
import pickle
import pathlib
import math
import sys
import json

# 获取 main.py 的目录
current_dir = os.path.dirname(os.path.dirname(__file__))
print("current dir: "+current_dir)
sys.path.append(current_dir+"\\myutils")

from BlenderImageAndShadow import HandleResult

####################################################################################
# 函数定义
####################################################################################

# 读取模型目录
def load_obj_paths(obj_root):
    # 缓存obj文件夹路径
    if not os.path.exists(current_dir+'\\obj_paths.pkl'):
        objList = list(obj_root.glob('**/*.obj'))
        print(objList)
        with open(current_dir+'\\obj_paths.pkl', 'wb') as f:
            pickle.dump(objList, f)
    else:
        with open(current_dir+'\\obj_paths.pkl', 'rb') as f:
            objList = pickle.load(f)
    return objList


# 删除某一集合中的所有物体
def remove_all_objects_from_collection(collection):
    # 遍历集合中的所有物体
    for obj in collection.objects:
        # 删除物体
        bpy.data.objects.remove(obj, do_unlink=True)


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


# 随机选择3-5个模型
def random3_5items(objList):
    objNum = random.randint(3, 5)
    eachX = 3 / objNum
    eachY = 2 / objNum
    beforeX = 0
    beforeY = 0
    for i in range(objNum):
        # 随机选取1个obj文件
        obj_fname = random.choice(list(objList))
        bpy.ops.import_scene.obj(filepath=str(obj_fname))
        # 选中导入的物体
        obj = bpy.context.selected_objects[0]
        randomX = random.uniform(eachX * i, eachX * (i + 1)) + beforeX - 3
        randomY = random.uniform(eachY * i, eachY * (i + 1)) + beforeY - 1
        # 设置obj z=0，x=1.7，y=2
        obj.location = (randomX, randomY, 0)
        # 设置物体的缩放
        set_obj_scale_to_max_size(obj, max_size=random.uniform(0.1, 1))
        # 随机设置物体的旋转
        obj.rotation_euler = 0,0, random.uniform(0, 2 * math.pi)
        beforeX = obj.dimensions.x
        beforeY = obj.dimensions.y
        # 放入items集合
        # bpy.data.collections['items'].objects.link(obj)
    addRenderFrame()
    return objNum


# 修改地面纹理
def change_ground_texture():
    # 设置纹理文件夹路径
    texture_folder =  config['texture_folder']
    # 获取所有的.jpg文件
    jpg_files = [f for f in os.listdir(texture_folder) if f.lower().endswith('.jpg')]

    # 确保至少有一个.jpg文件
    if not jpg_files:
        raise Exception("No .jpg files found in directory")

    # 随机选择一个.jpg文件
    selected_file = random.choice(jpg_files)
    selected_file_path = os.path.join(texture_folder, selected_file)

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
def randomCamera():
    # 随机选择Camera，Camera1，Camera2中的一个相机
    camera = random.choice([bpy.data.objects['Camera'], bpy.data.objects['Camera1'], bpy.data.objects['Camera2']])
    bpy.context.scene.camera = camera


# 随机设置灯光
def changeLight():
    # 选中名为"left"的灯光
    light = bpy.data.objects['left']
    # 随机设置灯光的强度为50到200之间的值
    light.data.energy = random.uniform(200, 400)

    light.location = random.uniform(-4.5, 1.5), random.uniform(-2.5, 2.5), random.uniform(0.5, 5)


# 制作渲染帧，使得可以获得每个物体的阴影
def addRenderFrame():
    ground = bpy.data.objects['ground']
    # 清除ground的动画
    ground.animation_data_clear()
    # 创建动画序列
    bpy.context.scene.render.fps = 1
    # 第0帧所有物体可见
    for k, obj in enumerate(bpy.data.collections['items'].all_objects):
        obj.visible_camera = True
        obj.visible_shadow = True
        obj.visible_diffuse = False
        obj.visible_glossy = False
        obj.pass_index = 1
        ground.is_shadow_catcher = False
        ground.keyframe_insert(data_path="is_shadow_catcher", frame=0)
        obj.keyframe_insert(data_path="visible_diffuse", frame=0)
        obj.keyframe_insert(data_path="visible_glossy", frame=0)
        obj.keyframe_insert(data_path="pass_index", frame=0)
        obj.keyframe_insert(data_path="visible_camera", frame=0)
        obj.keyframe_insert(data_path="visible_shadow", frame=0)
    # 第1帧所有物体不可见
    for k, obj in enumerate(bpy.data.collections['items'].all_objects):
        obj.visible_camera = False
        obj.visible_shadow = False
        obj.pass_index = 0
        obj.keyframe_insert(data_path="pass_index", frame=1)
        obj.keyframe_insert(data_path="visible_camera", frame=1)
        obj.keyframe_insert(data_path="visible_shadow", frame=1)
    # 循环items集合中的所有物体，每隔一秒可见一个物体
    i = 1
    for k, obj in enumerate(bpy.data.collections['items'].all_objects):
        obj.visible_camera = False
        obj.visible_shadow = False

        obj.keyframe_insert(data_path="visible_camera", frame=i)
        obj.keyframe_insert(data_path="visible_shadow", frame=i)
        obj.pass_index = 1
        obj.keyframe_insert(data_path="pass_index", frame=i+1)
        obj.visible_camera = True
        obj.visible_shadow = True
        obj.keyframe_insert(data_path="visible_camera", frame=i + 1)
        obj.keyframe_insert(data_path="visible_shadow", frame=i + 1)
        ground.is_shadow_catcher = True
        ground.keyframe_insert(data_path="is_shadow_catcher", frame=i + 2)
        obj.visible_camera = False
        ground.is_shadow_catcher = False
        ground.keyframe_insert(data_path="is_shadow_catcher", frame=i + 3)
        obj.keyframe_insert(data_path="visible_camera", frame=i + 3)
        obj.keyframe_insert(data_path="visible_shadow", frame=i + 3)
        obj.visible_camera = True
        obj.visible_shadow = False
        obj.pass_index = 1
        obj.keyframe_insert(data_path="pass_index", frame=i + 4)
        obj.keyframe_insert(data_path="visible_camera", frame=i + 4)
        obj.keyframe_insert(data_path="visible_shadow", frame=i + 4)
        obj.visible_camera = False
        obj.pass_index = 0

        obj.keyframe_insert(data_path="pass_index", frame=i + 5)
        obj.keyframe_insert(data_path="visible_camera", frame=i + 5)
        obj.keyframe_insert(data_path="visible_shadow", frame=i + 5)
        i += 4
    bpy.context.scene.frame_end = i
    
    
# 渲染动画
def render_animation():
    # 渲染动画
    bpy.ops.render.render(animation=True)    


####################################################################################
# 程序开始
####################################################################################


# 导入json配置
with open(current_dir+'\\config.json', 'r') as f:
    config = json.load(f)
    
print('Google Scanned Objects dir:',config['google_research_url'])
# obj文件夹路径
obj_root = pathlib.Path(config['google_research_url'])
objList = load_obj_paths(obj_root)

randomCamera()

# 切换当前工作目录到脚本所在的目录
os.chdir(current_dir)

times = 10
# baseUrl
baseUrl = config['baseUrl']
# outputUrl
outputUrl = config['outputUrl']
for i in range(times):
    # 获得时间戳
    now = int(time.time())
    outputUrl1 = outputUrl + '\\' + str(now)
    print('baseUrl and outputUrl1:',baseUrl, outputUrl1)
    remove_all_objects_from_collection(bpy.data.collections['items'])
    # 随机生成3-5个物体
    random3_5items(objList)
    # 随机修改ground材质、光源
    change_ground_texture()
    changeLight()
    # 保存.blend文件
    if(not os.path.exists(outputUrl1)):
        os.makedirs(outputUrl1)
    bpy.ops.wm.save_as_mainfile(filepath=outputUrl1+'.blend')
    # 渲染动画
    render_animation()
    HandleResult(baseUrl, outputUrl1)

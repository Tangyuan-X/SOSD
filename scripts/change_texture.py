import bpy
import os
import random
import json
# 导入json配置
with open('../config.json', 'r') as f:
    config = json.load(f)

def change_ground_texture():
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

change_ground_texture()
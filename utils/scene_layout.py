import pickle
import os
import random
import math
import cmath
import pathlib
import hashlib

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def load_obj_paths(project_root: str, obj_root: list[str]):
    """
    Read all the paths of objects. Cache them as obj_paths.pkl, so it can be used next time.
    The type of objects depends on the last folder's name of obj_root.
    The id of objects is its model file's md5.
    :param project_root: the root path of this project
    :param obj_root: the root paths of obj
    :return: list[list]: each element is [obj's path, obj's type, obj's id]
    """
    if not os.path.exists(project_root+os.sep+'obj_paths.pkl'):
        obj_list = []
        for obj_path in obj_root:
            obj_type = obj_path.split(os.sep)[-1]
            objs = list(pathlib.Path(obj_path).glob('**/*.obj'))
            for obj in objs:
                with open(obj, "rb") as f:
                    md5_hash = hashlib.md5()
                    for chunk in iter(lambda: f.read(4096), b""):
                        md5_hash.update(chunk)

                obj_list.append([obj, obj_type, md5_hash.hexdigest()])  # path，type，id
        with open(project_root+os.sep+'obj_paths.pkl', 'wb') as f:
            pickle.dump(obj_list, f)
    else:
        with open(project_root+os.sep+'obj_paths.pkl', 'rb') as f:
            obj_list = pickle.load(f)
    return obj_list


def change_ground_texture(json_data: dict, config: dict):
    """
    Randomly choose a ground texture (jpg) in indoor scene, from folder "config['path']['ground_texture']"
    :param json_data: data of the scene's layout config
    :param config: the data of "root/config.json"
    :return: None
    """

    texture_folder = config['path']['ground_texture']
    # all jpg files
    jpg_files = [f for f in os.listdir(texture_folder) if f.lower().endswith('.jpg')]

    if not jpg_files:
        raise Exception("No .jpg files found in directory")

    selected_file = random.choice(jpg_files)
    selected_file_path = os.path.join(texture_folder, selected_file)
    json_data["ground_texture_path"] = str(selected_file)

    if "ground" not in bpy.data.objects:
        raise Exception("Object 'ground' not found")

    ground_object = bpy.data.objects['ground']

    if not ground_object.data.materials:
        raise Exception("Object 'ground' has no materials")

    # get Principled BSDF node
    material = ground_object.data.materials[0]
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled_bsdf_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
    if principled_bsdf_node is None:
        raise Exception("Principled BSDF node not found in material of object 'ground'")

    for link in material.node_tree.links:
        if link.to_node == principled_bsdf_node and link.to_socket.name == 'Base Color':
            material.node_tree.links.remove(link)

    texture_node = nodes.new('ShaderNodeTexImage')
    texture_node.image = bpy.data.images.load(selected_file_path)
    material.node_tree.links.new(principled_bsdf_node.inputs['Base Color'], texture_node.outputs['Color'])

    print(f"Base color of material '{material.name}' of object 'ground' has been updated with '{selected_file}'")


def change_hdri(json_data: dict, config: dict):
    """
    Randomly choose a hdri texture in outdoor scene, from folder "config["path"]['hdri_texture']"
    :param json_data: data of the scene's layout config
    :param config: the data of "root/config.json"
    :return: None
    """

    hdri_folder = config["path"]['hdri_texture']
    exr_files = [f for f in os.listdir(hdri_folder) if f.lower().endswith('.exr')]

    if not exr_files:
        raise Exception("No .exr files found in directory")

    selected_file = random.choice(exr_files)
    selected_file_path = os.path.join(hdri_folder, selected_file)
    json_data["hdri_texture_path"] = str(selected_file)

    if "ground" not in bpy.data.objects:
        raise Exception("Object 'sphere' not found")

    if "sky" not in bpy.data.objects:
        raise Exception("Object 'sky' not found")

    ground = bpy.data.objects['ground']
    sky = bpy.data.objects['sky']

    if not ground.data.materials:
        raise Exception("Object 'sphere' has no materials")
    if not sky.data.materials:
        raise Exception("Object 'sphere' has no materials")

    # get Principled BSDF node
    material = ground.data.materials[0]
    material.use_nodes = True
    nodes = material.node_tree.nodes
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


def remove_all_objects_from_collection(collection):
    """
    Remove all objects in this collection.
    :param collection: object collection in blender
    :return: None
    """
    for obj in collection.objects:
        bpy.data.objects.remove(obj, do_unlink=True)


def remove_all_obj_materials():
    """
    Remove all materials of objects. Except the materials of ground, floor, sky, etc..
    :return: None
    """
    for mat in bpy.data.materials:
        if mat.name.endswith("floor") or mat.name.endswith("ground") or mat.name.endswith("sky"):
            continue
        bpy.data.materials.remove(mat)


def set_obj_scale_to_max_dim(obj, max_dim=1.0):
    """
    Set the maximum of object's dimensions to a specific number.
    For example, using max_dix = 1.0, [0.2, 0.3, 0.5] will be set to [0.4, 0.6, 1.0].
    And using max_dix = 2.0, [0.5, 0.1, 0.4] will be set to [2.0, 0.4, 1.6]
    :param obj: the object you want to resize
    :param max_dim:
    :return: None
    """
    dimensions = obj.dimensions
    max_dimension = max(dimensions)
    scale_factor = max_dim / max_dimension
    obj.scale = (scale_factor, scale_factor, scale_factor)


def world_bounding_box(obj):
    """
    returns the corners of the bounding box of an object in world coordinates
    :param obj: the object
    :return: list: the corners of the bounding box
    """
    return [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]


def objects_overlap(obj1, obj2):
    """
    returns True if the object's bounding boxes are overlapping
    :param obj1: first object
    :param obj2: second object
    :return: Bool: True if the object's bounding boxes are overlapping
    """

    vert1 = world_bounding_box(obj1)
    vert2 = world_bounding_box(obj2)
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7)]

    bvh1 = BVHTree.FromPolygons(vert1, faces)
    bvh2 = BVHTree.FromPolygons(vert2, faces)
    return bool(bvh1.overlap(bvh2))


def random_items(obj_list: list[list], min_count=3, max_count=5):
    """
    Randomly add objects in indoor scene.
    To generate self-shadow, there are two objs using the same model(they also have same location, rotation, etc.).
    So the i-th model's objs have index 2*i and 2*i+1 (starting from 0).
    :param obj_list: the return of load_obj_paths
    :param min_count: the minimum count of objects
    :param max_count: the maximum count of objects
    :return: list[list]: each element is [file's name of the obj model,
                                              obj its self,
                                              type of the obj model,
                                              id of the obj model]
    """

    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["items"]
    obj_num = random.randint(min_count, max_count)
    obj_ret = []

    for i in range(obj_num):
        obj_info = random.choice(list(obj_list))
        obj_fname = obj_info[0]
        bpy.ops.import_scene.obj(filepath=str(obj_fname))
        obj = bpy.context.selected_objects[0]

        # set Specular and Alpha to 0, prevent shadow images from blending with their textures
        material = obj.data.materials[0]
        nodes = material.node_tree.nodes
        principled_bsdf_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
        principled_bsdf_node.inputs['Specular'].default_value = 0.0
        principled_bsdf_node.inputs['Alpha'].default_value = 1.0

        random_x = random.uniform(-1.5, 1.5)
        random_y = random.uniform(-1.5, 1.5)
        obj.location = (random_x, random_y, 0)
        scale_size = random.uniform(0.3, 1.5)
        set_obj_scale_to_max_dim(obj, max_dim=scale_size)
        rotate = random.uniform(0, 2 * math.pi)
        obj.rotation_euler = 0, 0, rotate

        obj_ret.append([obj_fname, obj, obj_info[1], obj_info[2]])

        # the next obj is as same as the previous, just use to generate self-shadow images
        bpy.ops.import_scene.obj(filepath=str(obj_fname))
        obj = bpy.context.selected_objects[0]
        obj.location = (random_x, random_y, 0)
        set_obj_scale_to_max_dim(obj, max_dim=scale_size)
        obj.rotation_euler = 0, 0, rotate
        obj_ret.append([obj_fname, obj, obj_info[1], obj_info[2]])

    add_render_frame(obj_ret)

    for i in range(0, len(obj_ret), 2):
        for j in range(i+2, len(obj_ret), 2):
            if objects_overlap(obj_ret[i][1], obj_ret[j][1]):
                return []

    return obj_ret


def obj_layout_shadow_inter_only(obj_list: list[list]):
    """
    Randomly add objects in indoor scene(shadow intersection only). Exactly two models will be added.
    To generate self-shadow, there are two objs using the same model(they also have same location, rotation, etc.).
    So the i-th model's objs have index 2*i and 2*i+1 (starting from 0).
    :param obj_list: the return of load_obj_paths
    :return: list[list]: each element is [file's name of the obj model,
                                          obj its self,
                                          type of the obj model,
                                          id of the obj model]
             there are exactly two elements in this list
    """

    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["items"]
    obj_ret = []

    obj_info = random.choice(list(obj_list))
    obj_file_name = obj_info[0]
    bpy.ops.import_scene.obj(filepath=str(obj_file_name))
    # select the imported obj
    obj = bpy.context.selected_objects[0]

    # set Specular and Alpha to 0, prevent shadow images from blending with their textures
    for material in obj.data.materials:
        nodes = material.node_tree.nodes
        principled_bsdf_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
        principled_bsdf_node.inputs['Specular'].default_value = 0.0
        principled_bsdf_node.inputs['Alpha'].default_value = 1.0

    cn = cmath.rect(random.uniform(0.3, 0.8), random.uniform(math.pi*2/3, math.pi) + random.randint(0, 1)*math.pi)
    random_x = cn.real
    random_y = cn.imag
    obj.location = (random_x, random_y, 0)
    scale_size = random.uniform(0.3, 1.5)
    set_obj_scale_to_max_dim(obj, max_dim=scale_size)
    rotate = random.uniform(0, 2 * math.pi)
    obj.rotation_euler = 0, 0, rotate

    obj_ret.append([obj_file_name, obj, obj_info[1], obj_info[2]])

    # the next obj is as same as the previous, just use to generate self-shadow images
    bpy.ops.import_scene.obj(filepath=str(obj_file_name))
    obj = bpy.context.selected_objects[0]
    obj.location = (random_x, random_y, 0)
    set_obj_scale_to_max_dim(obj, max_dim=scale_size)
    obj.rotation_euler = 0, 0, rotate
    obj_ret.append([obj_file_name, obj, obj_info[1], obj_info[2]])

    # set the second model
    # this two models will form a specific angle, in order to make shadows cross
    cn = complex(random_x, random_y)
    radius, deg = cmath.polar(cn)
    cn1 = cmath.rect(radius+random.uniform(-0.2, 0.2), deg+random.uniform(math.pi/3, math.pi/2))
    obj_info = random.choice(list(obj_list))
    obj_file_name = obj_info[0]
    bpy.ops.import_scene.obj(filepath=str(obj_file_name))

    obj = bpy.context.selected_objects[0]

    for material in obj.data.materials:
        nodes = material.node_tree.nodes
        principled_bsdf_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
        principled_bsdf_node.inputs['Specular'].default_value = 0.0
        principled_bsdf_node.inputs['Alpha'].default_value = 1.0

    random_x = cn1.real
    random_y = cn1.imag
    obj.location = (random_x, random_y, 0)
    scale_size = random.uniform(0.3, 1.5)
    set_obj_scale_to_max_dim(obj, max_dim=scale_size)
    rotate = random.uniform(0, 2 * math.pi)
    obj.rotation_euler = 0, 0, rotate

    obj_ret.append([obj_file_name, obj, obj_info[1], obj_info[2]])

    # the next obj is as same as the previous, just use to generate self-shadow images
    bpy.ops.import_scene.obj(filepath=str(obj_file_name))
    obj = bpy.context.selected_objects[0]
    obj.location = (random_x, random_y, 0)
    set_obj_scale_to_max_dim(obj, max_dim=scale_size)
    obj.rotation_euler = 0, 0, rotate
    obj_ret.append([obj_file_name, obj, obj_info[1], obj_info[2]])

    add_render_frame(obj_ret)

    for i in range(0, len(obj_ret), 2):
        if obj_ret[i][1].dimensions[2] < 0.3:
            # obj is too low to make the shadow long enough
            return []
        for j in range(i + 2, len(obj_ret), 2):
            if objects_overlap(obj_ret[i][1], obj_ret[j][1]):
                return []

    return obj_ret


def obj_layout_shadow_no_overlap(obj_list: list[list], min_count=3, max_count=5):
    """
    Randomly add objects in indoor scene. Use a different placing algorithm to prevent shadows
    from overlapping with other shadows and objects.
    To generate self-shadow, there are two objs using the same model(they also have same location, rotation, etc.).
    So the i-th model's objs have index 2*i and 2*i+1 (starting from 0).
    :param obj_list: the return of load_obj_paths
    :param min_count: the minimum count of objects
    :param max_count: the maximum count of objects
    :return: list[list]: each element is [file's name of the obj model,
                                              obj its self,
                                              type of the obj model,
                                              id of the obj model]
    """
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["items"]
    obj_num = random.randint(min_count, max_count)
    obj_ret = []

    deg = random.uniform(0, 2*math.pi)
    # deg = 0.0

    for i in range(obj_num):
        obj_info = random.choice(list(obj_list))
        obj_fname = obj_info[0]
        bpy.ops.import_scene.obj(filepath=str(obj_fname))
        obj = bpy.context.selected_objects[0]

        # set Specular and Alpha to 0, prevent shadow images from blending with their textures
        for material in obj.data.materials:
            nodes = material.node_tree.nodes
            principled_bsdf_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
            principled_bsdf_node.inputs['Specular'].default_value = 0.0
            principled_bsdf_node.inputs['Alpha'].default_value = 1.0

        cn = cmath.rect(random.uniform(-0.4*obj_num, 0.4*obj_num), deg+random.uniform(-math.pi/6, math.pi/6))
        random_x = cn.real
        random_y = cn.imag
        obj.location = (random_x, random_y, 0)
        scale_size = random.uniform(max(1.5-0.2*obj_num, 0.5), max(2.0-0.2*obj_num, 0.7))
        set_obj_scale_to_max_dim(obj, max_dim=scale_size)
        rotate = random.uniform(0, 2 * math.pi)
        obj.rotation_euler = 0, 0, rotate

        obj_ret.append([obj_fname, obj, obj_info[1], obj_info[2]])

        # the next obj is as same as the previous, just use to generate self-shadow images
        bpy.ops.import_scene.obj(filepath=str(obj_fname))
        obj = bpy.context.selected_objects[0]
        for material in obj.data.materials:
            nodes = material.node_tree.nodes
            principled_bsdf_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
            principled_bsdf_node.inputs['Specular'].default_value = 0.0
            principled_bsdf_node.inputs['Alpha'].default_value = 1.0
        obj.location = (random_x, random_y, 0)
        set_obj_scale_to_max_dim(obj, max_dim=scale_size)
        obj.rotation_euler = 0, 0, rotate
        obj_ret.append([obj_fname, obj, obj_info[1], obj_info[2]])

    add_render_frame(obj_ret)

    for i in range(0, len(obj_ret), 2):
        if obj_ret[i][1].dimensions[2] < 0.3:
            # object is too low
            return []
        for j in range(i + 2, len(obj_ret), 2):
            if objects_overlap(obj_ret[i][1], obj_ret[j][1]):
                return []

    return obj_ret


def change_light(json_data: dict, max_light=4, light_types=None):
    """
    Randomly add lights in indoor scene. The type of lights is from a global var "light_types"
    :param json_data: data of the scene's layout config
    :param max_light: the maximum amount of lights
    :param light_types: the type of lights you want to use in blender.
                        if 'None', using ["POINT", "SUN", "SPOT", "AREA"]
    :return: None
    """

    if light_types is None:
        light_types = ["POINT", "SUN", "SPOT", "AREA"]
    light_num = random.randint(1, max_light)

    infos = []
    for i in range(light_num):
        ltype = random.choice(light_types)
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

    json_data["light"] = infos


def change_light_shadow_inter_only(json_data: dict, obj_info: list[list]):
    """
    Randomly add two 'POINT' light in indoor scene(shadow intersection only).
    One is behind obj 1, the other is behind object 2
    :param json_data: data of the scene's layout config
    :param obj_info: the return of obj_layout_shadow_inter_only
    :return: None
    """

    light_num = 2
    infos = []
    for i in range(light_num):
        ltype = "POINT"
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["light"]
        bpy.ops.object.light_add(type=ltype)
        light = bpy.context.selected_objects[0]
        light.hide_render = False
        light.hide_viewport = False

        light.data.energy = random.uniform(300, 350)
        obj = obj_info[i * 2][1]
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

    json_data["light"] = infos


def change_light_shadow_no_overlap(json_data: dict, obj_info: list[list]):
    """
    Randomly add only one 'SUN' light, to prevent shadows from overlapping with other shadows and objects.
    :param json_data: data of the scene's layout config
    :param obj_info: the return of usl.obj_layout_shadow_no_overlap
    :return: None
    """

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

    obj = obj_info[0][1]
    cn = complex(obj.location[0], obj.location[1])
    radius, deg = cmath.polar(cn)
    radius = random.uniform(4, 7) * random.choice([-1, 1])
    deg = deg + math.pi/2 + random.uniform(-math.pi / 24, math.pi / 24)
    cn1 = cmath.rect(radius, deg)
    tracked.location = cn1.real, cn1.imag, 0
    cn1 = cmath.rect(-radius, deg)

    light.data.energy = random.uniform(3, 8)
    light.location = cn1.real, cn1.imag, random.uniform(1, 5)
    light.data.angle = random.uniform(0, math.pi * 2.5 / 180)
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

    json_data["light"] = infos


# 随机设置相机位置
def random_camera(json_data: dict, obj_info: list[list], camera_min_r=3.5, camera_max_r=5, camera_min_z=1, camera_max_z=5):
    """
    Randomly place a camera.
    :param json_data: data of the scene's layout config
    :param obj_info: the return of random_items or other variants
    :param camera_min_r: the minimum distance from origin to the camera, in x-y plane
    :param camera_max_r: the maximum distance from origin to the camera, in x-y plane
    :param camera_min_z: the minimum z coordinate of the camera
    :param camera_max_z: the maximum z coordinate of the camera
    :return: None
    """

    camera = bpy.data.objects['Camera1']
    bpy.context.scene.camera = camera

    deg = random.uniform(-math.pi / 2, math.pi / 2)
    cn3 = cmath.rect(random.uniform(camera_min_r, camera_max_r), deg)
    camera.location = cn3.real, cn3.imag, random.uniform(camera_min_z, camera_max_z)

    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["tracked"]
    bpy.ops.object.add()
    tracked = bpy.context.selected_objects[0]
    # obj1 = random.choice(objInfo)[1]
    # tracked.location = obj1.location[0]+random.uniform(-0.1, 0.1), obj1.location[1]+random.uniform(-0.1, 0.1), 0
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
    info["track_to"] = {"x": x, "y": y, "z": z}  # when "track_to" is on，"rotation_euler" is invalid
    x, y, z = camera.rotation_euler
    info["rotation_euler"] = {"x": x, "y": y, "z": z}
    x, y, z = camera.scale
    info["scale"] = {"x": x, "y": y, "z": z}

    info["clip"] = {"start": camera.data.clip_start, "end": camera.data.clip_end}
    info["lens"] = camera.data.lens

    info["shift"] = {"x": camera.data.shift_x, "y": camera.data.shift_y}

    info["sensor"] = {"fit": camera.data.sensor_fit,
                      "height": camera.data.sensor_height,
                      "width": camera.data.sensor_width}

    json_data["camera"] = info


def random_camera_no_overlap(json_data: dict, obj_info: list[list], camera_min_z=1, camera_max_z=5, camera_min_deg=0,
                             camera_max_deg=2 * math.pi):
    """
    Randomly place a camera (for shadow no overlapping case).
    :param json_data: data of the scene's layout config
    :param obj_info: the return of random_items or other variants
    :param camera_min_z: the minimum z coordinate of the camera
    :param camera_max_z: the maximum z coordinate of the camera
    :param camera_min_deg: the minimum theta of the camera in polar coordinate. x-y plane
    :param camera_max_deg: the maximum theta of the camera in polar coordinate. x-y plane
    :return: None
    """
    camera = bpy.data.objects['Camera1']
    bpy.context.scene.camera = camera

    deg = random.uniform(camera_min_deg, camera_max_deg)
    sz = len(obj_info) // 2
    camera_min_r, camera_max_r = sz*0.7, sz*1.1
    cn3 = cmath.rect(random.uniform(camera_min_r, camera_max_r), deg)
    camera.location = cn3.real, cn3.imag, random.uniform(camera_min_z, camera_max_z)

    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["tracked"]
    bpy.ops.object.add()
    tracked = bpy.context.selected_objects[0]
    obj1 = obj_info[0][1]
    min_dis2 = 1e9
    for fname, obj, obj_type, obj_id in obj_info:
        x, y, z = obj.location
        dis2 = x*x+y*y
        if dis2 > min_dis2:
            min_dis2 = dis2
            obj1 = obj
    tracked.location = obj1.location[0]+random.uniform(-0.1, 0.1), obj1.location[1]+random.uniform(-0.1, 0.1), 0
    # tracked.location = random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), 0

    camera.constraints.clear()
    camera.constraints.new("TRACK_TO")
    camera.constraints[0].track_axis = "TRACK_NEGATIVE_Z"
    camera.constraints[0].up_axis = "UP_Y"
    camera.constraints[0].target = tracked

    info = {}
    x, y, z = camera.location
    info["location"] = {"x": x, "y": y, "z": z}
    x, y, z = tracked.location
    info["track_to"] = {"x": x, "y": y, "z": z}  # when "track_to" is on，"rotation_euler" is invalid
    x, y, z = camera.rotation_euler
    info["rotation_euler"] = {"x": x, "y": y, "z": z}
    x, y, z = camera.scale
    info["scale"] = {"x": x, "y": y, "z": z}

    info["clip"] = {"start": camera.data.clip_start, "end": camera.data.clip_end}
    info["lens"] = camera.data.lens

    info["shift"] = {"x": camera.data.shift_x, "y": camera.data.shift_y}

    info["sensor"] = {"fit": camera.data.sensor_fit,
                      "height": camera.data.sensor_height,
                      "width": camera.data.sensor_width}

    json_data["camera"] = info


def camera_pos_shadow_inter_only(json_data: dict, obj_info: list[list]):
    """
    Randomly place a camera to capture the shadow intersection.
    :param json_data: data of the scene's layout config
    :param obj_info: the return of obj_layout_shadow_inter_only
    :return: None
    """

    camera = bpy.data.objects['Camera1']
    bpy.context.scene.camera = camera

    cn1 = complex(obj_info[0][1].location[0], obj_info[0][1].location[1])
    cn2 = complex(obj_info[2][1].location[0], obj_info[2][1].location[1])
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
    info["track_to"] = {"x": x, "y": y, "z": z}  # when "track_to" is on, "rotation_euler" is invalid.
    x, y, z = camera.rotation_euler
    info["rotation_euler"] = {"x": x, "y": y, "z": z}
    x, y, z = camera.scale
    info["scale"] = {"x": x, "y": y, "z": z}

    info["clip"] = {"start": camera.data.clip_start, "end": camera.data.clip_end}
    info["lens"] = camera.data.lens

    json_data["camera"] = info


def get_img_output_param(json_data: dict):
    """
    Get blender's settings of "resolution" and "pixel_aspect". Write to json_data.
    :param json_data: data of the scene's layout config
    :return: None
    """
    json_data["output_param"] = {
        "resolution": {
            "x": bpy.context.scene.render.resolution_x,
            "y": bpy.context.scene.render.resolution_y,
            "percentage": bpy.context.scene.render.resolution_percentage
        },
        "pixel_aspect": {
            "x": bpy.context.scene.render.pixel_aspect_x,
            "y": bpy.context.scene.render.pixel_aspect_y
        }
    }


def add_render_frame(obj_info: list[list]):
    """
    Add render frame to generate the output images. Such as origin img, shadow-free img, shadow soft mask, etc.
    :param obj_info: the return of random_items or other variants
    :return: None
    """

    for background in bpy.data.collections['Collection'].objects:
        background.animation_data_clear()
    bpy.context.scene.render.fps = 1
    # frame 0, every object and background is visible
    for background in bpy.data.collections['Collection'].objects:
        background.is_shadow_catcher = False
        background.visible_camera = True
        background.visible_shadow = False
        background.is_holdout = False
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
        background.keyframe_insert(data_path="is_holdout", frame=0)
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
    for idx in range(1, len(obj_info), 2):
        [fname, obj] = obj_info[idx][:2]
        obj.visible_camera = False
        obj.visible_shadow = False
        obj.pass_index = 0
        obj.keyframe_insert(data_path="visible_camera", frame=0)
        obj.keyframe_insert(data_path="visible_shadow", frame=0)
        obj.keyframe_insert(data_path="pass_index", frame=0)
    # frame 1, every object is not casting shadow
    for obj in bpy.data.collections['items'].objects:
        obj.visible_shadow = False
        obj.keyframe_insert(data_path="visible_shadow", frame=1)
    # frame 2, every object is not visible
    for idx in range(0, len(obj_info), 2):
        [fname, obj] = obj_info[idx][:2]
        obj.is_shadow_catcher = True
        obj.pass_index = 0
        obj.keyframe_insert(data_path="pass_index", frame=2)
        obj.keyframe_insert(data_path="is_shadow_catcher", frame=2)
    # iterate every object，each frame only one object is visible
    i = 3
    for idx in range(0, len(obj_info), 2):  # there are two same objs for a model
        [fname, obj] = obj_info[idx][:2]
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

        # render self-shadow
        [fname, obj2] = obj_info[idx + 1][:2]
        for idx_other in range(0, len(obj_info), 2):
            if idx_other == idx:
                continue
            # prevent self-shadow from caught by other objs
            [fname, obj_other] = obj_info[idx_other][:2]
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
            background.is_holdout = True
            background.visible_shadow = False
            background.keyframe_insert(data_path="is_shadow_catcher", frame=i + 2)
            background.keyframe_insert(data_path="is_holdout", frame=i + 2)
            background.keyframe_insert(data_path="visible_shadow", frame=i + 2)

        # set this obj not visible, and then render next obj
        obj.is_shadow_catcher = True
        obj.visible_shadow = False
        obj.pass_index = 0
        obj.keyframe_insert(data_path="pass_index", frame=i + 3)
        obj.keyframe_insert(data_path="is_shadow_catcher", frame=i + 3)
        obj.keyframe_insert(data_path="visible_shadow", frame=i + 3)
        for background in bpy.data.collections['Collection'].objects:
            background.visible_shadow = False
            background.is_holdout = False
            if background.name_full == 'sky':
                background.visible_shadow = False
            background.keyframe_insert(data_path="visible_shadow", frame=i + 3)
            background.keyframe_insert(data_path="is_holdout", frame=i + 3)
        obj2.is_holdout = False
        obj2.visible_diffuse = False
        obj2.keyframe_insert(data_path="is_holdout", frame=i + 3)
        obj2.keyframe_insert(data_path="visible_diffuse", frame=i + 3)
        for idx_other in range(0, len(obj_info), 2):
            if idx_other == idx:
                continue
            [fname, obj_other] = obj_info[idx_other][:2]
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


def render_animation():
    """
    Let blender start rendering the animation.
    :return: None
    """
    bpy.ops.render.render(animation=True)


def adjust_obj_dataset(obj_info: list[list], json_data: dict):
    """
    The models in "car" and "motorcycle" has different origin and initial rotation. Use this function to
    unify them with "ScannedObjects"
    :param obj_info: the return of random_items or other variants
    :param json_data: data of the scene's layout config
    :return: None
    """
    sz = len(obj_info)
    for idx in range(0, sz):
        fname, obj, obj_type, obj_id = obj_info[idx]
        if obj_type in ["car", "motorcycle"]:
            x, y, z = obj.rotation_euler
            x = math.pi/2
            obj.rotation_euler = (x, y, z)

            bpy.ops.object.select_pattern(pattern=obj.name)
            bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
            x, y, z = obj.location
            z = obj.dimensions[1] * 0.4
            obj.location = (x, y, z)


def obj_info_to_json(obj_info: list[list], json_data: dict, obj_root: list[str]):
    """
    Write obj infos to json_data.
    :param obj_info: the return of random_items or other variants
    :param json_data: data of the scene's layout config
    :param obj_root: the root paths of obj
    :return:  None
    """
    info_list = []
    cnt = 0
    sz = len(obj_info)
    for idx in range(0, sz, 2):
        fname, obj, obj_type, obj_id = obj_info[idx]
        cnt += 1
        single_info = {}
        obj_path = str(fname)[len(str(obj_root)):]
        single_info["obj_path"] = obj_path

        single_info["obj_type"] = obj_type
        single_info["obj_id"] = obj_id

        if obj_type not in ["car", "motorcycle"]:
            tex_path = obj.active_material.node_tree.nodes[2].image.filepath
            tex_path = tex_path[tex_path.find(obj_path[:7]):]
            single_info["texture_path"] = tex_path

        x, y, z = obj.location
        single_info["location"] = {"x": x, "y": y, "z": z}
        x, y, z = obj.rotation_euler
        single_info["rotation_euler"] = {"x": x, "y": y, "z": z}
        x, y, z = obj.scale
        single_info["scale"] = {"x": x, "y": y, "z": z}
        x, y, z = obj.dimensions
        single_info["dimensions"] = {"x": x, "y": y, "z": z}
        info_list.append(single_info)

    json_data["object_count"] = cnt
    json_data["objects"] = info_list


def enable_gpus(device_type: str, use_cpus=False):
    """
    Use gpu to render.
    :param device_type: the device used in blender cycles
    :param use_cpus: True if cpu will be used
    :return: None
    """
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


import bpy

bpy.context.scene.render.fps = 1
# 循环items集合中的所有物体，每隔一秒可见一个物体
# 循环items集合中的所有物体，每隔一秒可见一个物体
i=0
for k,obj in enumerate(bpy.data.collections['items'].all_objects):
    obj.visible_camera = False
    obj.visible_shadow = False
    obj.keyframe_insert(data_path="visible_camera", frame=i)
    obj.keyframe_insert(data_path="visible_shadow", frame=i)
    obj.visible_camera = True
    obj.visible_shadow = True
    obj.keyframe_insert(data_path="visible_camera", frame=i+1)
    obj.keyframe_insert(data_path="visible_shadow", frame=i+1)
    obj.visible_camera = False
    obj.keyframe_insert(data_path="visible_camera", frame=i+2)
    obj.keyframe_insert(data_path="visible_shadow", frame=i+2)
    obj.visible_camera = True
    obj.visible_shadow = False
    obj.keyframe_insert(data_path="visible_camera", frame=i+3)
    obj.keyframe_insert(data_path="visible_shadow", frame=i+3)
    obj.visible_camera = False
    obj.keyframe_insert(data_path="visible_camera", frame=i+4)
    obj.keyframe_insert(data_path="visible_shadow", frame=i+4 )
    i+=3
 bpy.context.scene.frame_end = i+1
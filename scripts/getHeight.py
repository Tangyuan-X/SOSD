import bpy

# 选择名为item的对象
obj = bpy.data.objects['model.005']

# 获取对象尺寸
if obj is not None:
    dimensions = obj.dimensions
    print("Width: {:.2f}".format(dimensions.x))
    print("Height: {:.2f}".format(dimensions.y))
    print("Depth: {:.2f}".format(dimensions.z))

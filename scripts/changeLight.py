import math
import random

import bpy

# 选中名为"left"的灯光
light = bpy.data.objects['left']
# 随机设置灯光的强度为50到200之间的值
light.data.energy = random.uniform(50, 200)
# 灯泡的位置在0，0，0为中心，半径为5的球体内随机选择一个位置
def generate_random_coordinate():
    while True:
        x = random.uniform(-5, 5)
        y = random.uniform(-5, 5)
        z = random.uniform(0, math.sqrt(25 - x**2 - y**2))
        if x**2 + y**2 + z**2 <= 25:
            return x, y, z
light.location = generate_random_coordinate()
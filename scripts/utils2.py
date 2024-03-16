# 将G:\blender\location\Poly Haven所有子文件夹中所有info.json中type属性为“1”的文件夹复制到G:\blender\location\texture中
import os
import json
import shutil

# 起始路径
source_path = 'G:\\blender\\location\\Poly Haven'
# 目标路径
target_path = 'G:\\blender\\location\\texture'

# 确保目标路径存在
os.makedirs(target_path, exist_ok=True)

# 遍历起始路径的所有子文件夹
for root, dirs, files in os.walk(source_path):
    for dir in dirs:
        # 构建info.json的完整路径
        info_json_path = os.path.join(root, dir, 'info.json')
        # 检查info.json文件是否存在
        if os.path.isfile(info_json_path):
            # 读取并解析JSON文件
            with open(info_json_path, 'r') as f:
                try:
                    data = json.load(f)
                    # 检查type属性是否为"1"
                    print(data.get('type'))
                    if data.get('type') == 1:
                        # 复制整个文件夹
                        shutil.copytree(os.path.join(root, dir), os.path.join(target_path, dir))
                except json.JSONDecodeError as e:
                    print(f'JSON decode error in file: {info_json_path}: {e}')
                except Exception as e:
                    print(f'Error processing file {info_json_path}: {e}')

print('Finished copying folders.')
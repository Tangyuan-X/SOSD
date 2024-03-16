import shutil
from pathlib import Path
import json
# 指定数据集的根目录
with open('config.json', 'r') as f:
    config = json.load(f)

dataset_root = Path(config['google_research_url'])

# 遍历根目录下的所有子文件夹
for item in dataset_root.iterdir():
    if item.is_dir():  # 确保是一个目录
        materials_path = item / 'materials'  # 设置materials子文件夹的路径
        meshes_path = item / 'meshes'  # 设置meshes子文件夹的路径

        # 确认materials子文件夹和meshes子文件夹存在
        if materials_path.exists() and materials_path.is_dir() and meshes_path.exists() and meshes_path.is_dir():
            # 移动materials子文件夹到meshes子文件夹中
            target_path = meshes_path / 'materials'

            # 检查目标路径是否已经存在materials文件夹
            if not target_path.exists():
                shutil.move(str(materials_path), str(target_path))
                print(f"Moved {materials_path} to {target_path}")
            else:
                print(f"Target path {target_path} already exists.")
        else:
            # 如果materials或meshes子文件夹不存在，则打印一个消息
            if not materials_path.exists():
                print(f"Materials path {materials_path} does not exist.")
            if not meshes_path.exists():
                print(f"Meshes path {meshes_path} does not exist.")
import os
import shutil

# 设置原始文件夹路径和目标文件夹路径
source_path = 'G:\\blender\\location\\texture'
target_path = 'G:\\blender\\location\\texture_jpgs'

# 如果目标文件夹不存在，则创建它
os.makedirs(target_path, exist_ok=True)

# 遍历source_path下的所有文件和文件夹
for root, dirs, files in os.walk(source_path):
    for file in files:
        # 检查文件名是否包含"diff"且为".jpg"文件
        if "diff" in file.lower() and file.lower().endswith('.jpg'):
            source_file_path = os.path.join(root, file)
            target_file_path = os.path.join(target_path, file)

            # 如果目标路径中已存在同名文件，则生成新的文件名
            if os.path.exists(target_file_path):
                basename, extension = os.path.splitext(file)
                count = 1
                new_basename = f"{basename}_{count}"
                new_target_file_path = os.path.join(target_path, new_basename + extension)
                while os.path.exists(new_target_file_path):
                    count += 1
                    new_basename = f"{basename}_{count}"
                    new_target_file_path = os.path.join(target_path, new_basename + extension)
                target_file_path = new_target_file_path

            # 复制文件
            shutil.copy2(source_file_path, target_file_path)

print('Finished copying .jpg files containing "diff".')
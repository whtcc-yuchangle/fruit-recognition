import os

# 定义fruit目录路径
fruit_dir = 'fruit'

# 获取所有jpg文件
jpg_files = [f for f in os.listdir(fruit_dir) if f.endswith('.jpg')]

# 按文件名排序
jpg_files.sort()

# 重命名文件
for i, old_name in enumerate(jpg_files, start=1):
    # 生成新文件名，格式为001.jpg, 002.jpg等
    new_name = f'{i:03d}.jpg'
    
    # 构建完整路径
    old_path = os.path.join(fruit_dir, old_name)
    new_path = os.path.join(fruit_dir, new_name)
    
    # 重命名文件
    os.rename(old_path, new_path)
    print(f'重命名: {old_name} -> {new_name}')

print(f'共重命名 {len(jpg_files)} 个文件')

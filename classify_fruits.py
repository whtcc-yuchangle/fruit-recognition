import os
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

# 定义路径
model_path = 'model/best.pt'
fruit_dir = 'fruit'
out_dir = 'out'

# 加载模型
model = YOLO(model_path)

# 创建输出目录
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# 遍历所有图片文件
for filename in os.listdir(fruit_dir):
    if filename.endswith('.jpg'):
        # 构建图片路径
        img_path = os.path.join(fruit_dir, filename)
        
        # 进行预测
        results = model(img_path)
        
        # 获取预测结果
        for result in results:
            # 对于分类模型，使用result.probs
            if result.probs is not None:
                # 获取类别ID和名称
                class_id = result.probs.top1
                class_name = model.names[class_id]
                
                # 创建类别文件夹
                class_dir = os.path.join(out_dir, class_name)
                if not os.path.exists(class_dir):
                    os.makedirs(class_dir)
                
                # 打开图片
                image = Image.open(img_path)
                draw = ImageDraw.Draw(image)
                
                # 尝试使用系统字体，如果失败则使用默认字体
                try:
                    font = ImageFont.truetype("arial.ttf", 60)
                except:
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 60)
                    except:
                        font = ImageFont.load_default()
                
                # 在图片左上角绘制类别名称
                text = class_name
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 绘制白色背景框
                padding = 15
                height_padding = 20
                draw.rectangle([0, 0, text_width + padding * 2, text_height + padding + height_padding], fill='white')
                
                # 绘制文字
                draw.text((padding, padding), text, fill='red', font=font)
                
                # 保存图片到对应类别文件夹
                dest_path = os.path.join(class_dir, filename)
                image.save(dest_path)
                
                print(f'已分类: {filename} -> {class_name}')

print('分类完成！')

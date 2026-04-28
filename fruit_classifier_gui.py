import sys
import os

# 禁用ultralytics网络下载
os.environ['YOLO_OFFLINE'] = '1'
os.environ['ULTRALYTICS_OFFLINE'] = '1'
# 禁用SSL验证（临时解决方法）
os.environ['REQUESTS_CA_BUNDLE'] = ''

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class FruitClassifierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('水果分类器')
        self.setGeometry(100, 100, 800, 600)
        
        # 加载模型
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model', 'best.pt')
        self.model = YOLO(model_path)
        
        # 主窗口布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 图片显示区域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet('border: 1px solid gray;')
        main_layout.addWidget(self.image_label)
        
        # 按钮区域
        button_layout = QVBoxLayout()
        
        # 选择图片按钮
        self.select_button = QPushButton('选择图片')
        self.select_button.clicked.connect(self.select_image)
        button_layout.addWidget(self.select_button)
        
        # 检测按钮
        self.detect_button = QPushButton('检测')
        self.detect_button.clicked.connect(self.detect_fruit)
        button_layout.addWidget(self.detect_button)
        
        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)
        
        # 存储当前图片路径
        self.current_image_path = None
        self.current_pixmap = None
    
    def select_image(self):
        # 打开文件选择对话框
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择图片", "", "Image files (*.jpg *.jpeg *.png)")
        
        if file_path:
            self.current_image_path = file_path
            # 显示图片
            pixmap = QPixmap(file_path)
            # 调整图片大小以适应标签
            scaled_pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
            self.current_pixmap = scaled_pixmap
            self.image_label.setPixmap(scaled_pixmap)
    
    def detect_fruit(self):
        if not self.current_image_path:
            return
        
        # 使用模型进行预测
        results = self.model(self.current_image_path)
        
        for result in results:
            if result.probs is not None:
                # 获取类别ID和名称
                class_id = result.probs.top1
                class_name = self.model.names[class_id]
                
                # 打开图片并添加标签
                image = Image.open(self.current_image_path)
                draw = ImageDraw.Draw(image)
                
                # 尝试使用系统字体
                try:
                    font = ImageFont.truetype("arial.ttf", 60)
                except:
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 60)
                    except:
                        font = ImageFont.load_default()
                
                # 绘制标签
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
                
                # 保存带有标签的图片
                temp_path = 'temp_labeled.jpg'
                image.save(temp_path)
                
                # 显示带有标签的图片
                pixmap = QPixmap(temp_path)
                scaled_pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
                self.image_label.setPixmap(scaled_pixmap)
                
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                break

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FruitClassifierApp()
    window.show()
    sys.exit(app.exec_())

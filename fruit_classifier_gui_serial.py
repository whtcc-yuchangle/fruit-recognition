import sys
import os

os.environ['YOLO_OFFLINE'] = '1'
os.environ['ULTRALYTICS_OFFLINE'] = '1'
os.environ['REQUESTS_CA_BUNDLE'] = ''

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget,
    QFileDialog, QHBoxLayout, QComboBox, QGroupBox, QGridLayout, QMessageBox,
    QSizePolicy
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import serial
import serial.tools.list_ports

# model class_id -> user number mapping
CLASS_ID_TO_NUMBER = {
    0: 0,   # apple  -> 苹果
    1: 1,   # banana -> 香蕉
    3: 2,   # orange -> 橙子
    2: 3,   # grape  -> 葡萄
}
UNKNOWN_ID = 9


class FruitClassifierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('水果分类检测V1.0（人工智能学院上课学习使用）')
        self.setGeometry(100, 100, 900, 700)

        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model', 'best.pt')
        self.model = YOLO(model_path)

        self.serial_port = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # --- 顶部 Logo 区域 ---
        header_layout = QHBoxLayout()
        logo_width = 224
        self.logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.png')
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaledToWidth(logo_width, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_logo)
        header_layout.addWidget(self.logo_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout, 0)

        # --- 图片显示区域 ---
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet('border: 1px solid gray;')
        self.image_label.setMinimumHeight(200)
        self.image_label.setScaledContents(False)
        main_layout.addWidget(self.image_label, 1)

        # --- 底部：左串口配置 | 右检测操作 ---
        bottom_row = QHBoxLayout()

        # 左侧：串口配置
        serial_group = QGroupBox('串口配置')
        serial_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        serial_layout = QGridLayout()
        serial_layout.setVerticalSpacing(6)
        serial_layout.setHorizontalSpacing(10)
        serial_layout.setContentsMargins(10, 10, 10, 6)
        for row in range(6):
            serial_layout.setRowStretch(row, 0)
        serial_group.setLayout(serial_layout)

        serial_layout.addWidget(QLabel('串口:'), 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(90)
        serial_layout.addWidget(self.port_combo, 0, 1)
        self.refresh_ports_button = QPushButton('刷新')
        self.refresh_ports_button.setFixedWidth(60)
        self.refresh_ports_button.clicked.connect(self.refresh_ports)
        serial_layout.addWidget(self.refresh_ports_button, 0, 2)

        serial_layout.addWidget(QLabel('波特率:'), 1, 0)
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.baud_combo.setCurrentText('115200')
        serial_layout.addWidget(self.baud_combo, 1, 1, 1, 2)

        serial_layout.addWidget(QLabel('数据位:'), 2, 0)
        self.data_bits_combo = QComboBox()
        self.data_bits_combo.addItems(['8', '7', '6', '5'])
        serial_layout.addWidget(self.data_bits_combo, 2, 1, 1, 2)

        serial_layout.addWidget(QLabel('校验位:'), 3, 0)
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(['None', 'Even', 'Odd', 'Mark', 'Space'])
        serial_layout.addWidget(self.parity_combo, 3, 1, 1, 2)

        serial_layout.addWidget(QLabel('停止位:'), 4, 0)
        self.stop_bits_combo = QComboBox()
        self.stop_bits_combo.addItems(['1', '1.5', '2'])
        serial_layout.addWidget(self.stop_bits_combo, 4, 1, 1, 2)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 6, 0, 0)
        btn_row.addStretch()
        self.open_button = QPushButton('打开串口')
        self.open_button.setFixedWidth(180)
        self.open_button.setFixedHeight(34)
        self.open_button.clicked.connect(self.toggle_serial)
        btn_row.addWidget(self.open_button)
        self.serial_status_label = QLabel('未连接')
        self.serial_status_label.setStyleSheet('color: red;')
        btn_row.addWidget(self.serial_status_label)
        btn_row.addStretch()
        serial_layout.addLayout(btn_row, 5, 0, 1, 3)

        bottom_row.addWidget(serial_group)

        # 右侧：检测操作（与左侧等高，按钮间距撑开）
        action_group = QGroupBox('检测操作')
        action_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        action_layout = QVBoxLayout()
        action_layout.setSpacing(24)
        action_layout.setContentsMargins(16, 24, 16, 24)
        action_group.setLayout(action_layout)

        self.select_button = QPushButton('选择图片')
        self.select_button.setMinimumHeight(34)
        self.select_button.clicked.connect(self.select_image)
        action_layout.addWidget(self.select_button)

        self.detect_button = QPushButton('检测')
        self.detect_button.setMinimumHeight(34)
        self.detect_button.clicked.connect(self.detect_fruit)
        action_layout.addWidget(self.detect_button)

        bottom_row.addWidget(action_group, 0, Qt.AlignVCenter)

        main_layout.addLayout(bottom_row, 0)

        self.current_image_path = None
        self.current_pixmap = None

        # 初始刷新串口列表
        self.refresh_ports()

    def refresh_ports(self):
        current = self.port_combo.currentText()
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)
        if current and self.port_combo.findText(current) >= 0:
            self.port_combo.setCurrentText(current)

    def toggle_serial(self):
        if self.serial_port is not None and self.serial_port.is_open:
            self.close_serial()
        else:
            self.open_serial()

    def open_serial(self):
        port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, '错误', '请选择串口')
            return

        parity_map = {'None': 'N', 'Even': 'E', 'Odd': 'O', 'Mark': 'M', 'Space': 'S'}
        stop_bits_map = {'1': 1, '1.5': 1.5, '2': 2}

        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=int(self.baud_combo.currentText()),
                bytesize=int(self.data_bits_combo.currentText()),
                parity=parity_map[self.parity_combo.currentText()],
                stopbits=stop_bits_map[self.stop_bits_combo.currentText()],
                timeout=1
            )
            self.open_button.setText('关闭串口')
            self.serial_status_label.setText(f'已连接: {port}')
            self.serial_status_label.setStyleSheet('color: green;')
        except Exception as e:
            QMessageBox.critical(self, '串口错误', str(e))

    def close_serial(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.serial_port = None
        self.open_button.setText('打开串口')
        self.serial_status_label.setText('未连接')
        self.serial_status_label.setStyleSheet('color: red;')

    def select_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择图片", "", "Image files (*.jpg *.jpeg *.png)")

        if file_path:
            self.current_image_path = file_path
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
            self.current_pixmap = scaled_pixmap
            self.image_label.setPixmap(scaled_pixmap)

    def send_class_id(self, user_number):
        if self.serial_port and self.serial_port.is_open:
            try:
                msg = f'class:{user_number}'
                self.serial_port.reset_input_buffer()
                self.serial_port.write(msg.encode('utf-8'))
                self.serial_port.flush()
                print(f'[串口] 已发送: {msg!r} ({len(msg)}字节)')
            except Exception as e:
                self.serial_status_label.setText(f'发送失败: {e}')
                self.serial_status_label.setStyleSheet('color: red;')

    def detect_fruit(self):
        if not self.current_image_path:
            return

        results = self.model(self.current_image_path)

        for result in results:
            if result.probs is not None:
                class_id = result.probs.top1
                class_name = self.model.names[class_id]
                user_number = CLASS_ID_TO_NUMBER.get(class_id, UNKNOWN_ID)
                print(f'[检测] class_id={class_id}, name={class_name}, 发送=class:{user_number}')

                image = Image.open(self.current_image_path)
                draw = ImageDraw.Draw(image)

                try:
                    font = ImageFont.truetype("arial.ttf", 60)
                except:
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 60)
                    except:
                        font = ImageFont.load_default()

                text = f'{class_name} ({user_number})'
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_bottom = bbox[3]

                padding = 10
                draw.rectangle([0, 0, text_width + padding * 2, text_bottom + padding * 2], fill='white')
                draw.text((padding, padding), text, fill='red', font=font)

                temp_path = 'temp_labeled.jpg'
                image.save(temp_path)

                pixmap = QPixmap(temp_path)
                scaled_pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
                self.image_label.setPixmap(scaled_pixmap)

                if os.path.exists(temp_path):
                    os.remove(temp_path)

                self.send_class_id(user_number)
                break

    def closeEvent(self, event):
        self.close_serial()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FruitClassifierApp()
    window.show()
    sys.exit(app.exec_())

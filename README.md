# Fruit Recognition - 水果识别

基于 YOLOv8 的水果分类识别系统，支持命令行批量分类和 GUI 交互式识别。

## 功能

- **命令行批量分类**：对 `fruit/` 目录下所有图片进行分类，按类别输出到 `out/` 目录
- **GUI 应用**：基于 PyQt5 的图形界面，选择图片后一键识别并标注类别
- **GUI 串口通信**：在 GUI 基础上增加串口通信功能，识别后通过串口发送分类结果给 STM32
- **图片重命名**：将目录中的图片统一重命名为序号格式

## 环境要求

- Python 3.8+
- PyTorch
- ultralytics
- PyQt5
- Pillow
- pyserial

## 安装依赖

```bash
pip install torch ultralytics PyQt5 Pillow pyserial
```

## 使用方法

### GUI 图形界面

```bash
python fruit_classifier_gui.py
```

点击「选择图片」加载图片，再点击「检测」进行识别，结果会直接标注在图片上。

### GUI 串口通信

```bash
python fruit_classifier_gui_serial.py
```

在 GUI 基础上增加串口通信模块。配置串口参数并连接后，检测结果会以 7 字节固定格式 `class:<id>` 通过串口发送。

| 类别 | 发送内容 |
|------|----------|
| 苹果 | `class:0` |
| 香蕉 | `class:1` |
| 橙子 | `class:2` |
| 葡萄 | `class:3` |
| 未知 | `class:9` |

### 命令行批量分类

```bash
python classify_fruits.py
```

程序会读取 `fruit/` 目录下的所有 jpg 图片，分类后按类别名称存放到 `out/` 目录中。

### 图片重命名

```bash
python rename_images.py
```

将 `fruit/` 目录下的图片重命名为 `001.jpg`、`002.jpg` 等序号格式。

## 项目结构

```
├── model/
│   └── best.pt              # 训练好的 YOLOv8 分类模型
├── fruit/                   # 水果图片数据集
├── classify_fruits.py       # 命令行批量分类脚本
├── fruit_classifier_gui.py        # PyQt5 GUI 应用
├── fruit_classifier_gui_serial.py # GUI 串口通信版
├── rename_images.py               # 图片重命名工具
└── README.md
```

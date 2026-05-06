# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A fruit classification system using a pre-trained YOLOv8 classification model (`model/best.pt`). It has three modes: CLI batch classification, a PyQt5 GUI app, and a serial-communication GUI for STM32. Class names come directly from the YOLO model's internal `names` mapping.

## Commands

Use the conda environment Python interpreter for all Python commands.

```bash
PYTHON="D:/miniconda3/envs/PyTorch/python.exe"

# GUI app
$PYTHON fruit_classifier_gui.py

# GUI app with serial communication (STM32)
$PYTHON fruit_classifier_gui_serial.py

# CLI: classify all images in fruit/ → out/<class_name>/
$PYTHON classify_fruits.py

# Rename images in fruit/ to sequential 001.jpg, 002.jpg, ...
$PYTHON rename_images.py
```

No test suite, build step, or linter is configured.

## Architecture

**Model**: A YOLOv8 classification model at `model/best.pt`, loaded via `ultralytics.YOLO`. The model predicts a single top-1 class per image, accessed through `result.probs.top1` and `model.names[class_id]`.

**Image annotation pattern**: Both scripts repeat the same annotation logic — opening the image with PIL, drawing a white rectangle with the class name text in red at the top-left corner. The GUI writes to a temp file for display; the CLI writes to `out/<class_name>/<filename>`.

**GUI (`fruit_classifier_gui.py`)**: Single-window PyQt5 app (`FruitClassifierApp`). Workflow: user selects an image via file dialog → clicks "检测" (Detect) → model runs inference → PIL annotates the image → result is saved to a temp file and displayed. Sets `YOLO_OFFLINE` and `ULTRALYTICS_OFFLINE` env vars at module level to prevent network calls.

**GUI Serial (`fruit_classifier_gui_serial.py`)**: Extended version with serial port communication for STM32. Adds serial config UI (port, baud rate, data bits, parity, stop bits). Layout: image area (top), serial config (bottom-left), detect buttons (bottom-right). After detection, sends 7-byte fixed-length message `class:<id>` (no terminator). Class mapping: apple→0, banana→1, orange→2, grape→3, unknown→9. Serial config and detect groups use `QSizePolicy.Fixed` vertical policy with image area taking all remaining space via stretch factor 1.

**CLI (`classify_fruits.py`)**: Iterates over all `.jpg` files in `fruit/`, runs inference, annotates, and saves each to `out/<class_name>/<filename>`. Creates output subdirectories on demand.

**Dependencies**: `torch`, `ultralytics`, `PyQt5`, `Pillow` (PIL), `numpy`, `pyserial`.

**`.gitignore`**: Ignores `.idea/` and `.claude/`. The `out/` directory is not in `.gitignore` but is output-only.

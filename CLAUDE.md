# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A fruit classification system using a pre-trained YOLOv8 classification model (`model/best.pt`). It has two modes: CLI batch classification and a PyQt5 GUI app. Class names come directly from the YOLO model's internal `names` mapping.

## Commands

Use the conda environment Python interpreter for all Python commands.

```bash
PYTHON="D:/miniconda3/envs/yolo/python.exe"

# GUI app
$PYTHON fruit_classifier_gui.py

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

**CLI (`classify_fruits.py`)**: Iterates over all `.jpg` files in `fruit/`, runs inference, annotates, and saves each to `out/<class_name>/<filename>`. Creates output subdirectories on demand.

**Dependencies**: `torch`, `ultralytics`, `PyQt5`, `Pillow` (PIL), `numpy` (used by the GUI but only for the import — no direct array manipulation).

**`.gitignore`**: Ignores `.idea/` and `.claude/`. The `out/` directory is not in `.gitignore` but is output-only.

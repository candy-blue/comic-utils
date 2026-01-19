# 漫画工具箱 (Comic Utilities)

**[English](README.md) | [中文](README_ZH.md)**

**漫画工具箱 (Comic Utilities)** 是一个为漫画爱好者设计的综合工具集，用于轻松管理和将各种格式转换为 CBZ (Comic Book Zip)。

### 功能特点

- **文件夹转 CBZ**：递归搜索包含图片（JPG, PNG 等）的文件夹，并将其批量转换为 `.cbz` 文件。非常适合整理散乱的漫画图集。
- **电子书转 CBZ**：将电子书格式（`.epub`, `.mobi`）直接转换为 `.cbz`。
    - 自动提取书中的图片并按顺序重命名。
    - 支持无 DRM 保护的文件。
- **现代化界面**：支持中英双语切换，支持文件拖拽操作。

### 安装

1. 确保已安装 Python 3.10+。
2. 安装依赖库：
   ```bash
   pip install -r requirements.txt
   ```

### 使用方法

运行程序：
```bash
python main.py
```

### 源码构建

如果需要生成独立的 `.exe` 可执行文件：
```bash
build.bat
```
生成的文件将位于 `dist/` 目录下。

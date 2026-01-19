# Comic Utilities / 漫画工具箱

[English](#english) | [中文](#chinese)

<a name="english"></a>
## English

**Comic Utilities** is a unified toolset designed for comic book enthusiasts to easily manage and convert various formats into CBZ (Comic Book Zip).

### Features

- **Folder to CBZ**: Recursively searches for folders containing images (JPG, PNG, etc.) and batch converts them into `.cbz` files. Perfect for organizing loose image collections.
- **Ebook to CBZ**: Converts eBook formats (`.epub`, `.mobi`) directly into `.cbz`.
    - Extracts images from books and renames them sequentially.
    - Supports non-DRM files.
- **User-Friendly GUI**: A simple graphical interface with tabs for different tools.

### Installation

1. Ensure Python 3.10+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

Run the application:
```bash
python main.py
```

### Build from Source

To generate a standalone `.exe` file:
```bash
build.bat
```
The executable will be located in the `dist/` directory.

---

<a name="chinese"></a>
## 中文 (Chinese)

**Comic Utilities (漫画工具箱)** 是一个为漫画爱好者设计的综合工具集，用于轻松管理和将各种格式转换为 CBZ (Comic Book Zip)。

### 功能特点

- **文件夹转 CBZ**：递归搜索包含图片（JPG, PNG 等）的文件夹，并将其批量转换为 `.cbz` 文件。非常适合整理散乱的漫画图集。
- **电子书转 CBZ**：将电子书格式（`.epub`, `.mobi`）直接转换为 `.cbz`。
    - 自动提取书中的图片并按顺序重命名。
    - 支持无 DRM 保护的文件。
- **图形用户界面**：提供简洁的选项卡式界面，方便切换不同功能。

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

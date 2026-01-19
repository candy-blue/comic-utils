# 📦 漫画工具箱 (Comic Utilities)

**[English](README.md) | [中文](README_ZH.md)**

---

## ✨ 功能

- 📂 **文件夹转格式**：将包含图片的文件夹批量转换为 **CBZ, PDF, EPUB, ZIP, 7Z**。非常适合整理散乱的图集。
- 🔄 **格式转换**：支持各种漫画/电子书格式互转（例如 **EPUB 转 CBZ**，**MOBI 转 PDF**）。支持输入 `.epub`, `.mobi`, `.cbz`, `.zip`, `.rar`, `.pdf` 等格式。
- 📤 **提取图片**：一键将漫画包（CBZ, EPUB, PDF 等）中的所有图片提取到单独的文件夹中。
- 🧭 **智能排序**：文件处理遵循自然数字顺序（1, 2, 10...），避免乱序，确保阅读顺序正确。
- 🖥️ **现代化界面**：中英双语支持，全界面支持 **拖拽操作**，简单直观。

---

## 🖼️ 界面预览

<img src="https://github.com/candy-blue/comic-utils/blob/main/image/image1.png" width="45%" alt="Interface 1" /> <img src="https://github.com/candy-blue/comic-utils/blob/main/image/image2.png" width="45%" alt="Interface 2" />

---

## 📝 使用说明

1. **下载**：在 [Releases](https://github.com/candy-blue/comic-utils/releases) 页面下载最新的 `ComicUtils.exe`
2. **运行**：双击运行程序（无需安装）
3. **选择功能**：在顶部标签页选择 "文件夹转格式"、"格式转换" 或 "提取到文件夹"
4. **导入**：直接将文件夹或文件 **拖拽** 到窗口中
5. **开始**：点击开始按钮即可！

📁 **提示：**
- **默认输出**：如果未选择输出目录，转换后的文件将默认保存在输入文件所在的**上一级目录**（文件夹转格式）或同级目录（其他模式）。
- **MOBI 说明**：目前支持读取 MOBI，但创建 MOBI 功能受限（建议转为 EPUB）。

---

## 🛠️ 开发说明

1. 确保已安装 Python 3.10+
2. 安装依赖库：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行程序：
   ```bash
   python main.py
   ```
4. 构建 exe：
   ```bash
   build.bat
   ```

---

## 💬 说明

> 因为下载的漫画格式不统一所以做一个可以统一处理的工具

# 📦 漫画工具箱 (Comic Utilities)

**[English](README.md) | [中文](README_ZH.md)**

风神翼龙的漫画管理小工具 —— 把漫画包变成 PDF、CBZ 等格式！

一个纯离线的 **漫画管理转换** 工具 · 离线可用，所有操作均在本地完成，不上传任何文件到服务器。
🛠️ 纯属自己写着玩的练手项目，主要是防止以后找不到所以放 GitHub 备份 😂

---

## ✨ 功能

- ⚡ **纯离线实现**，安全可靠，所有文件都在本地处理
- 📂 **文件夹转格式**：支持将包含图片的文件夹批量转换为 `CBZ`, `PDF`, `EPUB`, `ZIP`, `7Z`
- 📚 **格式转换**：支持电子书/漫画格式互转 (`.epub`, `.mobi`, `.cbz` 等)
- 📤 **提取到文件夹**：一键将各种格式 (`.cbz`, `.pdf` 等) 里的图片提取到文件夹
- 🧭 **智能排序**：图片按文件名自然排序（自动识别 1、2、10 顺序）
- 🖥️ **现代化界面**：中英双语支持，电脑拖拽文件即可使用

---

## 🖼️ 界面预览

<img src="https://github.com/candy-blue/comic-utils/tree/main/image/image1.png" width="45%" alt="Interface 1" /> <img src="https://github.com/candy-blue/comic-utils/tree/main/image/image2.png" width="45%" alt="Interface 2" />

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

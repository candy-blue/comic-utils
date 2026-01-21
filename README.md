# 📦 Comic Utilities / 漫画工具箱

A powerful tool for comic & ebook management: **Pack folders**, **Convert formats**, and **Extract images**.  
一个强大的漫画与电子书管理工具：支持**文件夹打包**、**格式转换**以及**图片提取**。

---

## ✨ Features / 功能特性

### 🇬🇧 English
*   📦 **Folder to Archive** 
    Pack image folders or mixed-content directories directly into `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`.
*   🔄 **Format Conversion** 
    Convert between mainstream comic/ebook formats (lossless or lossy). Supports `.rar`, `.mobi`, `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`.
*   📂 **Extract to Folder** 
    One-click extraction of images from archives or ebooks. Supports `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`, `.rar`, `.mobi`.

### 🇨🇳 中文
*   📦 **文件夹打包与转换 (Folder to Archive)** 
    将包含图片的文件夹或混合文件直接封装为指定格式。支持 `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`。
*   🔄 **格式互转 (Format Conversion)** 
    实现主流漫画/电子书格式之间的无损或有损互转。支持将 `.rar`, `.mobi` 及其他常见格式统一转换为 `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`。
*   📂 **资源提取 (Extract to Folder)** 
    一键将压缩包或电子书还原为图片文件夹。支持解压 `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`, `.rar`, `.mobi` 中的图片数据。

---

## 📊 Supported Formats / 支持格式

**Search Keywords**: `CBZ`, `ZIP`, `PDF`, `EPUB`, `7Z`, `RAR`, `MOBI`

| Function / 功能 | Input Support / 输入支持 | Output Support / 输出支持 | 
| :--- | :--- | :--- | 
| **Folder Pack / 文件夹打包** | Folder (Images) | `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | 
| **Converter / 格式转换** | `.rar`, `.mobi`, `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | 
| **Extract / 提取图片** | `.rar`, `.mobi`, `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | Folder (Images) |

---

## 🖼️ Interface / 界面预览

<div align="center">
<img src="https://github.com/candy-blue/comic-utils/blob/main/image/image1.png" width="45%" alt="Interface 1" /> 
<img src="https://github.com/candy-blue/comic-utils/blob/main/image/image2.png" width="45%" alt="Interface 2" />
</div>

---

## 📝 Usage / 使用说明

### 🇬🇧 English
1.  **Download**: Get the latest `.exe` from the [Releases](https://github.com/candy-blue/comic-utils/releases) page.
2.  **Run**: Double-click `ComicUtils.exe` (No installation needed).
3.  **Select Tab**: Choose between "Folder to Format", "Format Converter", or "Extract".
4.  **Drag & Drop**: Drag your files or folders into the window.
5.  **Start**: Click the Start button and watch it go!

> **Note**: 
> *   **RAR**: Writing `.rar` files is **not supported** (requires proprietary WinRAR). However, **reading/extracting** RAR files is fully supported.
> *   **MOBI**: Creating `.mobi` files is **disabled** (requires kindlegen). Previous experimental support was unstable. Please use **EPUB** instead.

### 🇨🇳 中文
1.  **下载**：在 [Releases](https://github.com/candy-blue/comic-utils/releases) 页面下载最新的 `ComicUtils.exe`。
2.  **运行**：双击运行程序（无需安装）。
3.  **选择功能**：在顶部标签页选择 "文件夹转格式"、"格式转换" 或 "提取到文件夹"。
4.  **导入**：直接将文件夹或文件 **拖拽** 到窗口中。
5.  **开始**：点击开始按钮即可！

> **提示**：
> *   **RAR**: "文件夹转格式" 和 "格式转换" 功能**不支持生成** `.rar` 文件（需 WinRAR）。但是，**读取/提取** RAR 文件是完全支持的。
> *   **MOBI**: **已禁用**创建 `.mobi` 文件（需 kindlegen）。建议使用 **EPUB** 等格式，它具有更广泛的兼容性。

---

## 🛠️ Development / 开发说明

1.  Ensure Python 3.10+ is installed.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    python main.py
    ```
4.  Build standalone executable:
    ```bash
    build.bat
    ```

---

## 🔍 SEO & Keywords
Comic Converter, Ebook Converter, Manga Packer, Image to PDF, Batch Converter.
漫画转换器, 电子书格式转换, 漫画打包工具, 图片转PDF, 批量转换.
**Supported Extensions**: `cbz`, `zip`, `pdf`, `epub`, `7z`, `rar`, `mobi`.

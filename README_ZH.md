# 📦 漫画工具箱 (Comic Utilities)

**[English](README.md) | [中文](README_ZH.md)**

---

## ✨ 功能

*   📦 **文件夹打包与转换 (Folder to Archive)** 
    支持将包含图片的文件夹或混合文件直接封装为指定格式。 
    *   **输入支持**：图片文件夹，或包含 `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`, `.rar`, `.mobi` 的目录。 
    *   **输出格式**：`.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`。 

*   🔄 **格式互转 (Format Conversion)** 
    实现主流漫画/电子书格式之间的无损或有损互转。 
    *   **支持互转**：将 `.rar`, `.mobi` 及其他常见格式统一转换为 `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`。 

*   📂 **资源提取 (Extract to Folder)** 
    一键将压缩包或电子书还原为图片文件夹。 
    *   **支持解压**：`.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`, `.rar`, `.mobi` 中的图片数据。 


## **Supported Formats (支持格式一览)** 

| 功能 (Function) | 输入支持 (Input) | 输出支持 (Output) | 
| :--- | :--- | :--- | 
| **文件夹打包** (Folder Pack) | Folder(Images) | `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | 
| **格式转换** (Converter) | `.rar`, `.mobi`, `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | 
| **提取图片** (Extract) | `.rar`, `.mobi`, `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | Folder (Images) |

---

## 🖼️ 界面预览

<img src="https://github.com/candy-blue/comic-utils/blob/main/image/image1.png" width="100%" alt="Interface 1" /> <img src="https://github.com/candy-blue/comic-utils/blob/main/image/image2.png" width="100%" alt="Interface 2" />

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

### 关于 RAR 和 MOBI 支持
- **RAR**: "文件夹转格式" 和 "格式转换" 功能**不支持生成** `.rar` 文件，因为创建 RAR 需要专有的外部工具（WinRAR）。但是，**读取/提取** RAR 文件是完全支持的。
- **MOBI**: **已禁用**创建 `.mobi` 文件，因为生成有效的 MOBI 文件需要复杂的专有库（如 kindlegen）。此前的实验性支持常导致文件无法读取。建议使用 **EPUB,CBZ** 等格式，它具有更广泛的兼容性。

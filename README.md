# 📦 Comic Utilities

**[English](README.md) | [中文](README_ZH.md)**
---

## ✨ Features

*   � **文件夹打包与转换 (Folder to Archive)** 
    支持将包含图片的文件夹或混合文件直接封装为指定格式。 
    *   **输入支持**：图片文件夹，或包含 `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`, `.rar`, `.mobi` 的目录。 
    *   **输出格式**：`.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`。 

*   🔄 **格式互转 (Format Conversion)** 
    实现主流漫画/电子书格式之间的无损或有损互转。 
    *   **支持互转**：将 `.rar`, `.mobi` 及其他常见格式统一转换为 `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`。 

*   � **资源提取 (Extract to Folder)** 
    一键将压缩包或电子书还原为图片文件夹。 
    *   **支持解压**：`.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`, `.rar`, `.mobi` 中的图片数据。 


## **Supported Formats (支持格式一览)** 

| 功能 (Function) | 输入支持 (Input) | 输出支持 (Output) | 
| :--- | :--- | :--- | 
| **文件夹打包** (Folder Pack) | Folder(Images) | `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | 
| **格式转换** (Converter) | `.rar`, `.mobi`, `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | 
| **提取图片** (Extract) | `.rar`, `.mobi`, `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | Folder (Images) |

---

## 🖼️ Interface Preview

<img src="https://github.com/candy-blue/comic-utils/blob/main/image/image1.png" width="45%" alt="Interface 1" /> <img src="https://github.com/candy-blue/comic-utils/blob/main/image/image2.png" width="45%" alt="Interface 2" />

---

## 📝 Usage

1. **Download**: Get the latest `.exe` from the [Releases](https://github.com/candy-blue/comic-utils/releases) page.
2. **Run**: Double-click `ComicUtils.exe`.
3. **Select Tab**: Choose between "Folder to Format", "Format Converter", or "Extract".
4. **Drag & Drop**: Drag your files or folders into the window.
5. **Start**: Click the Start button and watch it go!

---

## 🛠️ Development

1. Ensure Python 3.10+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```
4. Build standalone executable:
   ```bash
   build.bat
   ```

---

## 💬 Note

> Because the downloaded comic formats are inconsistent, I created a tool to handle them uniformly.

### About RAR and MOBI Support
- **RAR**: Writing `.rar` files is **not supported** in "Folder to Format" or "Format Converter" because it requires proprietary external tools (WinRAR). However, **reading/extracting** RAR files is supported.
- **MOBI**: Creating `.mobi` files is **disabled** because generating valid MOBI files requires complex proprietary libraries (like kindlegen). Previous experimental support often resulted in unreadable files. Please use **EPUB ** instead, which is widely supported.

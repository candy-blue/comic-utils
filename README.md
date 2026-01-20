# 📦 Comic Utilities

**[English](README.md) | [中文](README_ZH.md)**
---

## ✨ Features

*   📦 **Folder to Archive** 
    Pack image folders or mixed-content directories directly into specific formats.
    *   **Input Support**: Image folders, or directories containing `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`, `.rar`, `.mobi`. 
    *   **Output Support**: `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`. 

*   🔄 **Format Conversion** 
    Convert between mainstream comic/ebook formats (lossless or lossy). 
    *   **Conversion Support**: Unified conversion from `.rar`, `.mobi`, and other common formats to `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`. 

*   📂 **Extract to Folder** 
    One-click extraction of archives or ebooks back to image folders. 
    *   **Extraction Support**: Extract images from `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z`, `.rar`, `.mobi`. 


## **Supported Formats** 

| Function | Input Support | Output Support | 
| :--- | :--- | :--- | 
| **Folder Pack** | Folder (Images) | `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | 
| **Converter** | `.rar`, `.mobi`, `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | 
| **Extract** | `.rar`, `.mobi`, `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` | Folder (Images) |

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

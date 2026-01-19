# 📦 Comic Utilities

**[English](README.md) | [中文](README_ZH.md)**

A unified toolset for comic book enthusiasts to easily manage and convert various formats!

A pure offline **Comic Management** tool · No server uploads, all operations are local.
🛠️ Originally a personal practice project to prevent losing it later, so backed up on GitHub 😂

---

## ✨ Features

- ⚡ **Offline & Secure**: All processing happens locally on your machine.
- 📂 **Folder to Format**: Batch convert folders containing images into **CBZ, PDF, EPUB, ZIP, or 7Z**. Perfect for organizing loose image collections.
- � **Format Converter**: Convert between various comic/ebook formats (e.g., **EPUB to CBZ**, **MOBI to PDF**). Supports converting `.epub`, `.mobi`, `.cbz`, `.zip`, `.rar`, `.pdf` to any target format.
- 📤 **Extract Images**: Quickly extract all images from any comic archive (`.cbz`, `.epub`, `.pdf`, etc.) into a folder.
- 🧭 **Smart Sorting**: Images are sorted naturally (1, 2, 10...) ensuring correct reading order.
- 🖥️ **Modern GUI**: Bilingual (English/Chinese) interface with full **Drag & Drop** support.

---

## 🖼️ Interface Preview

<img src="https://github.com/candy-blue/comic-utils/tree/main/image/image1.png" width="45%" alt="Interface 1" /> <img src="https://github.com/candy-blue/comic-utils/tree/main/image/image2.png" width="45%" alt="Interface 2" />

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

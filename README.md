# Comic Utilities

**[English](README.md) | [中文](README_ZH.md)**

**Comic Utilities** is a unified toolset designed for comic book enthusiasts to easily manage and convert various formats into CBZ (Comic Book Zip).

### Features

- **Folder to CBZ**: Recursively searches for folders containing images (JPG, PNG, etc.) and batch converts them into `.cbz` files. Perfect for organizing loose image collections.
- **Ebook to CBZ**: Converts eBook formats (`.epub`, `.mobi`) directly into `.cbz`.
    - Extracts images from books and renames them sequentially.
    - Supports non-DRM files.
- **Modern GUI**: A modern, bilingual (English/Chinese) graphical interface with drag-and-drop support.

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

# Comic Utils (漫画工具箱)

<div align="center">

<img src="src/assets/icon.png" width="128" height="128" alt="Comic Utils Logo" />

### 现代化、高性能的漫画与电子书格式转换、归档与图片提取工具

[![Platform](https://img.shields.io/badge/Platform-Windows%2011%20%7C%2010-0078D4?style=flat-square&logo=windows)](https://github.com/candy-blue/comic-utils/releases)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PySide6%20Fluent%20Design-00BCF2?style=flat-square)](https://github.com/zhiyiYo/PySide6-Fluent-Widgets)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Release](https://img.shields.io/badge/Release-v1.5.0-blue?style=flat-square)](https://github.com/candy-blue/comic-utils/releases)

**[English](README.md)** | **简体中文**

</div>

---

## 📖 项目简介

**Comic Utils (漫画工具箱)** 是一款专为漫画爱好者、数字藏书整理者及电子书读者打造的高性能桌面工具。基于 **Windows 11 Fluent Design** 现代化设计语言构建，深度融合系统 Mica/亚克力磨砂质感与系统主题色，提供极为流畅、优雅且专业的视觉与操作体验。

---

## ✨ 核心特性

- 🎨 **原生 Windows 11 Fluent 视觉体验**
  - 原生继承 Windows 系统主题色与深浅色模式。
  - 支持 **浅色 / 深色 / 跟随系统** 实时无缝动态换肤，无需重启软件。
  - 沉浸式侧边导航栏与优雅的浮动设置控件。
  - **极简圆角细滚动条**：常态 4px 悬浮透明滑块，悬停平滑加宽至 8px，自适应深浅主题。
- 📦 **智能文件夹打包 (Folder Packaging)**
  - 支持将图片文件夹（如分卷/分话目录）一键打包为标准的漫画归档或电子书格式。
  - **递归扫描子文件夹**：自动识别多卷漫画父目录，将每个包含图片的子目录单独打包。
- 🔄 **全能格式批量互转 (Format Converter)**
  - 支持将现有漫画归档、电子书文件批量转换为指定目标格式。
  - 采用多线程并行工作流，处理大批量图书快速稳定。
- 📂 **无损图片提取 (Extract Resources)**
  - 快速解包已有的 `.cbz`、`.zip`、`.epub`、`.pdf`、`.rar` 等归档文件中的全部高清原始图片。
- 📋 **可视化多任务中心 (Task Center)**
  - 实时显示任务进度百分比与处理状态（`等待中`、`处理中`、`已暂停`、`已完成`、`失败`）。
  - **4 大分类分段标签**：支持在 `全部任务`、`文件打包`、`格式转换`、`提取资源` 间秒级筛选。
  - **精细化控制**：支持单个任务的暂停、继续与删除，以及全局全部暂停/继续、清除已完成和清空列表。
- 🌐 **多语言即时热切换 (i18n)**
  - 支持 **简体中文** 与 **English**，切换设置时全局文字与导航栏即时响应更新。
- 🚀 **智能自动更新系统**
  - 内置 GitHub 智能版本比对与防限流更新检测机制。
  - 应用内一键下载更新包，配备实时下载进度条与取消下载支持。

---

## 🖼️ 界面预览

<div align="center">

### 首页概览 (浅色模式 & 深色模式)
<img src="docs/images/home_light.png" width="48%" alt="首页 - 浅色模式" />
<img src="docs/images/home_dark.png" width="48%" alt="首页 - 深色模式" />

<br/><br/>

### 文件夹打包与递归选项
<img src="docs/images/pack_page.png" width="80%" alt="文件夹打包页" />

<br/><br/>

### 实时多任务中心
<img src="docs/images/task_page.png" width="80%" alt="多任务中心" />

</div>

---

## 📊 支持格式对照表

| 核心功能 | 输入格式支持 | 输出格式支持 |
| :--- | :--- | :--- |
| **文件夹打包** | 包含图片 (`.jpg`, `.png`, `.webp`, `.gif`, `.bmp`) 的文件夹 | `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` |
| **格式互转** | `.cbz`, `.zip`, `.rar`, `.pdf`, `.epub`, `.mobi`, `.7z` | `.cbz`, `.zip`, `.pdf`, `.epub`, `.7z` |
| **提取图片** | `.cbz`, `.zip`, `.rar`, `.pdf`, `.epub`, `.mobi`, `.7z` | 原始图片文件夹 |

> **说明**：
> - **RAR 格式**：受限于专利与压缩许可，仅支持读取/解压与转换，不支持生成新 `.rar` 归档。
> - **MOBI 格式**：已逐步淘汰，推荐将 `.mobi` 转换为现代通用的 **`.epub`** 或 **`.cbz`**。

---

## 🚀 快速上手

### 1. 下载使用（推荐普通用户）
1. 前往 GitHub 的 [Releases 最新发布页面](https://github.com/candy-blue/comic-utils/releases) 下载 `ComicUtils.exe`。
2. 双击 `ComicUtils.exe` 即可直接运行，纯绿色软件，无需安装任何额外依赖。

### 2. 开发者本地运行与二次开发
确保本地已安装 **Python 3.10+** 环境：

```bash
# 1. 克隆代码仓库
git clone https://github.com/candy-blue/comic-utils.git
cd comic-utils

# 2. 安装项目依赖
pip install -r requirements.txt

# 3. 启动开发版 GUI
python main.py
```

### 3. 构建独立 EXE 可执行文件
项目配备了完整的自动化构建脚本 `build.bat`（内置独立虚拟环境与 Windows PE 规范的高清图标资源注入）：

```bash
# 执行打包脚本
build.bat
```

构建完成后，产物将生成在 **`dist\ComicUtils.exe`**。

---

## 🤝 贡献与反馈

欢迎提交 Issue 和 Pull Request 来帮助完善 Comic Utils！
- **问题反馈 / 功能建议**：[GitHub Issues](https://github.com/candy-blue/comic-utils/issues)
- **代码仓库**：[https://github.com/candy-blue/comic-utils](https://github.com/candy-blue/comic-utils)

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源。

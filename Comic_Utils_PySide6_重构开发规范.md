# Comic Utils — PySide6 现代化界面重构开发规范

> **用途：直接交给 Gemini / Gemini CLI 作为开发任务说明。**
>
> 目标不是简单给旧 GUI “换颜色”，而是在**保留现有 Python 核心功能和兼容性的前提下，使用 PySide6 对整个桌面 GUI 进行现代化重构**。
>
> 参考项目：`https://github.com/candy-blue/comic-utils`
>
> 当前项目定位：漫画/电子书工具箱，主要包含文件夹打包、格式转换、资源提取等功能。仓库当前 README 明确列出支持 CBZ、ZIP、PDF、EPUB、7Z、RAR、MOBI 等格式，并采用拖放文件/文件夹的交互方式；RAR 写入和 MOBI 创建存在现有限制。开发环境为 Python 3.10+，当前入口为 `main.py`，并提供 `build.bat` 打包流程。
>
> **参考项目现状：**
> - Python 3.10+
> - `main.py` 为现有入口
> - `src/` 为现有源码目录
> - 已存在 `comic-utils.spec`
> - 已存在 `build.bat`
> - GUI 当前采用顶部 Tab/传统工具型界面
> - 核心功能包括：
>   1. Folder to Archive / 文件夹打包
>   2. Format Conversion / 格式转换
>   3. Extract to Folder / 提取到文件夹
>
> 重要原则：**核心业务逻辑优先保留，先理解现有代码，再进行 GUI 重构。不要为了 UI 重写已有可靠的文件处理逻辑。**

---

# 1. 项目最终目标

将当前“传统 Python 工具软件风格”的 GUI 改造成：

- 现代 Windows 桌面应用
- 简洁
- 有层级
- 大量留白
- 卡片式布局
- 侧边栏导航
- 拖拽优先
- 深色 / 浅色主题
- 清晰的任务状态
- 批量处理友好
- 长时间任务不阻塞 UI
- 有统一的错误提示
- 有统一的成功提示
- 支持窗口缩放
- 支持高 DPI
- 最终仍可独立打包为 `.exe`

不要把最终 UI 做成：

- 大量输入框
- 大量按钮堆叠
- 一个窗口塞所有功能
- 顶部一排 Tab 作为主导航
- 大量原生默认控件
- 高密度表单
- 传统“工具箱”样式
- 用颜色堆砌“高级感”

---

# 2. 技术方案

## 2.1 核心技术

必须采用：

```text
Python 3.10+
PySide6
Qt Widgets
QSS
PyInstaller
```

推荐：

```text
图标：Lucide Icons 或同类 SVG 图标
```

不要求引入 Web 前端框架。

本阶段**不要改成 Electron、Tauri、Vue、React**。

目标就是：

```text
Python
  ↓
PySide6
  ↓
Qt Desktop App
  ↓
Windows EXE
```

---

# 3. 总体架构

建议最终结构：

```text
comic-utils/
│
├── main.py
│
├── app/
│   ├── __init__.py
│   │
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── sidebar.py
│   │   │
│   │   ├── pages/
│   │   │   ├── home_page.py
│   │   │   ├── pack_page.py
│   │   │   ├── convert_page.py
│   │   │   ├── extract_page.py
│   │   │   ├── task_page.py
│   │   │   └── settings_page.py
│   │   │
│   │   └── dialogs/
│   │       ├── about_dialog.py
│   │       ├── confirm_dialog.py
│   │       └── error_dialog.py
│   │
│   ├── widgets/
│   │   ├── card.py
│   │   ├── drop_zone.py
│   │   ├── task_card.py
│   │   ├── format_selector.py
│   │   ├── empty_state.py
│   │   ├── primary_button.py
│   │   ├── secondary_button.py
│   │   └── toast.py
│   │
│   ├── workers/
│   │   ├── worker.py
│   │   └── task_manager.py
│   │
│   ├── services/
│   │   ├── conversion_service.py
│   │   ├── packing_service.py
│   │   ├── extraction_service.py
│   │   └── file_service.py
│   │
│   ├── models/
│   │   ├── task.py
│   │   ├── settings.py
│   │   └── file_item.py
│   │
│   ├── config/
│   │   └── app_config.py
│   │
│   └── utils/
│       ├── file_utils.py
│       ├── format_utils.py
│       ├── size_utils.py
│       └── logger.py
│
├── resources/
│   ├── icons/
│   ├── images/
│   └── fonts/
│
├── styles/
│   ├── theme.qss
│   ├── light.qss
│   └── dark.qss
│
├── config/
│   └── default_settings.json
│
├── build.bat
├── comic-utils.spec
├── requirements.txt
└── README.md
```

注意：

**不要机械地按照此目录重写整个项目。**

先分析现有 `src/`，将已有逻辑映射到新的 `services/` 或保持原有模块路径，然后让 GUI 调用已有业务代码。

---

# 4. 重构原则

## 4.1 第一原则：业务逻辑和 UI 解耦

禁止：

```python
def on_start_clicked():
    # 一边改 UI
    # 一边压缩文件
    # 一边处理 PDF
    # 一边循环文件
```

不要在 Qt 主线程直接执行耗时操作。

应该：

```text
UI
 ↓
Task Manager
 ↓
Worker
 ↓
Existing Core Logic
 ↓
Signal
 ↓
UI 更新
```

---

# 5. 多线程 / Worker 架构

漫画处理可能包含：

- 大量文件 IO
- 图片读取
- 图片压缩
- PDF 生成
- EPUB 生成
- ZIP/7Z 操作
- RAR 解压
- 批量转换

这些任务必须避免阻塞 GUI。

推荐：

```python
class ConvertWorker(QObject):
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(object)
    error = Signal(str)

    @Slot()
    def run(self):
        ...
```

主窗口：

```text
QThread
   ↓
Worker
   ↓
业务处理
   ↓
Signal
   ↓
主线程更新 UI
```

要求：

- GUI 永远可响应
- 处理过程中可以切换页面
- 可以取消任务时尽量支持取消
- 任务异常必须回传 GUI
- 不允许 worker 直接操作 Qt UI 控件

---

# 6. 任务模型

建议建立统一 Task Model：

```python
class Task:
    id: str
    name: str
    source: str
    output: str
    operation: str
    status: str
    progress: int
    current: int
    total: int
    error: str | None
```

任务状态建议统一为：

```text
pending
running
paused
completed
failed
cancelled
```

GUI 不要自己猜任务状态。

---

# 7. 主窗口设计

主窗口建议：

```text
┌──────────────────────────────────────────────────┐
│ Comic Utils                              ─ □ ×  │
├───────────────┬──────────────────────────────────┤
│               │                                  │
│  Comic Utils  │                                  │
│               │         Page Content             │
│  🏠 首页       │                                  │
│  📦 文件打包   │                                  │
│  🔄 格式转换   │                                  │
│  📤 提取资源   │                                  │
│  📋 任务       │                                  │
│               │                                  │
│               │                                  │
│  ⚙ 设置       │                                  │
│  ℹ 关于       │                                  │
│               │                                  │
└───────────────┴──────────────────────────────────┘
```

推荐窗口默认尺寸：

```text
1200 × 760
```

最小尺寸：

```text
960 × 640
```

允许用户自由缩放。

不要默认全屏。

---

# 8. Sidebar 设计

侧边栏目标：

- 宽度约 220~240px
- 不要过宽
- 上方 Logo
- 中间导航
- 底部设置 / 关于
- 当前页面有明显选中状态

推荐：

```text
Comic Utils

首页
文件打包
格式转换
提取资源
任务

                ← 空间

设置
关于
```

选中状态：

```text
┌────────────────────┐
│  🔄  格式转换       │
└────────────────────┘
```

而不是：

```text
================================
```

避免使用传统粗边框。

---

# 9. 首页 Home Page

首页不是功能表单。

主要作用：

1. 展示软件定位
2. 快速进入核心功能
3. 展示最近任务
4. 让第一次使用的用户知道怎么操作

推荐结构：

```text
欢迎使用 Comic Utils

轻松管理你的漫画与电子书文件

┌────────────────────┐ ┌────────────────────┐
│       📦           │ │       🔄           │
│                    │ │                    │
│     文件打包        │ │     格式转换        │
│                    │ │                    │
│ 文件夹 → CBZ/PDF   │ │ 多种格式快速转换    │
│                    │ │                    │
│ 开始使用 →         │ │ 开始使用 →         │
└────────────────────┘ └────────────────────┘

┌────────────────────┐
│       📤           │
│                    │
│     提取资源        │
│                    │
│ 从漫画文件提取图片  │
│                    │
│ 开始使用 →         │
└────────────────────┘

最近任务
─────────────────────────────────────────
xxx.cbz       ✓ 已完成
xxx.rar       ⟳ 处理中
```

---

# 10. 文件夹打包页面

页面标题：

```text
文件夹打包
```

副标题：

```text
将漫画文件夹快速打包为常用格式
```

核心区域必须优先采用拖放：

```text
┌────────────────────────────────────────┐
│                                        │
│                  ＋                    │
│                                        │
│          将文件夹拖到这里              │
│                                        │
│       支持图片文件夹 / 混合目录         │
│                                        │
└────────────────────────────────────────┘
```

支持：

- 点击选择文件夹
- 拖入文件夹
- 多文件夹批量添加

添加后：

```text
待处理

┌────────────────────────────────────────┐
│ 📁 One Piece 001                       │
│ 145 files · 320 MB             ×       │
└────────────────────────────────────────┘
```

输出格式：

```text
输出格式

○ CBZ
○ ZIP
○ PDF
○ EPUB
○ 7Z
```

禁止：

- 过度使用 ComboBox
- 所有选项挤成一个表格
- 没有说明文字

---

# 11. 格式转换页面

这是核心页面之一。

页面：

```text
格式转换

将漫画或电子书转换为目标格式
```

拖拽区：

```text
┌──────────────────────────────────────────┐
│                                          │
│                  ＋                       │
│                                          │
│        拖入文件或文件夹开始转换           │
│                                          │
│      CBZ · ZIP · PDF · EPUB · 7Z         │
│                                          │
└──────────────────────────────────────────┘
```

支持文件：

```text
.rar
.mobi
.cbz
.zip
.pdf
.epub
.7z
```

输出支持根据现有项目能力显示：

```text
CBZ
ZIP
PDF
EPUB
7Z
```

注意：

不要给用户显示“RAR 输出”作为可选项，除非现有核心明确支持 RAR 写入。

不要启用不可用的 MOBI 输出。

---

# 12. 提取页面

标题：

```text
提取资源
```

说明：

```text
从漫画或电子书中提取图片资源
```

支持：

- RAR
- MOBI
- CBZ
- ZIP
- PDF
- EPUB
- 7Z

页面设计：

```text
┌────────────────────────────────────────┐
│                                        │
│                  ＋                    │
│                                        │
│          将文件拖到这里                │
│                                        │
│       自动提取图片到文件夹              │
│                                        │
└────────────────────────────────────────┘
```

输出目录单独作为一个卡片：

```text
输出目录

D:\Comics\Extracted

                         [选择目录]
```

---

# 13. 任务页面

这是新版 UI 的重要页面。

不要只显示一个 ProgressBar。

要做成任务卡片。

示例：

```text
正在处理

┌────────────────────────────────────────────┐
│ OnePiece_001.rar                           │
│ RAR → CBZ                                  │
│                                            │
│ ███████████████████░░░░░ 82%               │
│                                            │
│ 第 98 / 120 页                             │
│                                            │
│                      [暂停] [取消]         │
└────────────────────────────────────────────┘
```

已完成：

```text
已完成

┌────────────────────────────────────────────┐
│ Naruto_001.zip                             │
│ ZIP → CBZ                                  │
│                                            │
│ ✓ 转换完成                                  │
│                                            │
│                 [打开文件] [打开目录]       │
└────────────────────────────────────────────┘
```

失败：

```text
┌────────────────────────────────────────────┐
│ xxx.pdf                                    │
│                                            │
│ ⚠ 转换失败                                 │
│ 无法读取文件                               │
│                                            │
│             [重试] [查看详情]              │
└────────────────────────────────────────────┘
```

---

# 14. 空状态

所有页面都必须考虑没有数据的情况。

例如任务为空：

```text
              📋

          暂无任务

开始一个转换任务后，
任务会出现在这里。
```

不要让页面空白。

---

# 15. 成功 / 错误 / 警告提示

建议做统一 Toast。

成功：

```text
✓ 转换完成
```

警告：

```text
⚠ 部分文件无法转换
```

错误：

```text
✕ 转换失败
```

Toast 不要永久占用窗口。

---

# 16. 删除 / 取消操作

涉及数据删除时必须弹确认框。

例如：

```text
清除任务记录？

已完成任务将从列表中移除。

[取消]   [清除]
```

危险操作的按钮要明确。

---

# 17. 文件列表设计

文件列表不要使用传统的“Windows 表格感”。

不推荐：

```text
| Name | Size | Type | Path | Status |
```

更推荐：

```text
┌──────────────────────────────────────────────┐
│ 📕 OnePiece_001.cbz                          │
│    320 MB · CBZ                              │
│                                              │
│                              ✓ 已完成        │
└──────────────────────────────────────────────┘
```

只有确实需要大量文件批量浏览时才使用 `QTableView`。

---

# 18. UI 风格规范

整体视觉目标：

```text
现代
简洁
轻量
柔和
专业
```

不要：

- 过多渐变
- 过多阴影
- 花哨动画
- 大量边框
- 五颜六色
- 拟物化
- 传统 Windows 2000 风格控件

推荐：

```text
圆角
浅阴影
留白
卡片
微妙边框
统一图标
```

---

# 19. 色彩系统

不要每个控件单独定义颜色。

必须建立全局 Design Tokens。

例如：

```text
背景：
#F7F7F8

卡片：
#FFFFFF

正文：
#18181B

次级文字：
#71717A

边框：
#E4E4E7

主色：
#6366F1

成功：
#22C55E

警告：
#F59E0B

错误：
#EF4444
```

注意：

颜色只是推荐起点。

最终以整体视觉效果为准。

如果开发过程中发现颜色冲突，可以统一调整。

---

# 20. Dark Mode

必须支持：

```text
浅色
深色
跟随系统
```

Dark Mode 示例：

```text
背景：
#111113

卡片：
#18181B

正文：
#F4F4F5

次级文字：
#A1A1AA

边框：
#27272A
```

主题切换必须尽可能实时。

不要要求重启应用。

---

# 21. 字体规范

优先使用系统字体，不要强制用户安装字体。

Windows 优先：

```text
Microsoft YaHei UI
Segoe UI
```

建议字号：

```text
页面标题：24~28px
卡片标题：16~18px
正文：14px
辅助文字：12~13px
按钮：14px
```

标题应该有明显层级。

---

# 22. 间距规范

推荐统一 4/8 间距体系：

```text
4
8
12
16
20
24
32
40
48
```

页面：

```text
页面边距：24~32px
卡片间距：16px
卡片内边距：20~24px
```

避免：

```text
5px
13px
17px
23px
```

这种随意间距。

---

# 23. 圆角规范

建议：

```text
小按钮：8px
输入框：8~10px
卡片：12~16px
大拖拽区域：16~20px
对话框：16px
```

不要每个地方一个圆角。

---

# 24. 图标

统一采用 SVG 图标。

推荐 Lucide 风格：

```text
Home
Package
RefreshCw
Archive
FolderOpen
Upload
Download
Settings
Info
Trash2
X
Check
AlertCircle
Play
Pause
RotateCcw
File
FileArchive
FileText
```

不要混用：

- Emoji 图标
- Windows 默认图标
- 不同风格 SVG
- 彩色图标
- 3D 图标

正式 UI 建议全部使用统一线性图标。

---

# 25. 拖拽交互

拖拽是这个项目的重要核心。

拖入文件：

```text
默认：
虚线边框
```

拖入时：

```text
拖拽区域高亮
```

非法文件：

```text
提示：
不支持的文件格式
```

合法文件：

```text
提示：
已添加 3 个文件
```

拖拽成功后自动显示文件列表。

---

# 26. 按钮规范

按钮分为三类：

## Primary

主要动作：

```text
开始转换
开始打包
开始提取
```

## Secondary

普通操作：

```text
选择文件夹
添加文件
打开目录
```

## Destructive

危险操作：

```text
删除
取消全部任务
清空任务
```

不要所有按钮都是 Primary。

---

# 27. 操作流程

一个典型转换流程应该是：

```text
进入格式转换
     ↓
拖入文件
     ↓
文件列表显示
     ↓
选择输出格式
     ↓
选择输出目录
     ↓
点击开始
     ↓
创建任务
     ↓
自动跳转任务页面
     ↓
实时显示进度
     ↓
完成
     ↓
显示成功状态
     ↓
可打开文件 / 打开目录
```

---

# 28. 批量转换

必须支持批量任务。

例如用户一次拖入：

```text
001.rar
002.rar
003.rar
004.rar
005.rar
```

不要立即弹 5 次窗口。

应该：

```text
5 个任务
     ↓
任务队列
```

统一显示：

```text
等待中   2
处理中   1
已完成   2
```

---

# 29. 并发策略

默认不要同时无限启动多个转换任务。

建议配置：

```text
并发任务数：
1
2
3
4
```

默认值：

```text
2
```

具体数值可根据实际处理性能调整。

如果某些操作本身不适合并发，要由核心服务控制。

---

# 30. 进度处理

如果核心业务能提供：

```text
current
total
```

则显示：

```text
98 / 120
82%
```

如果无法获得精确进度：

不要伪造：

```text
██████████████ 83%
```

可以显示：

```text
正在处理…
```

或使用 indeterminate progress。

**禁止制造虚假进度。**

---

# 31. 文件信息

文件列表至少显示：

```text
名称
大小
类型
状态
```

处理中的文件可以显示：

```text
当前文件
当前进度
总体进度
```

---

# 32. 错误处理

所有核心异常必须经过统一错误层。

例如：

```text
FileNotFoundError
PermissionError
UnsupportedFormatError
ConversionError
ArchiveError
```

GUI 最终不要直接显示 Python traceback。

用户看到：

```text
转换失败

无法读取此文件，文件可能已损坏或格式不受支持。

[查看详细错误]
```

点击“详细错误”后才显示技术信息。

---

# 33. 日志

开发模式记录：

```text
时间
任务 ID
模块
级别
错误
```

生产模式不应在 UI 中铺满日志。

可以提供：

```text
查看日志
```

---

# 34. 设置页面

设置建议分组：

## 常规

```text
启动时进入首页
记住窗口大小
记住最后输出目录
```

## 处理

```text
默认输出格式
并发任务数
压缩级别
图片质量
```

## 外观

```text
主题
浅色
深色
跟随系统
```

## 高级

```text
日志目录
缓存目录
恢复任务
```

---

# 35. 设置持久化

不要把用户设置写死在 Python 代码。

可以使用：

```text
JSON
QSettings
```

优先考虑 `QSettings` 保存 GUI 偏好：

```text
窗口尺寸
窗口位置
主题
最后目录
```

业务设置可继续根据现有项目方式保存。

---

# 36. 首页最近任务

保存最近任务摘要：

```text
文件名
类型
状态
时间
```

例如：

```text
最近任务

OnePiece_001.rar
RAR → CBZ
✓ 完成
今天 10:22

Naruto_001.pdf
PDF → 图片
✓ 完成
今天 09:48
```

不要保存过多历史。

建议默认保留最近 20 条。

---

# 37. 右键菜单

可增加：

```text
打开文件
打开所在目录
复制路径
重试
删除记录
```

但第一版不是必须功能。

---

# 38. 系统托盘

可选功能：

```text
运行后台任务时最小化到托盘
```

托盘菜单：

```text
显示主窗口
暂停全部
继续全部
退出
```

注意：

如果用户退出时还有任务，必须提示。

---

# 39. 窗口关闭行为

如果没有任务：

```text
直接退出
```

如果有任务：

```text
仍有任务正在执行

退出后任务将被终止。

[继续退出] [取消]
```

不要无提示直接杀掉处理任务。

---

# 40. 高 DPI

必须保证：

- Windows 125%
- Windows 150%
- Windows 200%

下 UI 不错位。

不要硬编码大量绝对坐标。

优先：

```text
Layouts
SizePolicy
Stretch
MinimumSize
```

避免：

```python
setGeometry(...)
```

大量手动摆放控件。

---

# 41. 禁止的实现方式

## 禁止 1：大量绝对定位

不要：

```python
widget.setGeometry(...)
```

作为主要布局手段。

---

## 禁止 2：所有页面都塞进 main.py

不要：

```text
main.py
  1500 行
```

---

## 禁止 3：UI 和业务逻辑耦合

不要：

```python
button.click -> 直接执行完整转换
```

---

## 禁止 4：主线程执行耗时任务

禁止：

```python
for file in files:
    convert(file)
```

直接运行在 UI 线程。

---

## 禁止 5：虚假进度

没有真实进度就不要显示精确百分比。

---

## 禁止 6：默认 Qt 控件直接裸奔

不要让最终软件满屏默认：

```text
QPushButton
QComboBox
QLineEdit
```

必须通过 QSS 和自定义 Widget 统一风格。

---

# 42. QSS 组织方式

不要把几千行 CSS 全部塞进一个 Python 字符串。

推荐：

```text
styles/
├── theme.qss
├── light.qss
└── dark.qss
```

通用：

```text
theme.qss
```

主题：

```text
light.qss
dark.qss
```

程序启动时：

```text
加载基础主题
+
加载 Light / Dark
```

---

# 43. 自定义 Widget

建议最少实现：

```text
CardWidget
DropZone
TaskCard
Toast
PrimaryButton
SecondaryButton
FormatSelector
EmptyState
```

这样页面代码会更加清晰。

---

# 44. 主窗口页面切换

使用：

```text
QStackedWidget
```

结构：

```text
Sidebar
   ↓
Signal
   ↓
MainWindow
   ↓
QStackedWidget
```

不要为每个导航项创建新窗口。

---

# 45. 国际化

当前项目已经存在中英文 README。

UI 第一版可优先：

```text
中文
```

但代码层面必须避免把所有文字硬编码到复杂逻辑中。

建议统一：

```python
self.tr("开始转换")
```

或建立简单的翻译资源结构，为未来中英文切换保留空间。

---

# 46. 现有功能兼容性要求

重构 GUI 后，以下能力不能因为换 UI 丢失：

## Folder Pack

支持现有：

```text
Folder
→
CBZ
ZIP
PDF
EPUB
7Z
```

## Converter

保留项目当前支持的输入：

```text
RAR
MOBI
CBZ
ZIP
PDF
EPUB
7Z
```

输出按照当前核心能力。

## Extract

保留：

```text
RAR
MOBI
CBZ
ZIP
PDF
EPUB
7Z
```

→ 图片文件夹。

---

# 47. 已知限制

必须在 UI 中正确处理：

## RAR

项目当前不支持创建 RAR。

所以：

```text
RAR
```

可以作为输入，但不能作为输出。

当用户尝试选择不可用输出时：

```text
不允许选择
```

或：

```text
RAR 输出暂不可用
读取 RAR 文件完全支持
```

---

## MOBI

项目当前不建议创建 MOBI。

默认不要显示为输出选项。

如果用户导入 MOBI：

```text
MOBI → 可用目标格式
```

正常工作。

---

# 48. 软件标题

统一：

```text
Comic Utils
```

中文副标题可以使用：

```text
漫画工具箱
```

程序窗口标题：

```text
Comic Utils
```

---

# 49. 关于页面

简单即可：

```text
Comic Utils

漫画与电子书处理工具

Version x.x.x

GitHub
项目地址

许可证

检查更新（如实现）
```

不要把关于页面做得非常复杂。

---

# 50. 启动画面

第一版可选。

如果实现：

不要长时间停留。

只显示：

```text
Comic Utils

漫画工具箱

正在启动…
```

加载完成立即进入主界面。

---

# 51. 动画规范

可以使用轻量动画：

- Sidebar hover
- 页面切换
- Toast
- Progress
- 卡片 hover

不要：

- 页面全屏动画
- 大量缩放
- 过度弹跳
- 持续动画
- 影响文件处理性能

---

# 52. 视觉设计优先级

优先级：

```text
1. 信息层级
2. 布局
3. 间距
4. 可用性
5. 颜色
6. 图标
7. 动画
```

不要：

```text
先做渐变和动画
再考虑布局
```

---

# 53. UX 原则

整个应用应该遵循：

## 用户不应该思考“我要点哪个按钮”

而应该：

```text
把文件拖进来
↓
选择格式
↓
开始
```

核心动作尽量 3 步以内。

---

# 54. 页面层级

最终页面建议：

```text
首页
│
├── 快速操作
├── 最近任务
└── 软件提示

文件打包
│
├── 拖放
├── 文件列表
├── 输出设置
└── 开始

格式转换
│
├── 拖放
├── 文件列表
├── 输出格式
├── 输出设置
└── 开始

提取资源
│
├── 拖放
├── 文件列表
├── 输出目录
└── 开始

任务
│
├── 进行中
├── 已完成
├── 失败
└── 操作

设置
│
├── 常规
├── 处理
├── 外观
└── 高级

关于
```

---

# 55. 开发顺序

**不要一次重写所有代码。**

推荐严格按以下步骤：

## Phase 1：代码审计

先阅读：

```text
main.py
src/**
requirements.txt
comic-utils.spec
build.bat
README.md
```

确认：

- 现有 GUI 是如何实现的
- 功能入口在哪里
- 核心转换代码在哪里
- 是否已有线程
- 是否已有进度机制
- 外部依赖有哪些
- PyInstaller 如何打包

**这一步只分析，不要立即大规模改代码。**

---

## Phase 2：建立 PySide6 基础壳

实现：

```text
main.py
 ↓
QApplication
 ↓
MainWindow
 ↓
Sidebar
 ↓
QStackedWidget
```

先确保窗口可以正常启动。

---

## Phase 3：建立 Design System

先实现：

```text
theme.qss
light.qss
dark.qss
```

并建立：

```text
颜色
字体
圆角
间距
按钮
卡片
输入框
滚动区域
```

---

## Phase 4：实现公共 Widget

依次实现：

```text
CardWidget
DropZone
PrimaryButton
SecondaryButton
Toast
EmptyState
TaskCard
```

---

## Phase 5：先做 Home

确保：

```text
首页
```

视觉已经达到最终标准。

不要一开始做全部页面。

---

## Phase 6：实现三个核心功能

顺序：

```text
文件打包
↓
格式转换
↓
资源提取
```

每实现一个页面：

```text
UI
↓
Worker
↓
Existing Core
↓
Task
↓
Success/Error
```

完整跑通。

---

## Phase 7：任务中心

实现统一：

```text
TaskManager
Worker
TaskCard
```

让三个功能共用任务系统。

---

## Phase 8：设置 / 深色模式

最后实现：

```text
Settings
Theme
QSettings
```

---

## Phase 9：打包

保证：

```text
python main.py
```

开发环境正常。

然后：

```text
build.bat
```

正常生成：

```text
ComicUtils.exe
```

---

# 56. PyInstaller 要求

最终必须测试：

```text
开发环境启动
√

PyInstaller EXE 启动
√

EXE 无 Python 环境也能启动
√
```

注意：

- Qt DLL
- SVG
- 图片
- QSS
- 图标
- 其他资源
- 第三方二进制依赖

都必须正确打包。

---

# 57. build.bat

保留现有：

```text
build.bat
```

如果现有流程可用，不要无必要删除。

可以升级为：

```bat
@echo off

echo Building Comic Utils...

pyinstaller --clean --noconfirm comic-utils.spec

if %errorlevel% neq 0 (
    echo Build failed.
    pause
    exit /b 1
)

echo Build completed.
pause
```

具体命令必须以当前 `.spec` 实际情况为准。

---

# 58. 验收标准

开发完成后必须逐项验证。

## 启动

- [ ] Python 开发环境可以启动
- [ ] EXE 可以启动
- [ ] 无控制台黑框
- [ ] 窗口标题正确
- [ ] 图标正确

## UI

- [ ] 侧边栏正常
- [ ] 页面切换正常
- [ ] Light Mode 正常
- [ ] Dark Mode 正常
- [ ] 窗口缩放不变形
- [ ] 高 DPI 下正常

## 文件操作

- [ ] 可以拖文件
- [ ] 可以拖文件夹
- [ ] 可以点击选择
- [ ] 可以批量添加
- [ ] 非法文件正确提示

## 打包

- [ ] Folder → CBZ
- [ ] Folder → ZIP
- [ ] Folder → PDF
- [ ] Folder → EPUB
- [ ] Folder → 7Z

## 转换

- [ ] RAR 输入
- [ ] MOBI 输入
- [ ] CBZ 输入
- [ ] ZIP 输入
- [ ] PDF 输入
- [ ] EPUB 输入
- [ ] 7Z 输入

## 提取

- [ ] RAR
- [ ] MOBI
- [ ] CBZ
- [ ] ZIP
- [ ] PDF
- [ ] EPUB
- [ ] 7Z

## 任务

- [ ] 后台任务不阻塞 UI
- [ ] 显示进度
- [ ] 显示状态
- [ ] 成功状态
- [ ] 失败状态
- [ ] 重试
- [ ] 取消

---

# 59. Gemini 开发时必须遵守的工作方式

这是非常重要的一部分。

## 规则 1

**先阅读现有代码，再修改。**

不要在不了解现有架构的情况下：

```text
直接删除 src
直接重写 main.py
```

---

## 规则 2

优先复用现有核心逻辑。

只有发现代码本身存在严重架构问题时，才重构核心。

---

## 规则 3

每完成一个阶段都确保程序可运行。

推荐：

```text
阶段 1 → 可运行
阶段 2 → 可运行
阶段 3 → 可运行
阶段 4 → 可运行
```

不要一次修改 50 个文件后才首次启动。

---

## 规则 4

修改代码前先说明：

```text
将修改哪些文件
为什么修改
是否影响现有功能
```

---

## 规则 5

不要为了“现代化”引入大量不必要依赖。

优先：

```text
PySide6
标准库
已有依赖
```

只有真正需要时再增加依赖。

---

## 规则 6

不要把 Web 技术混进本方案。

本阶段不要：

```text
Electron
React
Vue
Tauri
HTML
CSS Web
```

UI 使用：

```text
PySide6 + QSS
```

---

# 60. 建议 Gemini 生成代码时的优先级

优先保证：

```text
功能正确
>
线程正确
>
页面结构正确
>
UI 样式
>
动画
```

不要为了漂亮而破坏功能。

---

# 61. 最终视觉目标

最终效果应该接近：

```text
现代桌面工具
+
现代文件管理器
+
现代下载器
+
漫画工具
```

整体感觉：

```text
┌─────────────────────────────────────────────┐
│ Comic Utils                           ─ □ × │
│                                             │
│ ┌───────────┐ ┌───────────────────────────┐ │
│ │           │ │                           │ │
│ │ 首页      │ │     漫画工具箱             │ │
│ │           │ │                           │ │
│ │ 文件打包   │ │  ┌─────────┐ ┌─────────┐ │ │
│ │           │ │  │  📦     │ │   🔄    │ │ │
│ │ 格式转换   │ │  │ 打包     │ │  转换    │ │ │
│ │           │ │  └─────────┘ └─────────┘ │ │
│ │ 提取资源   │ │                           │ │
│ │           │ │  最近任务                  │ │
│ │ 任务      │ │  ┌─────────────────────┐ │ │
│ │           │ │  │ ✓ xxx.cbz           │ │ │
│ │           │ │  └─────────────────────┘ │ │
│ │           │ │                           │ │
│ │ 设置      │ │                           │ │
│ └───────────┘ └───────────────────────────┘ │
└─────────────────────────────────────────────┘
```

整体要有：

- 明确导航
- 清晰层级
- 大面积留白
- 高可读性
- 一致圆角
- 一致图标
- 一致色彩
- 状态明确

---

# 62. 最终交付物

开发完成后必须至少包含：

```text
1. 完整 PySide6 GUI
2. 现代化 QSS
3. Light / Dark
4. 侧边栏
5. 首页
6. 文件打包
7. 格式转换
8. 资源提取
9. 任务中心
10. 设置
11. Toast / Dialog
12. 拖拽支持
13. Worker 后台任务
14. 错误处理
15. EXE 打包
16. 更新后的 README
```

---

# 63. 最终要求：不要只“美化”

**本任务不是：**

```text
旧按钮
↓
新颜色
```

**本任务是：**

```text
传统工具型 GUI
        ↓
重新设计信息架构
        ↓
重新设计交互流程
        ↓
建立 Design System
        ↓
使用 PySide6 实现
        ↓
统一任务系统
        ↓
现代桌面应用
```

最终用户应该感觉：

> “这是一个专门做漫画/电子书处理的现代桌面软件。”

而不是：

> “这是一个 Python 脚本套了一个窗口。”

---

# 64. 给 Gemini 的执行指令

请严格按照以下流程执行：

```text
第一步：
完整检查现有项目结构。

第二步：
找到 GUI、业务逻辑、转换逻辑、打包逻辑、文件处理逻辑。

第三步：
评估哪些代码可以直接复用。

第四步：
建立 PySide6 App Shell。

第五步：
建立 Design System 和 QSS。

第六步：
实现 Sidebar + QStackedWidget。

第七步：
实现 HomePage。

第八步：
实现 PackPage。

第九步：
实现 ConvertPage。

第十步：
实现 ExtractPage。

第十一步：
实现统一 Worker / TaskManager。

第十二步：
实现 TaskPage。

第十三步：
实现 SettingsPage。

第十四步：
实现 Dark / Light Theme。

第十五步：
修复所有线程、异常、资源加载问题。

第十六步：
使用现有 PyInstaller 配置重新打包。

第十七步：
运行完整功能测试。

第十八步：
修复 UI 细节。

第十九步：
更新 README。

第二十步：
给出最终修改文件清单。
```

---

# 65. Gemini 每阶段输出要求

每完成一个阶段，输出：

```text
【本阶段完成】

修改：
- xxx.py
- xxx.qss

新增：
- xxx.py

功能：
- xxx
- xxx

验证：
- python main.py ✅
- 功能 xxx ✅

下一阶段：
xxx
```

---

# 66. 最重要的一句话

> **先把 Comic Utils 做成一个好用的软件，再把它做漂亮；不要为了视觉效果牺牲文件处理功能和稳定性。**


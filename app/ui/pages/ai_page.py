from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal
from pathlib import Path
import os

from qfluentwidgets import (
    TitleLabel, BodyLabel, SubtitleLabel, CaptionLabel, StrongBodyLabel,
    PrimaryPushButton, PushButton, SimpleCardWidget, LineEdit, ComboBox,
    SwitchSettingCard, SettingCardGroup, FluentIcon, InfoBar, TableWidget,
    ScrollArea, CheckBox as FluentCheckBox
)

from app.widgets.drop_zone import DropZoneCard
from app.widgets.file_list import FileListWidget
from src.core.ai.models import AIModelConfig, AIRenameResult, MangaStructuredMetadata
from src.core.ai.hub import AIEngineHub
from src.core.ai.renamer import TemplateRenamer
from src.core.i18n import i18n
from app.config.app_config import cfg
from app.ui.dialogs.metadata_dialog import AIMetadataDetailDialog

class AIPrecheckWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, config: AIModelConfig):
        super().__init__()
        self.config = config

    def run(self):
        try:
            hub = AIEngineHub()
            ok, msg = hub.test_connection(self.config)
            self.finished.emit(ok, msg)
        except Exception as e:
            self.finished.emit(False, str(e))

class AIPreviewWorker(QThread):
    item_parsed = Signal(str, AIRenameResult)
    all_finished = Signal()
    error = Signal(str)

    def __init__(self, files, config, template, target_lang="auto"):
        super().__init__()
        self.files = files
        self.config = config
        self.template = template
        self.target_lang = target_lang
        self.hub = AIEngineHub()
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            for f in self.files:
                if self._is_cancelled:
                    break
                p = Path(f)
                res = self.hub.parse_metadata(
                    p.name, 
                    parent_folder=p.parent.name, 
                    config=self.config, 
                    target_language=self.target_lang,
                    use_cache=True
                )
                if res.success and res.metadata:
                    ext = p.suffix if not p.is_dir() else ""
                    res.new_name = TemplateRenamer.render(res.metadata, template=self.template, extension=ext)
                self.item_parsed.emit(f, res)
            self.all_finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class AISingleParseWorker(QThread):
    finished = Signal(str, AIRenameResult)
    error = Signal(str)

    def __init__(self, file_path, config, template, target_lang="auto"):
        super().__init__()
        self.file_path = file_path
        self.config = config
        self.template = template
        self.target_lang = target_lang
        self.hub = AIEngineHub()

    def run(self):
        try:
            p = Path(self.file_path)
            # Force bypass cache on single item re-recognition
            res = self.hub.parse_metadata(
                p.name, 
                parent_folder=p.parent.name, 
                config=self.config, 
                target_language=self.target_lang,
                use_cache=False
            )
            if res.success and res.metadata:
                ext = p.suffix if not p.is_dir() else ""
                res.new_name = TemplateRenamer.render(res.metadata, template=self.template, extension=ext)
            self.finished.emit(self.file_path, res)
        except Exception as e:
            self.error.emit(str(e))

class AIPage(ScrollArea):
    def __init__(self, main_window=None):
        super().__init__()
        self.setObjectName("AIPage")
        self.setWidgetResizable(True)
        self.enableHorizontalScroll = False
        self.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        self.view = QWidget(self)
        self.view.setStyleSheet("background-color: transparent;")
        self.setWidget(self.view)

        self.main_window = main_window
        self.precheck_worker = None
        self.preview_worker = None
        self.single_worker = None
        self.row_data_map = {} # row_idx -> dict
        self._setup_ui()
        i18n.add_listener(self.retranslate)
        self.retranslate()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self.view)
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.layout.setSpacing(20)

        # Header
        self.title_label = TitleLabel("AI 智能命名与元数据整理", self.view)
        self.subtitle_label = BodyLabel(
            "大模型智能解析杂乱文件名、规范模板重命名与自动生成 ComicInfo.xml v2.1 及 Calibre metadata.opf", self.view
        )
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.subtitle_label)
        self.layout.addSpacing(4)

        # Drop Zone
        self.drop_zone = DropZoneCard(
            "拖拽漫画归档文件、电子书 (CBZ/ZIP/EPUB/PDF) 或漫画文件夹到此处，或点击选择",
            select_mode="file",
            file_filter="漫画/电子书 (*.cbz *.zip *.epub *.pdf *.mobi *.7z *.rar);;所有文件 (*.*)",
            parent=self.view
        )
        self.drop_zone.files_dropped.connect(self.on_files_dropped)
        self.layout.addWidget(self.drop_zone)

        # Folder & Scan Settings Card
        self.scan_card = SimpleCardWidget(self.view)
        scan_layout = QVBoxLayout(self.scan_card)
        scan_layout.setContentsMargins(20, 14, 20, 14)
        scan_layout.setSpacing(10)

        scan_row1 = QHBoxLayout()
        scan_row1.addWidget(StrongBodyLabel("文件夹扫描深度与语言偏好:", self.scan_card))
        scan_row1.addStretch()

        # Depth combo
        scan_row1.addWidget(CaptionLabel("扫描深度:", self.scan_card))
        self.depth_combo = ComboBox(self.scan_card)
        self.depth_combo.addItems(["仅当前层 (Depth=1)", "2 层子目录", "3 层子目录", "5 层子目录", "不限深度 (全量递归)"])
        self.depth_combo.setCurrentIndex(0)
        scan_row1.addWidget(self.depth_combo)
        scan_row1.addSpacing(16)

        # Target language combo
        scan_row1.addWidget(CaptionLabel("目标元数据与命名语言:", self.scan_card))
        self.lang_combo = ComboBox(self.scan_card)
        self.lang_combo.addItems(["自动跟随原名 (Auto)", "简体中文 (zh-CN)", "繁體中文 (zh-TW)", "日本語 (ja)", "English (en)"])
        self.lang_combo.setCurrentIndex(0)
        scan_row1.addWidget(self.lang_combo)

        # Format filters
        scan_row2 = QHBoxLayout()
        scan_row2.addWidget(CaptionLabel("关注的文件格式:", self.scan_card))
        self.chk_cbz = FluentCheckBox("CBZ / ZIP", self.scan_card)
        self.chk_cbz.setChecked(True)
        self.chk_epub = FluentCheckBox("EPUB", self.scan_card)
        self.chk_epub.setChecked(True)
        self.chk_pdf = FluentCheckBox("PDF", self.scan_card)
        self.chk_pdf.setChecked(True)
        self.chk_other = FluentCheckBox("MOBI / 7Z / RAR", self.scan_card)
        self.chk_other.setChecked(True)
        self.chk_folder = FluentCheckBox("包含图片的分卷文件夹", self.scan_card)
        self.chk_folder.setChecked(True)

        scan_row2.addWidget(self.chk_cbz)
        scan_row2.addWidget(self.chk_epub)
        scan_row2.addWidget(self.chk_pdf)
        scan_row2.addWidget(self.chk_other)
        scan_row2.addWidget(self.chk_folder)
        scan_row2.addStretch()

        scan_layout.addLayout(scan_row1)
        scan_layout.addLayout(scan_row2)
        self.layout.addWidget(self.scan_card)

        # File List
        self.file_list = FileListWidget(self.view)
        self.layout.addWidget(self.file_list)

        # Template Card
        self.template_card = SimpleCardWidget(self.view)
        tpl_layout = QVBoxLayout(self.template_card)
        tpl_layout.setContentsMargins(20, 16, 20, 16)
        tpl_layout.setSpacing(12)

        tpl_header = QHBoxLayout()
        tpl_header.addWidget(StrongBodyLabel("重命名规范模板 (Naming Template):", self.template_card))
        tpl_header.addStretch()

        self.tpl_input = LineEdit(self.template_card)
        self.tpl_input.setText(cfg.aiTemplate.value)
        self.tpl_input.setPlaceholderText("例如: [{author}] {title} - Vol.{vol:02d} [{group}]")
        self.tpl_input.textChanged.connect(self._on_template_changed)

        # Quick preset buttons
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(CaptionLabel("常用预设:", self.template_card))
        
        btn_p1 = PushButton("作者 + 标题 + 卷号", self.template_card)
        btn_p1.clicked.connect(lambda: self.tpl_input.setText("[{author}] {title} - Vol.{vol:02d} [{group}]"))
        
        btn_p2 = PushButton("系列 + 第X卷", self.template_card)
        btn_p2.clicked.connect(lambda: self.tpl_input.setText("{series} 第{vol}卷 [{group}]"))

        btn_p3 = PushButton("同人本 (社团/作者/年份)", self.template_card)
        btn_p3.clicked.connect(lambda: self.tpl_input.setText("[{circle} ({author})] {title} [{year}]"))

        preset_layout.addWidget(btn_p1)
        preset_layout.addWidget(btn_p2)
        preset_layout.addWidget(btn_p3)
        preset_layout.addStretch()

        tpl_layout.addLayout(tpl_header)
        tpl_layout.addWidget(self.tpl_input)
        tpl_layout.addLayout(preset_layout)
        self.layout.addWidget(self.template_card)

        # Settings Group
        self.setting_group = SettingCardGroup("高级选项", self.view)
        self.comicinfo_switch = SwitchSettingCard(
            FluentIcon.DOCUMENT,
            "自动生成并注入 ComicInfo.xml v2.1 与 Calibre 元数据",
            "将解析出的作者、题材、简介与标签规范化写入归档根目录，兼容 Komga/Kavita/Mihon 及 Calibre",
            parent=self.setting_group
        )
        self.comicinfo_switch.setChecked(cfg.aiAutoComicInfo.value)
        self.comicinfo_switch.checkedChanged.connect(lambda c: cfg.set(cfg.aiAutoComicInfo, c))
        self.setting_group.addSettingCard(self.comicinfo_switch)
        self.layout.addWidget(self.setting_group)

        # Actions
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.preview_btn = PushButton(FluentIcon.SEARCH, "智能解析预览", self.view)
        self.preview_btn.clicked.connect(self.run_ai_preview)
        action_layout.addWidget(self.preview_btn)

        self.start_btn = PrimaryPushButton(FluentIcon.PLAY, "一键智能重命名并写入元数据", self.view)
        self.start_btn.clicked.connect(self.start_ai_process)
        action_layout.addWidget(self.start_btn)
        self.layout.addLayout(action_layout)

        # Interactive Preview & Manual Correction Table
        self.table_card = SimpleCardWidget(self.view)
        table_card_layout = QVBoxLayout(self.table_card)
        table_card_layout.setContentsMargins(16, 16, 16, 16)
        table_card_layout.setSpacing(8)

        table_header = QHBoxLayout()
        table_header.addWidget(StrongBodyLabel("📋 AI 识别结果预览与可交互人工校对表 (双击单元格或点击「详情」可直接修正):", self.table_card))
        table_header.addStretch()
        table_card_layout.addLayout(table_header)

        self.preview_table = TableWidget(self.table_card)
        self.preview_table.setColumnCount(7)
        self.preview_table.setHorizontalHeaderLabels([
            "启用", "原始文件/目录名", "作者 (可编辑)", "系列/作品名 (可编辑)", "卷号 (可编辑)", "拟重命名为", "详情与操作"
        ])
        self.preview_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.preview_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.preview_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.preview_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.preview_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.preview_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.preview_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.preview_table.setMinimumHeight(260)
        self.preview_table.itemChanged.connect(self._on_table_item_changed)
        
        table_card_layout.addWidget(self.preview_table)
        self.table_card.hide()
        self.layout.addWidget(self.table_card)

        self.layout.addStretch()

    def _get_target_lang_code(self) -> str:
        idx = self.lang_combo.currentIndex()
        mapping = {0: "auto", 1: "zh-CN", 2: "zh-TW", 3: "ja", 4: "en"}
        return mapping.get(idx, "auto")

    def _get_allowed_extensions(self):
        exts = set()
        if self.chk_cbz.isChecked():
            exts.update(['.cbz', '.zip'])
        if self.chk_epub.isChecked():
            exts.add('.epub')
        if self.chk_pdf.isChecked():
            exts.add('.pdf')
        if self.chk_other.isChecked():
            exts.update(['.mobi', '.7z', '.rar'])
        return exts

    def _get_max_depth(self) -> int:
        idx = self.depth_combo.currentIndex()
        if idx == 0: return 1
        if idx == 1: return 2
        if idx == 2: return 3
        if idx == 3: return 5
        return 9999

    def _collect_files_from_paths(self, input_paths):
        allowed_exts = self._get_allowed_extensions()
        allow_folders = self.chk_folder.isChecked()
        max_depth = self._get_max_depth()

        collected = []
        for p_str in input_paths:
            p = Path(p_str)
            if not p.exists():
                continue
            if p.is_file():
                if p.suffix.lower() in allowed_exts or not allowed_exts:
                    collected.append(str(p))
            elif p.is_dir():
                base_depth = len(p.parts)
                for root, dirs, files in os.walk(p):
                    cur_depth = len(Path(root).parts) - base_depth + 1
                    if cur_depth > max_depth:
                        continue
                    
                    # Check files
                    for file in files:
                        ext = os.path.splitext(file)[1].lower()
                        if ext in allowed_exts:
                            collected.append(os.path.join(root, file))

                    # If allow_folders and folder contains images directly
                    if allow_folders:
                        from src.core.utils import is_image_file
                        if any(is_image_file(f) for f in files) and not any(os.path.splitext(f)[1].lower() in allowed_exts for f in files):
                            collected.append(root)

        return list(dict.fromkeys(collected))

    def on_files_dropped(self, paths):
        resolved = self._collect_files_from_paths(paths)
        if resolved:
            self.file_list.add_files(resolved)
        else:
            InfoBar.warning("提示", "未找到符合过滤条件的漫画文件或文件夹", parent=self, duration=2000)

    def _get_ai_config(self) -> AIModelConfig:
        return AIModelConfig(
            provider=cfg.aiProvider.value,
            model_name=cfg.aiModelName.value,
            base_url=cfg.aiBaseUrl.value,
            api_key=cfg.aiApiKey.value
        )

    def _validate_ai_config(self) -> bool:
        """ Validates whether user has filled all required AI configuration credentials """
        config = self._get_ai_config()
        if config.provider == "openai_compatible":
            if not config.base_url or not config.base_url.strip():
                InfoBar.warning("未配置 Base URL", "请前往「设置」页面填写 API Base URL 端点", parent=self, duration=3000)
                return False
            if not config.model_name or not config.model_name.strip():
                InfoBar.warning("未配置模型名称", "请前往「设置」页面填写模型名称 (如 deepseek-chat)", parent=self, duration=3000)
                return False
            if not config.api_key and "localhost" not in config.base_url and "127.0.0.1" not in config.base_url:
                InfoBar.warning("未配置 API Key", "请前往「设置」页面填写 API Key 凭据", parent=self, duration=3000)
                return False
        elif config.provider == "google_gemini":
            if not config.api_key or not config.api_key.strip():
                InfoBar.warning("未配置 Gemini Key", "请前往「设置」页面填写 Google Gemini API Key", parent=self, duration=3000)
                return False
        return True

    def _on_template_changed(self, text):
        cfg.set(cfg.aiTemplate, text)
        self._refresh_all_rename_previews()

    def _refresh_all_rename_previews(self):
        self.preview_table.blockSignals(True)
        for row in range(self.preview_table.rowCount()):
            self._update_row_rename_preview(row)
        self.preview_table.blockSignals(False)

    def _update_row_rename_preview(self, row: int):
        f_path = self.row_data_map.get(row, {}).get('file_path', '')
        meta = self.row_data_map.get(row, {}).get('metadata', None)
        if not meta:
            return

        # Read edited cells
        author_item = self.preview_table.item(row, 2)
        title_item = self.preview_table.item(row, 3)
        vol_item = self.preview_table.item(row, 4)

        if author_item: meta.author = author_item.text().strip()
        if title_item: meta.title = title_item.text().strip(); meta.series = meta.title
        if vol_item:
            try:
                meta.volume = int(vol_item.text().strip())
            except Exception:
                pass

        ext = Path(f_path).suffix if not Path(f_path).is_dir() else ""
        new_name = TemplateRenamer.render(meta, template=self.tpl_input.text(), extension=ext)
        self.preview_table.setItem(row, 5, QTableWidgetItem(new_name))

    def _on_table_item_changed(self, item: QTableWidgetItem):
        row = item.row()
        col = item.column()
        if col in (2, 3, 4): # Author, Title, Volume edited
            self.preview_table.blockSignals(True)
            self._update_row_rename_preview(row)
            self.preview_table.blockSignals(False)

    def _show_metadata_detail(self, row: int):
        row_info = self.row_data_map.get(row)
        if not row_info or not row_info.get('metadata'):
            return

        fp = row_info['file_path']
        meta = row_info['metadata']

        dialog = AIMetadataDetailDialog(Path(fp).name, meta, self.window())
        if dialog.exec():
            updated_meta = dialog.get_updated_metadata()
            self.row_data_map[row]['metadata'] = updated_meta
            self.preview_table.blockSignals(True)
            self.preview_table.setItem(row, 2, QTableWidgetItem(updated_meta.author))
            self.preview_table.setItem(row, 3, QTableWidgetItem(updated_meta.title))
            self.preview_table.setItem(row, 4, QTableWidgetItem(str(updated_meta.volume or "")))
            self._update_row_rename_preview(row)
            self.preview_table.blockSignals(False)
            InfoBar.success("元数据已更新", f"{Path(fp).name} 详细信息已修正", parent=self, duration=2000)

    def run_ai_preview(self):
        raw_files = self.file_list.get_files()
        if not raw_files:
            InfoBar.warning("提示", "请先在上方列表中添加漫画文件或文件夹", parent=self, duration=2000)
            return

        if not self._validate_ai_config():
            return

        files = self._collect_files_from_paths(raw_files)
        config = self._get_ai_config()

        self.preview_btn.setEnabled(False)
        self.preview_btn.setText("正在测试 AI 服务连接...")

        # 1. First test connection asynchronously
        self.precheck_worker = AIPrecheckWorker(config)
        
        def on_precheck_done(ok: bool, msg: str):
            if not ok:
                self.preview_btn.setEnabled(True)
                self.preview_btn.setText("智能解析预览")
                InfoBar.error("AI 服务连接失败", f"无法连通大模型: {msg}，请检查「设置」中的 Key 与端点", parent=self, duration=4000)
                return

            # Connection test passed, run preview
            self.table_card.show()
            self.preview_table.blockSignals(True)
            self.preview_table.setRowCount(0)
            self.preview_table.blockSignals(False)
            self.row_data_map.clear()

            self.preview_btn.setText("正在调用 AI 解析中...")

            target_lang = self._get_target_lang_code()
            self.preview_worker = AIPreviewWorker(files, config, self.tpl_input.text(), target_lang=target_lang)
            self.preview_worker.item_parsed.connect(self._on_item_parsed)
            self.preview_worker.all_finished.connect(self._on_preview_finished)
            self.preview_worker.error.connect(self._on_preview_error)
            self.preview_worker.start()

        self.precheck_worker.finished.connect(on_precheck_done)
        self.precheck_worker.start()

    def _on_item_parsed(self, file_path, result: AIRenameResult):
        self.preview_table.blockSignals(True)
        row = self.preview_table.rowCount()
        self.preview_table.insertRow(row)

        orig_name = Path(file_path).name
        meta = result.metadata or MangaStructuredMetadata(title=Path(file_path).stem)
        author = meta.author
        title = meta.title or meta.series
        vol = str(meta.volume) if meta.volume is not None else ""
        new_name = result.new_name or orig_name

        self.row_data_map[row] = {
            "file_path": file_path,
            "metadata": meta,
            "result": result
        }

        # 0. Checkbox
        chk = FluentCheckBox(self.preview_table)
        chk.setChecked(result.success)
        self.preview_table.setCellWidget(row, 0, chk)

        # 1. Orig Name (ReadOnly)
        orig_item = QTableWidgetItem(orig_name)
        orig_item.setFlags(orig_item.flags() & ~Qt.ItemIsEditable)
        self.preview_table.setItem(row, 1, orig_item)

        # 2. Author (Editable)
        self.preview_table.setItem(row, 2, QTableWidgetItem(author))

        # 3. Title (Editable)
        self.preview_table.setItem(row, 3, QTableWidgetItem(title))

        # 4. Vol (Editable)
        self.preview_table.setItem(row, 4, QTableWidgetItem(vol))

        # 5. New Name (Live preview)
        new_item = QTableWidgetItem(new_name)
        new_item.setFlags(new_item.flags() & ~Qt.ItemIsEditable)
        self.preview_table.setItem(row, 5, new_item)

        # 6. Action Buttons: Details & Single Re-parse
        btn_widget = QWidget(self.preview_table)
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(4, 2, 4, 2)
        btn_layout.setSpacing(6)

        detail_btn = PushButton(FluentIcon.INFO, "详情", btn_widget)
        detail_btn.setFixedHeight(28)
        detail_btn.clicked.connect(lambda _, r=row: self._show_metadata_detail(r))

        reparse_btn = PushButton(FluentIcon.SYNC, "重新识别", btn_widget)
        reparse_btn.setFixedHeight(28)
        reparse_btn.clicked.connect(lambda _, r=row, fp=file_path: self._single_reparse_row(r, fp))

        btn_layout.addWidget(detail_btn)
        btn_layout.addWidget(reparse_btn)
        self.preview_table.setCellWidget(row, 6, btn_widget)

        self.preview_table.blockSignals(False)

    def _single_reparse_row(self, row: int, file_path: str):
        config = self._get_ai_config()
        target_lang = self._get_target_lang_code()
        
        btn_widget = self.preview_table.cellWidget(row, 6)
        
        self.single_worker = AISingleParseWorker(file_path, config, self.tpl_input.text(), target_lang=target_lang)
        
        def on_single_done(fp, res: AIRenameResult):
            if res.success and res.metadata:
                self.preview_table.blockSignals(True)
                self.row_data_map[row] = {"file_path": fp, "metadata": res.metadata, "result": res}
                self.preview_table.setItem(row, 2, QTableWidgetItem(res.metadata.author))
                self.preview_table.setItem(row, 3, QTableWidgetItem(res.metadata.title))
                self.preview_table.setItem(row, 4, QTableWidgetItem(str(res.metadata.volume or "")))
                self.preview_table.setItem(row, 5, QTableWidgetItem(res.new_name))
                self.preview_table.blockSignals(False)
                InfoBar.success("单项更新成功", f"{Path(fp).name} 已重新解析完成", parent=self, duration=2000)
            else:
                InfoBar.error("识别失败", res.error_message or "AI 未能提取出有效数据", parent=self, duration=3000)

        self.single_worker.finished.connect(on_single_done)
        self.single_worker.start()

    def _on_preview_finished(self):
        self.preview_btn.setEnabled(True)
        self.preview_btn.setText("智能解析预览")
        InfoBar.success("解析完成", "所有文件已解析完毕，您可点击「详情」查看完整元数据或双击表格修改", parent=self, duration=3500)

    def _on_preview_error(self, err_msg):
        self.preview_btn.setEnabled(True)
        self.preview_btn.setText("智能解析预览")
        InfoBar.error("解析失败", f"AI 解析报错: {err_msg}", parent=self, duration=3500)

    def start_ai_process(self):
        if not self._validate_ai_config():
            return

        config = self._get_ai_config()
        template = self.tpl_input.text()
        inject_ci = self.comicinfo_switch.isChecked()
        target_lang = self._get_target_lang_code()

        from app.models.task import Task
        from app.workers.task_manager import TaskManager

        tm = TaskManager.get_instance()
        tasks_count = 0

        # If table has items, execute based on checked table rows
        if self.preview_table.rowCount() > 0:
            for row in range(self.preview_table.rowCount()):
                chk_widget = self.preview_table.cellWidget(row, 0)
                if chk_widget and not chk_widget.isChecked():
                    continue

                row_info = self.row_data_map.get(row)
                if not row_info:
                    continue

                fp = row_info['file_path']
                meta = row_info['metadata']

                task = Task(
                    "ai_process",
                    Path(fp),
                    None,
                    config=config,
                    template=template,
                    target_language=target_lang,
                    inject_comicinfo=inject_ci,
                    override_metadata=meta
                )
                tm.add_task(task)
                tasks_count += 1
        else:
            raw_files = self.file_list.get_files()
            if not raw_files:
                InfoBar.warning("提示", "请先添加要整理的漫画文件或文件夹", parent=self, duration=2000)
                return
            files = self._collect_files_from_paths(raw_files)
            for f in files:
                task = Task(
                    "ai_process",
                    Path(f),
                    None,
                    config=config,
                    template=template,
                    target_language=target_lang,
                    inject_comicinfo=inject_ci
                )
                tm.add_task(task)
                tasks_count += 1

        self.file_list.clear()
        self.preview_table.setRowCount(0)
        self.table_card.hide()
        self.main_window.switchTo(self.main_window.task_interface)

    def retranslate(self):
        self.title_label.setText(i18n.get("ai_title") or "AI 智能命名与元数据整理")
        self.subtitle_label.setText(
            i18n.get("ai_subtitle") or "大模型智能解析杂乱文件名、规范模板重命名与自动生成 ComicInfo.xml v2.1 及 Calibre metadata.opf"
        )
        self.drop_zone.label.setText(i18n.get("ai_drop_text") or "拖拽漫画归档文件 (CBZ/ZIP/EPUB/PDF) 到此处，或点击选择")
        self.start_btn.setText(i18n.get("btn_start_ai") or "一键智能重命名并写入元数据")

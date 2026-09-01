from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from pathlib import Path
import os

from qfluentwidgets import (
    TitleLabel, BodyLabel, SubtitleLabel, CaptionLabel, StrongBodyLabel,
    PrimaryPushButton, PushButton, SimpleCardWidget,
    ComboBoxSettingCard, SwitchSettingCard, SettingCardGroup, RangeSettingCard,
    FluentIcon, InfoBar, ProgressBar, ScrollArea
)

from app.widgets.drop_zone import DropZoneCard
from app.widgets.file_list import FileListWidget
from src.core.optimizer.models import OptimizerProfile
from src.core.optimizer.estimator import FastSamplingEstimator
from src.core.i18n import i18n
from app.config.app_config import cfg

class QuickEstimateWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, file_path: str, profile: OptimizerProfile):
        super().__init__()
        self.file_path = file_path
        self.profile = profile

    def run(self):
        try:
            res = FastSamplingEstimator.estimate_archive(self.file_path, self.profile)
            self.finished.emit(res)
        except Exception as e:
            self.error.emit(str(e))

class OptimizerPage(ScrollArea):
    def __init__(self, main_window=None):
        super().__init__()
        self.setObjectName("OptimizerPage")
        self.setWidgetResizable(True)
        self.enableHorizontalScroll = False
        self.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        self.view = QWidget(self)
        self.view.setStyleSheet("background-color: transparent;")
        self.setWidget(self.view)

        self.main_window = main_window
        self.estimate_worker = None
        self._setup_ui()
        i18n.add_listener(self.retranslate)
        self.retranslate()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self.view)
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.layout.setSpacing(20)

        # Header
        self.title_label = TitleLabel(i18n.get("opt_title") or "漫画体积与画质优化", self.view)
        self.subtitle_label = BodyLabel(
            i18n.get("opt_subtitle") or "WebP/JPEG 智能转码、黑白单通道灰度降维与封面画质特权保护", self.view
        )
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.subtitle_label)
        self.layout.addSpacing(4)

        # Drop Zone
        self.drop_zone = DropZoneCard(
            i18n.get("opt_drop_text") or "拖拽漫画归档文件 (CBZ/ZIP) 到此处，或点击选择",
            select_mode="file",
            file_filter="漫画归档文件 (*.cbz *.zip);;所有文件 (*.*)",
            parent=self.view
        )
        self.drop_zone.files_dropped.connect(self.on_files_dropped)
        self.layout.addWidget(self.drop_zone)

        # File List
        self.file_list = FileListWidget(self.view)
        self.layout.addWidget(self.file_list)

        # Sampling Estimate Card
        self.estimate_card = SimpleCardWidget(self.view)
        est_layout = QHBoxLayout(self.estimate_card)
        est_layout.setContentsMargins(20, 14, 20, 14)
        est_layout.setSpacing(16)

        est_info_layout = QVBoxLayout()
        est_info_layout.setSpacing(4)
        self.est_title = StrongBodyLabel("快速采样体积预估", self.estimate_card)
        self.est_desc = CaptionLabel("点击右侧按钮，抽样 4 张关键帧毫秒级预估优化后体积与降幅", self.estimate_card)
        est_info_layout.addWidget(self.est_title)
        est_info_layout.addWidget(self.est_desc)
        est_layout.addLayout(est_info_layout, 1)

        self.est_btn = PushButton(FluentIcon.SEARCH, "快速试算预估", self.estimate_card)
        self.est_btn.clicked.connect(self.run_fast_estimate)
        est_layout.addWidget(self.est_btn)
        self.layout.addWidget(self.estimate_card)

        # Settings Group
        self.setting_group = SettingCardGroup("优化方案与参数设置", self.view)

        # 1. Preset card
        self.preset_card = ComboBoxSettingCard(
            cfg.optPreset,
            FluentIcon.SPEED_HIGH,
            "优化预设方案",
            "选择内置的高性能压缩方案或进行个性化调整",
            texts=[
                "极致压缩 (WebP + 自动黑白灰度 + 2K限制)",
                "高清平衡 (JPEG + Q80)",
                "自定义参数"
            ],
            parent=self.setting_group
        )
        self.setting_group.addSettingCard(self.preset_card)

        # 2. Target Format
        self.format_card = ComboBoxSettingCard(
            cfg.optTargetFormat,
            FluentIcon.TILES,
            "目标图像格式",
            "WebP 可大幅减小体积，JPEG 兼具高通用性",
            texts=["WebP (推荐)", "JPEG", "PNG (无损)", "保持原格式 (仅压缩/降采样)"],
            parent=self.setting_group
        )
        self.setting_group.addSettingCard(self.format_card)

        # 3. Quality Slider
        self.quality_card = RangeSettingCard(
            cfg.optQuality,
            FluentIcon.PHOTO,
            "画面质量 (Quality)",
            "内页图像的压缩质量 (推荐 75 - 85)",
            parent=self.setting_group
        )
        self.setting_group.addSettingCard(self.quality_card)

        # 4. Max Dimension
        self.dimension_card = ComboBoxSettingCard(
            cfg.optMaxDimension,
            FluentIcon.ZOOM_IN,
            "最大分辨率限制 (Lanczos3 下采样)",
            "超出设定像素时按比例缩小以显著降低体积",
            texts=["不限制原尺寸", "1920 px (1080P)", "2160 px (2K 推荐)", "2560 px (2.5K)", "3840 px (4K)"],
            parent=self.setting_group
        )
        self.setting_group.addSettingCard(self.dimension_card)

        # 5. Auto Grayscale Switch
        self.grayscale_card = SwitchSettingCard(
            FluentIcon.BRUSH,
            "智能黑白漫画单通道灰度化",
            "自动识别实质黑白页面并转为 8-bit 单通道灰度图，立减 33%+ 体积",
            parent=self.setting_group
        )
        self.grayscale_card.setChecked(cfg.optAutoGrayscale.value)
        self.setting_group.addSettingCard(self.grayscale_card)

        # 6. Output Mode
        self.output_card = ComboBoxSettingCard(
            cfg.optOutputMode,
            FluentIcon.FOLDER,
            "输出模式",
            "选择优化后文件的存储位置与命名方式",
            texts=["添加后缀 (如 _optimized.cbz)", "原地原子覆盖 (安全备份)", "输出到新文件夹"],
            parent=self.setting_group
        )
        self.setting_group.addSettingCard(self.output_card)

        self.layout.addWidget(self.setting_group)

        # Actions
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        self.start_btn = PrimaryPushButton(FluentIcon.PLAY, "开始批量优化", self.view)
        self.start_btn.clicked.connect(self.start_optimization)
        action_layout.addWidget(self.start_btn)
        self.layout.addLayout(action_layout)

        self.layout.addStretch()

    def on_files_dropped(self, paths):
        valid = [p for p in paths if p.lower().endswith(('.cbz', '.zip'))]
        if valid:
            self.file_list.add_files(valid)
        else:
            InfoBar.warning("提示", "请添加 CBZ 或 ZIP 格式的漫画归档文件", parent=self, duration=2000)

    def _build_profile_from_ui(self) -> OptimizerProfile:
        preset_val = cfg.optPreset.value
        if preset_val == "extreme_webp":
            profile = OptimizerProfile.preset_extreme_webp()
        elif preset_val == "balanced_jpeg":
            profile = OptimizerProfile.preset_balanced_jpeg()
        else:
            profile = OptimizerProfile()
            fmt_map = {"WebP (推荐)": "webp", "JPEG": "jpeg", "PNG (无损)": "png", "保持原格式 (仅压缩/降采样)": "original"}
            profile.target_format = fmt_map.get(self.format_card.comboBox.currentText(), "webp")
            profile.quality = self.quality_card.slider.value()
            profile.cover_quality = min(100, profile.quality + 12)
            
            dim_map = {"不限制原尺寸": 0, "1920 px (1080P)": 1920, "2160 px (2K 推荐)": 2160, "2560 px (2.5K)": 2560, "3840 px (4K)": 3840}
            profile.max_dimension = dim_map.get(self.dimension_card.comboBox.currentText(), 2160)
            profile.auto_grayscale = self.grayscale_card.isChecked()

        # Output mode
        out_mode_map = {"添加后缀 (如 _optimized.cbz)": "suffix", "原地原子覆盖 (安全备份)": "overwrite", "输出到新文件夹": "new_folder"}
        profile.output_mode = out_mode_map.get(self.output_card.comboBox.currentText(), "suffix")
        profile.keep_backup = cfg.optKeepBackup.value
        return profile

    def run_fast_estimate(self):
        files = self.file_list.get_files()
        if not files:
            InfoBar.warning("提示", "请先在上方列表中添加漫画文件进行抽样预估", parent=self, duration=2000)
            return

        target_file = files[0]
        profile = self._build_profile_from_ui()
        self.est_btn.setEnabled(False)
        self.est_desc.setText("正在抽样关键帧并计算预估压缩率...")

        self.estimate_worker = QuickEstimateWorker(target_file, profile)
        self.estimate_worker.finished.connect(self._on_estimate_done)
        self.estimate_worker.error.connect(self._on_estimate_error)
        self.estimate_worker.start()

    def _on_estimate_done(self, res):
        self.est_btn.setEnabled(True)
        if "error" in res:
            self.est_desc.setText(f"预估失败: {res['error']}")
            return

        orig_mb = round(res['original_size'] / (1024 * 1024), 2)
        opt_mb = round(res['estimated_size'] / (1024 * 1024), 2)
        ratio = res['saved_ratio']
        gray = res.get('grayscale_rate', 0.0)

        self.est_desc.setText(
            f"抽样分析结果：原大小 {orig_mb} MB ➔ 预估优化后 {opt_mb} MB (预计减小 {ratio}% | 黑白单通道占比 {gray}%)"
        )
        InfoBar.success("预估完成", f"预计可为当前漫画减少约 {ratio}% 的存储占用！", parent=self, duration=3000)

    def _on_estimate_error(self, err_msg):
        self.est_btn.setEnabled(True)
        self.est_desc.setText(f"试算出错: {err_msg}")

    def start_optimization(self):
        files = self.file_list.get_files()
        if not files:
            InfoBar.warning("提示", "请先添加要优化的漫画归档文件", parent=self, duration=2000)
            return

        profile = self._build_profile_from_ui()
        from app.models.task import Task
        from app.workers.task_manager import TaskManager

        tm = TaskManager.get_instance()
        for f in files:
            task = Task("optimize", Path(f), None, profile=profile)
            tm.add_task(task)

        self.file_list.clear()
        self.main_window.switchTo(self.main_window.task_interface)

    def retranslate(self):
        self.title_label.setText(i18n.get("opt_title") or "漫画体积与画质优化")
        self.subtitle_label.setText(i18n.get("opt_subtitle") or "WebP/JPEG 智能转码、黑白单通道灰度降维与封面画质特权保护")
        self.drop_zone.label.setText(i18n.get("opt_drop_text") or "拖拽漫画归档文件 (CBZ/ZIP) 到此处，或点击选择")
        self.start_btn.setText("🚀 开始批量优化")

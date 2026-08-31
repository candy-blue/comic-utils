import os
import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap, QIcon
from qfluentwidgets import (TitleLabel, SubtitleLabel, BodyLabel, CaptionLabel,
                             SettingCardGroup, HyperlinkCard, PrimaryPushSettingCard,
                             SwitchSettingCard, PushSettingCard, SimpleCardWidget,
                             FluentIcon, InfoBar, InfoBarPosition, MessageBox,
                             ProgressBar, Dialog)

from app.services.update_service import (APP_VERSION, GITHUB_URL, 
                                         UpdateCheckWorker, UpdateDownloadWorker)
from app.config.app_config import cfg
from src.core.i18n import i18n

class AboutPage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.setObjectName("AboutPage")
        self.setStyleSheet(f"#{self.objectName()} {{ background-color: transparent; }}")
        self.main_window = main_window
        self.check_worker = None
        self.download_worker = None
        self._setup_ui()
        i18n.add_listener(self.retranslate)
        self.retranslate()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.layout.setSpacing(24)

        # Header
        self.title_label = TitleLabel(i18n.get("about_title"), self)
        self.subtitle_label = BodyLabel(i18n.get("about_subtitle"), self)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.subtitle_label)
        self.layout.addSpacing(8)

        # App Hero Card
        hero_card = SimpleCardWidget(self)
        hero_layout = QHBoxLayout(hero_card)
        hero_layout.setContentsMargins(24, 24, 24, 24)
        hero_layout.setSpacing(20)

        # App Icon
        icon_label = QLabel(hero_card)
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        icon_png = os.path.join(base_path, "src", "assets", "icon.png")
        if not os.path.exists(icon_png):
            icon_png = os.path.join(base_path, "src", "assets", "icon.ico")

        if os.path.exists(icon_png):
            pix = QPixmap(icon_png).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pix)
        icon_label.setFixedSize(64, 64)
        hero_layout.addWidget(icon_label)

        # Info texts
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)

        self.name_lbl = SubtitleLabel("Comic Utils", hero_card)
        self.ver_lbl = CaptionLabel(i18n.get("about_version", APP_VERSION), hero_card)
        self.desc_lbl = BodyLabel(i18n.get("about_desc"), hero_card)

        text_layout.addWidget(self.name_lbl)
        text_layout.addWidget(self.ver_lbl)
        text_layout.addWidget(self.desc_lbl)
        hero_layout.addLayout(text_layout)
        hero_layout.addStretch()

        self.layout.addWidget(hero_card)

        # Software Update Group
        self.update_group = SettingCardGroup(i18n.get("about_group_update"), self)

        self.check_card = PrimaryPushSettingCard(
            i18n.get("about_check_update"),
            FluentIcon.UPDATE,
            i18n.get("about_check_update"),
            f"Comic Utils {APP_VERSION}",
            self.update_group
        )
        self.check_card.clicked.connect(self.check_for_updates)
        self.update_group.addSettingCard(self.check_card)

        self.auto_check_card = SwitchSettingCard(
            FluentIcon.SYNC,
            i18n.get("about_auto_update_title"),
            i18n.get("about_auto_update_desc"),
            configItem=cfg.autoCheckUpdate,
            parent=self.update_group
        )
        self.update_group.addSettingCard(self.auto_check_card)
        self.layout.addWidget(self.update_group)

        # Community Group
        self.community_group = SettingCardGroup(i18n.get("about_group_community"), self)

        self.github_card = HyperlinkCard(
            GITHUB_URL,
            "GitHub",
            FluentIcon.GITHUB,
            i18n.get("about_github_title"),
            i18n.get("about_github_desc"),
            self.community_group
        )
        self.community_group.addSettingCard(self.github_card)

        self.issues_card = HyperlinkCard(
            f"{GITHUB_URL}/issues",
            "Issues",
            FluentIcon.FEEDBACK,
            i18n.get("about_issues_title"),
            i18n.get("about_issues_desc"),
            self.community_group
        )
        self.community_group.addSettingCard(self.issues_card)

        self.layout.addWidget(self.community_group)
        self.layout.addStretch()

    def retranslate(self):
        self.title_label.setText(i18n.get("about_title"))
        self.subtitle_label.setText(i18n.get("about_subtitle"))
        self.ver_lbl.setText(i18n.get("about_version", APP_VERSION))
        self.desc_lbl.setText(i18n.get("about_desc"))
        self.update_group.titleLabel.setText(i18n.get("about_group_update"))
        self.check_card.setTitle(i18n.get("about_check_update"))
        self.check_card.button.setText(i18n.get("about_check_update"))
        self.auto_check_card.setTitle(i18n.get("about_auto_update_title"))
        self.auto_check_card.setContent(i18n.get("about_auto_update_desc"))
        self.community_group.titleLabel.setText(i18n.get("about_group_community"))
        self.github_card.setTitle(i18n.get("about_github_title"))
        self.github_card.setContent(i18n.get("about_github_desc"))
        self.issues_card.setTitle(i18n.get("about_issues_title"))
        self.issues_card.setContent(i18n.get("about_issues_desc"))

    def check_for_updates(self, silent=False):
        """ Check for software updates """
        self.check_card.button.setEnabled(False)
        self.check_card.button.setText("正在检查..." if i18n.lang == "zh" else "Checking...")

        self.check_worker = UpdateCheckWorker()
        self.check_worker.finished.connect(lambda info: self._on_check_finished(info, silent))
        self.check_worker.error.connect(lambda err: self._on_check_error(err, silent))
        self.check_worker.start()

    def _on_check_finished(self, info, silent=False):
        self.check_card.button.setEnabled(True)
        self.check_card.button.setText(i18n.get("about_check_update"))

        if info["has_update"]:
            msg = MessageBox(
                "发现新版本" if i18n.lang == "zh" else "Update Available",
                f"最新版本: {info['latest_version']}\n当前版本: {info['current_version']}\n\n更新内容:\n{info['release_notes']}",
                self.window()
            )
            msg.yesButton.setText("立即更新" if i18n.lang == "zh" else "Update Now")
            msg.cancelButton.setText("取消" if i18n.lang == "zh" else "Cancel")

            if msg.exec():
                self._start_auto_update(info["download_url"], info["latest_version"])
        else:
            if not silent:
                InfoBar.success(
                    title="已是最新版本" if i18n.lang == "zh" else "Up to date",
                    content=f"当前已是最新版本 ({APP_VERSION})，无需更新。" if i18n.lang == "zh" else f"You are on the latest version ({APP_VERSION}).",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.window()
                )

    def _on_check_error(self, err, silent=False):
        self.check_card.button.setEnabled(True)
        self.check_card.button.setText(i18n.get("about_check_update"))
        if not silent:
            InfoBar.warning(
                title="检查更新失败" if i18n.lang == "zh" else "Update Check Failed",
                content=f"连接更新服务器失败: {err}" if i18n.lang == "zh" else f"Failed to check updates: {err}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3500,
                parent=self.window()
            )

    def _start_auto_update(self, download_url, version):
        """ Download update with a visual progress dialog and cancel button """
        import tempfile
        save_dir = os.path.join(tempfile.gettempdir(), "ComicUtilsUpdate")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"ComicUtils_{version}.exe")

        # Progress Dialog
        title_txt = "正在下载更新" if i18n.lang == "zh" else "Downloading Update"
        content_txt = f"正在下载新版本 {version}，请稍候..." if i18n.lang == "zh" else f"Downloading {version}, please wait..."
        progress_dialog = MessageBox(title_txt, content_txt, self.window())
        progress_dialog.yesButton.hide()
        progress_dialog.cancelButton.setText("取消下载" if i18n.lang == "zh" else "Cancel Download")

        # Add custom progress bar & label to dialog layout
        prog_bar = ProgressBar(progress_dialog)
        prog_bar.setMinimumWidth(300)
        prog_label = CaptionLabel("已下载: 0 MB (0%)", progress_dialog)
        
        progress_dialog.viewLayout.addWidget(prog_bar)
        progress_dialog.viewLayout.addWidget(prog_label)

        self.download_worker = UpdateDownloadWorker(download_url, save_path)

        def on_prog(current, total, percent):
            cur_mb = current / (1024 * 1024)
            tot_mb = total / (1024 * 1024) if total > 0 else 0
            prog_bar.setValue(percent)
            if tot_mb > 0:
                prog_label.setText(f"已下载: {cur_mb:.1f} MB / {tot_mb:.1f} MB ({percent}%)")
            else:
                prog_label.setText(f"已下载: {cur_mb:.1f} MB")

        self.download_worker.progress.connect(on_prog)
        self.download_worker.finished.connect(lambda p: (progress_dialog.close(), self._on_download_finished(p)))
        self.download_worker.error.connect(lambda e: (progress_dialog.close(), self._on_download_error(e, download_url)))

        progress_dialog.cancelButton.clicked.connect(self.download_worker.cancel)
        
        self.download_worker.start()
        progress_dialog.exec()

    def _on_download_finished(self, save_path):
        msg = MessageBox(
            "更新下载完成" if i18n.lang == "zh" else "Download Complete",
            f"新版本已成功下载至:\n{save_path}\n\n是否立即打开所在文件夹运行新版本？" if i18n.lang == "zh" else f"New version downloaded to:\n{save_path}\n\nOpen folder now?",
            self.window()
        )
        msg.yesButton.setText("打开文件夹" if i18n.lang == "zh" else "Open Folder")
        msg.cancelButton.setText("稍后处理" if i18n.lang == "zh" else "Later")
        if msg.exec():
            os.system(f'explorer.exe /select,"{os.path.normpath(save_path)}"')

    def _on_download_error(self, err, download_url):
        if err != "下载已取消":
            InfoBar.error(
                title="自动下载失败" if i18n.lang == "zh" else "Download Failed",
                content=f"下载出错: {err}，已为您打开浏览器下载页面。" if i18n.lang == "zh" else f"Download error: {err}. Opening browser page.",
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self.window()
            )
            QDesktopServices.openUrl(QUrl(download_url))

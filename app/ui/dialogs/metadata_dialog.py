from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QApplication
from PySide6.QtCore import Qt
from qfluentwidgets import (
    MessageBoxBase, SubtitleLabel, StrongBodyLabel, BodyLabel, CaptionLabel,
    LineEdit, TextEdit, FluentIcon, SimpleCardWidget
)
from src.core.ai.models import MangaStructuredMetadata

class AIMetadataDetailDialog(MessageBoxBase):
    """ Dialog to inspect and manually edit full AI-extracted metadata """

    def __init__(self, raw_filename: str, metadata: MangaStructuredMetadata, parent=None):
        if parent is None:
            parent = QApplication.activeWindow()
        super().__init__(parent)
        self.raw_filename = raw_filename
        self.metadata = metadata
        self.setFixedWidth(680)

        self.title_label = SubtitleLabel("AI 元数据详细信息与校对", self)
        self.viewLayout.addWidget(self.title_label)

        # File card
        file_card = SimpleCardWidget(self)
        fc_layout = QVBoxLayout(file_card)
        fc_layout.setContentsMargins(12, 8, 12, 8)
        fc_layout.addWidget(CaptionLabel(f"源文件: {raw_filename}", file_card))
        self.viewLayout.addWidget(file_card)
        self.viewLayout.addSpacing(10)

        # Form Layout
        grid = QGridLayout()
        grid.setSpacing(12)

        # 1. Title & Original Title
        grid.addWidget(StrongBodyLabel("主标题 (Title):", self), 0, 0)
        self.title_edit = LineEdit(self)
        self.title_edit.setText(metadata.title)
        grid.addWidget(self.title_edit, 0, 1)

        grid.addWidget(StrongBodyLabel("原始日文/外文名:", self), 0, 2)
        self.orig_title_edit = LineEdit(self)
        self.orig_title_edit.setText(metadata.original_title or "")
        grid.addWidget(self.orig_title_edit, 0, 3)

        # 2. Author & Circle
        grid.addWidget(StrongBodyLabel("作者/画师 (Author):", self), 1, 0)
        self.author_edit = LineEdit(self)
        self.author_edit.setText(metadata.author)
        grid.addWidget(self.author_edit, 1, 1)

        grid.addWidget(StrongBodyLabel("同人社团 (Circle):", self), 1, 2)
        self.circle_edit = LineEdit(self)
        self.circle_edit.setText(metadata.circle or "")
        grid.addWidget(self.circle_edit, 1, 3)

        # 3. Series & Volume
        grid.addWidget(StrongBodyLabel("系列名 (Series):", self), 2, 0)
        self.series_edit = LineEdit(self)
        self.series_edit.setText(metadata.series or metadata.title)
        grid.addWidget(self.series_edit, 2, 1)

        grid.addWidget(StrongBodyLabel("卷号 (Volume):", self), 2, 2)
        self.vol_edit = LineEdit(self)
        self.vol_edit.setText(str(metadata.volume) if metadata.volume is not None else "")
        grid.addWidget(self.vol_edit, 2, 3)

        # 4. Group & Year
        grid.addWidget(StrongBodyLabel("汉化组/发布组:", self), 3, 0)
        self.group_edit = LineEdit(self)
        self.group_edit.setText(metadata.scanlation_group or "")
        grid.addWidget(self.group_edit, 3, 1)

        grid.addWidget(StrongBodyLabel("出版年份 (Year):", self), 3, 2)
        self.year_edit = LineEdit(self)
        self.year_edit.setText(str(metadata.publish_year) if metadata.publish_year else "")
        grid.addWidget(self.year_edit, 3, 3)

        # 5. Language & Rating
        grid.addWidget(StrongBodyLabel("语言 (Language):", self), 4, 0)
        self.lang_edit = LineEdit(self)
        self.lang_edit.setText(metadata.language or "zh-CN")
        grid.addWidget(self.lang_edit, 4, 1)

        grid.addWidget(StrongBodyLabel("年龄分级 (Rating):", self), 4, 2)
        self.rating_edit = LineEdit(self)
        self.rating_edit.setText(metadata.age_rating or "Unknown")
        grid.addWidget(self.rating_edit, 4, 3)

        self.viewLayout.addLayout(grid)
        self.viewLayout.addSpacing(10)

        # 6. Tags
        self.viewLayout.addWidget(StrongBodyLabel("题材标签 (Tags, 逗号分隔):", self))
        self.tags_edit = LineEdit(self)
        self.tags_edit.setText(", ".join(metadata.tags))
        self.viewLayout.addWidget(self.tags_edit)
        self.viewLayout.addSpacing(8)

        # 7. Summary
        self.viewLayout.addWidget(StrongBodyLabel("作品/本卷剧情简介 (Summary):", self))
        self.summary_edit = TextEdit(self)
        self.summary_edit.setText(metadata.summary)
        self.summary_edit.setFixedHeight(72)
        self.viewLayout.addWidget(self.summary_edit)

        # Buttons
        self.yesButton.setText("保存修正")
        self.cancelButton.setText("取消")

    def get_updated_metadata(self) -> MangaStructuredMetadata:
        """ Returns updated MangaStructuredMetadata with all edited values """
        self.metadata.title = self.title_edit.text().strip()
        self.metadata.original_title = self.orig_title_edit.text().strip() or None
        self.metadata.author = self.author_edit.text().strip()
        self.metadata.circle = self.circle_edit.text().strip() or None
        self.metadata.series = self.series_edit.text().strip() or self.metadata.title
        
        vol_txt = self.vol_edit.text().strip()
        try:
            self.metadata.volume = int(vol_txt) if vol_txt else None
        except Exception:
            pass

        self.metadata.scanlation_group = self.group_edit.text().strip() or None
        
        yr_txt = self.year_edit.text().strip()
        try:
            self.metadata.publish_year = int(yr_txt) if yr_txt else None
        except Exception:
            pass

        self.metadata.language = self.lang_edit.text().strip() or "zh-CN"
        self.metadata.age_rating = self.rating_edit.text().strip() or "Unknown"

        raw_tags = self.tags_edit.text().replace("，", ",")
        self.metadata.tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
        self.metadata.summary = self.summary_edit.toPlainText().strip()

        return self.metadata

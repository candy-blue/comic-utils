from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from qfluentwidgets import SimpleCardWidget, TitleLabel, SubtitleLabel, BodyLabel, PrimaryPushButton, IconWidget, FluentIcon
from src.core.i18n import i18n

class HomePage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.setObjectName("HomePage")
        self.setStyleSheet(f"#{self.objectName()} {{ background-color: transparent; }}")
        self.main_window = main_window
        self.cards = {}
        self._setup_ui()
        i18n.add_listener(self.retranslate)
        self.retranslate()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.layout.setSpacing(24)
        
        # Header
        self.title_label = TitleLabel(i18n.get("home_title"), self)
        self.subtitle_label = BodyLabel(i18n.get("home_subtitle"), self)
        
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.subtitle_label)
        self.layout.addSpacing(16)
        
        # Feature Cards layout
        self.features_layout = QHBoxLayout()
        self.features_layout.setSpacing(16)
        
        card1, self.c1_title, self.c1_desc, self.c1_btn = self._create_feature_card(
            FluentIcon.ZIP_FOLDER,
            i18n.get("home_card_pack_title"),
            i18n.get("home_card_pack_desc"),
            lambda: self.main_window.switchTo(self.main_window.pack_interface)
        )
        self.features_layout.addWidget(card1)
        
        card2, self.c2_title, self.c2_desc, self.c2_btn = self._create_feature_card(
            FluentIcon.SYNC,
            i18n.get("home_card_convert_title"),
            i18n.get("home_card_convert_desc"),
            lambda: self.main_window.switchTo(self.main_window.convert_interface)
        )
        self.features_layout.addWidget(card2)
        
        self.layout.addLayout(self.features_layout)
        
        self.features_layout2 = QHBoxLayout()
        self.features_layout2.setSpacing(16)
        
        card3, self.c3_title, self.c3_desc, self.c3_btn = self._create_feature_card(
            FluentIcon.DOWNLOAD,
            i18n.get("home_card_extract_title"),
            i18n.get("home_card_extract_desc"),
            lambda: self.main_window.switchTo(self.main_window.extract_interface)
        )
        self.features_layout2.addWidget(card3)
        
        # Spacer card
        empty_card = QWidget()
        self.features_layout2.addWidget(empty_card)
        
        self.layout.addLayout(self.features_layout2)
        self.layout.addStretch()

    def _create_feature_card(self, icon, title, desc, callback):
        card = SimpleCardWidget(self)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        
        icon_widget = IconWidget(icon)
        icon_widget.setFixedSize(32, 32)
        
        title_lbl = SubtitleLabel(title, card)
        desc_lbl = BodyLabel(desc, card)
        desc_lbl.setWordWrap(True)
        
        btn = PrimaryPushButton(i18n.get("btn_start_using"), card)
        btn.clicked.connect(callback)
        
        layout.addWidget(icon_widget)
        layout.addWidget(title_lbl)
        layout.addWidget(desc_lbl)
        layout.addStretch()
        layout.addWidget(btn, 0, Qt.AlignLeft)
        
        return card, title_lbl, desc_lbl, btn

    def retranslate(self):
        self.title_label.setText(i18n.get("home_title"))
        self.subtitle_label.setText(i18n.get("home_subtitle"))
        self.c1_title.setText(i18n.get("home_card_pack_title"))
        self.c1_desc.setText(i18n.get("home_card_pack_desc"))
        self.c1_btn.setText(i18n.get("btn_start_using"))
        self.c2_title.setText(i18n.get("home_card_convert_title"))
        self.c2_desc.setText(i18n.get("home_card_convert_desc"))
        self.c2_btn.setText(i18n.get("btn_start_using"))
        self.c3_title.setText(i18n.get("home_card_extract_title"))
        self.c3_desc.setText(i18n.get("home_card_extract_desc"))
        self.c3_btn.setText(i18n.get("btn_start_using"))

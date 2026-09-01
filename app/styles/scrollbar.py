from qfluentwidgets import Theme

def get_fluent_scrollbar_style(theme: Theme = Theme.LIGHT) -> str:
    """ Returns native Windows 11 Fluent sleek rounded scrollbar stylesheet """
    is_dark = (theme == Theme.DARK)

    # Color definitions
    if is_dark:
        handle_normal = "rgba(255, 255, 255, 0.22)"
        handle_hover = "rgba(255, 255, 255, 0.45)"
        handle_pressed = "rgba(255, 255, 255, 0.65)"
    else:
        handle_normal = "rgba(0, 0, 0, 0.20)"
        handle_hover = "rgba(0, 0, 0, 0.42)"
        handle_pressed = "rgba(0, 0, 0, 0.65)"

    return f"""
    /* Vertical Scrollbar */
    QScrollBar:vertical {{
        background: transparent;
        width: 12px;
        margin: 0px;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background: {handle_normal};
        min-height: 28px;
        border-radius: 3px;
        margin: 2px 3px 2px 3px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {handle_hover};
        margin: 2px 1px 2px 1px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:pressed {{
        background: {handle_pressed};
        margin: 2px 1px 2px 1px;
        border-radius: 4px;
    }}
    QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {{
        height: 0px;
        width: 0px;
        background: transparent;
        border: none;
    }}
    QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical {{
        background: transparent;
        border: none;
    }}

    /* Horizontal Scrollbar */
    QScrollBar:horizontal {{
        background: transparent;
        height: 12px;
        margin: 0px;
        border: none;
    }}
    QScrollBar::handle:horizontal {{
        background: {handle_normal};
        min-width: 28px;
        border-radius: 3px;
        margin: 3px 2px 3px 2px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {handle_hover};
        margin: 1px 2px 1px 2px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:pressed {{
        background: {handle_pressed};
        margin: 1px 2px 1px 2px;
        border-radius: 4px;
    }}
    QScrollBar::sub-line:horizontal, QScrollBar::add-line:horizontal {{
        height: 0px;
        width: 0px;
        background: transparent;
        border: none;
    }}
    QScrollBar::sub-page:horizontal, QScrollBar::add-page:horizontal {{
        background: transparent;
        border: none;
    }}
    """

DARK = """
QWidget { background: #111827; color: #e7edf7; }
QMainWindow, QWidget#welcomePage, QWidget#appPage, QWidget#utilityPage { background: #111827; }
QStackedWidget, QScrollArea, QScrollArea QWidget#qt_scrollarea_viewport { background: transparent; border: 0; }
QLabel { background: transparent; color: #e7edf7; }
QLabel#brand { color: #f4f7ff; }
QLabel#eyebrow { color: #92a0b8; }
QLabel#muted { color: #a4b0c5; }
QLabel#heroTitle { color: #f5f7ff; }
QLabel#heroIcon { color: #9b8cff; }
QLabel#pill { background: #252447; color: #c4baff; border: 1px solid #403b70; }
QFrame#heroCard { background: #192235; border: 1px solid #2b3851; }
QFrame#featureCard, QFrame#statCard, QFrame#sectionCard { background: #1a2436; border: 1px solid #2b3851; }
QLabel#featureTitle { color: #f0f3fb; }
QFrame#sidebar { background: #151e2e; border-right: 1px solid #29354a; }
QFrame#vaultBadge { background: #19342f; border: 1px solid #28584d; }
QLabel#successText { color: #73dfb3; }
QLabel#pageTitle, QLabel#sectionTitle, QLabel#statNumber { color: #f1f5fd; }
QLabel#creatorCredit { color: #8491a8; }
QLabel#dialogTitle { color: #f1f5fd; }
QLabel#auditSummary { color: #e7edf7; }
QPushButton { background: #222e43; color: #e7edf7; border: 1px solid #36445c; }
QPushButton:hover { background: #2b3a53; border-color: #6576a0; }
QPushButton:pressed { background: #1c2739; }
QPushButton:disabled { color: #77849b; background: #1a2434; border-color: #2b3548; }
QPushButton#primary { background: #7867f5; border: 1px solid #7867f5; color: #ffffff; font-weight: 750; }
QPushButton#primary:hover { background: #8a7bff; border-color: #8a7bff; }
QPushButton#nav { text-align: left; background: transparent; border: 1px solid transparent; color: #aebbd0; }
QPushButton#nav:hover { background: #202c40; }
QPushButton#nav:checked { background: #2a2c52; color: #e6e2ff; border: 1px solid #484779; font-weight: 700; }
QPushButton#lockButton { background: #222e43; border-color: #36445c; }
QPushButton#dangerButton { color: #ff9fa9; border-color: #74424d; }
QPushButton#linkButton { background: transparent; border: 0; color: #b8afff; }
QLineEdit, QTextEdit, QComboBox, QSpinBox { background: #131d2c; color: #edf2fb; border: 1px solid #34425a; border-radius: 9px; padding: 10px; selection-background-color: #6655d9; }
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #9486ff; }
QLineEdit#searchBox { padding: 12px 14px; }
QTableWidget { background: #172235; alternate-background-color: #1a263a; color: #e7edf7; border: 1px solid #2b3851; border-radius: 13px; gridline-color: transparent; selection-background-color: #393765; selection-color: #ffffff; }
QHeaderView::section { background: #202c40; color: #a9b7ce; border: 0; padding: 12px 9px; font-size: 10px; font-weight: 750; }
QTableWidget::item { padding-left: 8px; border-bottom: 1px solid #25334a; }
QTableWidget::item:selected { background: #393765; }
QScrollBar:vertical { background: transparent; width: 9px; margin: 2px; }
QScrollBar::handle:vertical { background: #465571; border-radius: 4px; min-height: 25px; }
QScrollBar::handle:vertical:hover { background: #65759a; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QStatusBar { background: #151e2e; color: #a4b0c5; border-top: 1px solid #29354a; }
QCheckBox { spacing: 8px; background: transparent; }
QDialog { background: #1a2436; }
QToolTip { background: #202c40; color: #f4f7ff; border: 1px solid #465571; padding: 5px; }
"""

LIGHT = """
QWidget { background: #f3f5fb; color: #202941; }
QMainWindow, QWidget#welcomePage, QWidget#appPage, QWidget#utilityPage { background: #f3f5fb; }
QStackedWidget, QScrollArea, QScrollArea QWidget#qt_scrollarea_viewport { background: transparent; border: 0; }
QLabel { background: transparent; color: #202941; }
QLabel#brand { color: #202941; }
QLabel#eyebrow { color: #75819a; }
QLabel#muted { color: #68758d; }
QLabel#heroTitle { color: #202941; }
QLabel#heroIcon { color: #6556db; }
QLabel#pill { background: #eceaff; color: #5144c4; border: 1px solid #d8d3ff; }
QFrame#heroCard { background: #ffffff; border: 1px solid #e0e5f0; }
QFrame#featureCard, QFrame#statCard, QFrame#sectionCard { background: #ffffff; border: 1px solid #e0e5f0; }
QLabel#featureTitle { color: #202941; }
QFrame#sidebar { background: #ffffff; border-right: 1px solid #e1e6f0; }
QFrame#vaultBadge { background: #e9f8f0; border: 1px solid #c9ead8; }
QLabel#successText { color: #147b50; }
QLabel#pageTitle, QLabel#sectionTitle, QLabel#statNumber { color: #202941; }
QLabel#dialogTitle { color: #202941; }
QLabel#auditSummary { color: #202941; }
QPushButton { background: #ffffff; color: #29334b; border: 1px solid #dce2ee; }
QPushButton:hover { background: #f0f2fb; border-color: #c1c9e0; }
QPushButton:pressed { background: #e8ebf7; }
QPushButton:disabled { color: #a3adc0; background: #f4f6fa; border-color: #e3e7f0; }
QPushButton#primary { background: #6556db; border: 1px solid #6556db; color: #ffffff; font-weight: 750; }
QPushButton#primary:hover { background: #5748c9; border-color: #5748c9; }
QPushButton#nav { text-align: left; background: transparent; border: 1px solid transparent; color: #5f6b83; }
QPushButton#nav:hover { background: #f2f3fc; }
QPushButton#nav:checked { background: #eceaff; color: #4538b8; border: 1px solid #d8d3ff; font-weight: 700; }
QPushButton#lockButton { background: #f7f8fc; border-color: #dce2ee; }
QPushButton#dangerButton { color: #b52e43; border-color: #f0cbd2; }
QPushButton#linkButton { background: transparent; border: 0; color: #5144c4; }
QLineEdit, QTextEdit, QComboBox, QSpinBox { background: #ffffff; color: #202941; border: 1px solid #dce2ee; border-radius: 9px; padding: 10px; selection-background-color: #dedbff; }
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #6556db; }
QLineEdit#searchBox { padding: 12px 14px; }
QTableWidget { background: #ffffff; alternate-background-color: #f7f8fc; color: #29334b; border: 1px solid #e0e5f0; border-radius: 13px; gridline-color: transparent; selection-background-color: #e7e4ff; selection-color: #202941; }
QHeaderView::section { background: #f0f2f9; color: #68758d; border: 0; padding: 12px 9px; font-size: 10px; font-weight: 750; }
QTableWidget::item { padding-left: 8px; border-bottom: 1px solid #edf0f6; }
QTableWidget::item:selected { background: #e7e4ff; }
QScrollBar:vertical { background: transparent; width: 9px; margin: 2px; }
QScrollBar::handle:vertical { background: #c8cfe0; border-radius: 4px; min-height: 25px; }
QScrollBar::handle:vertical:hover { background: #aeb8d0; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QStatusBar { background: #ffffff; color: #68758d; border-top: 1px solid #e1e6f0; }
QCheckBox { spacing: 8px; background: transparent; }
QDialog { background: #f3f5fb; }
QToolTip { background: #ffffff; color: #202941; border: 1px solid #dce2ee; padding: 5px; }
"""

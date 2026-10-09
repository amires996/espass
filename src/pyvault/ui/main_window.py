from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtCore import QEvent, Qt, QUrl, QTimer
from PySide6.QtGui import QAction, QDesktopServices, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from pyvault.config import Config
from pyvault.core.exceptions import PyVaultError
from pyvault.services.backup_service import BackupService
from pyvault.services.password_generator import estimate_strength, generate_password
from pyvault.services.security_audit import audit_credentials
from pyvault.services.telegram_backup import TelegramBackupService
from pyvault.services.vault_service import VaultService
from pyvault.ui.dialogs.credential_dialog import CredentialDialog
from pyvault.ui.theme_manager import DARK, LIGHT
from pyvault.utils.paths import default_vault_path, resource_path

GITHUB_URL = "https://github.com/amires996"
NAV_ITEMS = (
    ("▦", "All Items"),
    ("★", "Favorites"),
    ("▤", "Categories"),
    ("◷", "Recently Added"),
    ("⌘", "Password Generator"),
    ("◈", "Security Audit"),
    ("⚙", "Settings"),
)


class MainWindow(QMainWindow):
    """Main espass desktop window. Secrets stay in the encrypted local vault."""

    def __init__(self) -> None:
        super().__init__()
        self.config = Config()
        self.vault: VaultService | None = None
        self.page = "All Items"
        self._clipboard_token: str | None = None
        self._last_activity = time.monotonic()
        self._clipboard_timer = QTimer(self)
        self._clipboard_timer.setSingleShot(True)
        self._clipboard_timer.timeout.connect(self._clear_clipboard)
        self._idle_timer = QTimer(self)
        self._idle_timer.setInterval(5000)
        self._idle_timer.timeout.connect(self._check_idle)

        self.setWindowTitle("espass | Password Manager")
        self.setWindowIcon(QIcon(str(resource_path("assets/icons/espass.ico"))))
        self.setMinimumSize(900, 620)
        self.resize(
            int(self.config.values.get("window_width", 1240)),
            int(self.config.values.get("window_height", 800)),
        )
        self._build_ui()
        self._apply_theme()
        self._show_start()
        self.installEventFilter(self)
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)
        self._install_shortcuts()

    def _install_shortcuts(self) -> None:
        shortcuts = (
            ("Ctrl+N", self.new_credential),
            ("Ctrl+F", self.focus_search),
            ("Ctrl+G", self.show_generator),
            ("Ctrl+L", self.lock_vault),
            ("Ctrl+,", self.show_settings),
        )
        for sequence, callback in shortcuts:
            action = QAction(self)
            action.setShortcut(QKeySequence(sequence))
            action.triggered.connect(callback)
            self.addAction(action)

    def _build_ui(self) -> None:
        self.root_stack = QStackedWidget()
        self.setCentralWidget(self.root_stack)
        self.start_page = self._build_start_page()
        self.app_page = self._build_app_page()
        self.root_stack.addWidget(self.start_page)
        self.root_stack.addWidget(self.app_page)
        self.statusBar().showMessage("Your vault stays encrypted on this device.")

    def _build_start_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("welcomePage")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(44, 30, 44, 22)
        top = QHBoxLayout()
        brand = QLabel("◈  espass")
        brand.setObjectName("brand")
        top.addWidget(brand)
        top.addStretch()
        badge = QLabel("PRIVATE BY DESIGN")
        badge.setObjectName("pill")
        top.addWidget(badge)
        outer.addLayout(top)
        outer.addStretch(1)

        hero = QFrame()
        hero.setObjectName("heroCard")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(42, 38, 42, 38)
        hero_layout.setSpacing(16)
        icon = QLabel("◈")
        icon.setObjectName("heroIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(icon)
        title = QLabel("Your digital life.\nOne secure vault.")
        title.setObjectName("heroTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(title)
        intro = QLabel(
            "A clean, local-first password manager built to keep your credentials private.\n"
            "No account required. Your master password never leaves this device."
        )
        intro.setObjectName("muted")
        intro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        intro.setWordWrap(True)
        hero_layout.addWidget(intro)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addStretch()
        create = QPushButton("Create a new vault  →")
        create.setObjectName("primary")
        create.setMinimumWidth(200)
        create.clicked.connect(self.create_vault)
        open_button = QPushButton("Open existing vault")
        open_button.setMinimumWidth(180)
        open_button.clicked.connect(self.open_existing)
        buttons.addWidget(create)
        buttons.addWidget(open_button)
        buttons.addStretch()
        hero_layout.addSpacing(6)
        hero_layout.addLayout(buttons)

        features = QHBoxLayout()
        features.setSpacing(12)
        for title_text, detail in (
            ("Strong encryption", "Encrypted at rest"),
            ("Local-first", "No mandatory cloud"),
            ("Backup control", "You choose where"),
        ):
            card = QFrame()
            card.setObjectName("featureCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 15, 16, 15)
            heading = QLabel(title_text)
            heading.setObjectName("featureTitle")
            description = QLabel(detail)
            description.setObjectName("muted")
            card_layout.addWidget(heading)
            card_layout.addWidget(description)
            features.addWidget(card)
        outer.addWidget(hero, 0, Qt.AlignmentFlag.AlignHCenter)
        hero.setMaximumWidth(820)
        outer.addSpacing(16)
        outer.addLayout(features)
        outer.addStretch(1)

        footer = QHBoxLayout()
        footer.addStretch()
        github = QPushButton("GitHub ↗")
        github.setObjectName("linkButton")
        github.clicked.connect(self._open_github)
        footer.addWidget(github)
        outer.addLayout(footer)
        return page

    def _build_app_page(self) -> QWidget:
        page = QWidget()
        shell = QHBoxLayout(page)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(238)
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(16, 22, 16, 16)
        side.setSpacing(7)
        brand = QLabel("◈  espass")
        brand.setObjectName("brand")
        side.addWidget(brand)
        subtitle = QLabel("PASSWORD WORKSPACE")
        subtitle.setObjectName("eyebrow")
        side.addWidget(subtitle)
        side.addSpacing(15)

        self.nav_buttons: dict[str, QPushButton] = {}
        for icon, name in NAV_ITEMS:
            button = QPushButton(f"{icon}    {name}")
            button.setObjectName("nav")
            button.setCheckable(True)
            button.setMinimumHeight(42)
            button.clicked.connect(lambda checked=False, target=name: self.navigate(target))
            self.nav_buttons[name] = button
            side.addWidget(button)
        side.addStretch(1)

        vault_badge = QFrame()
        vault_badge.setObjectName("vaultBadge")
        badge_layout = QVBoxLayout(vault_badge)
        badge_layout.setContentsMargins(12, 12, 12, 12)
        vault_title = QLabel("●  VAULT UNLOCKED")
        vault_title.setObjectName("successText")
        vault_title.setStyleSheet("font-size: 10px; font-weight: 700;")
        badge_layout.addWidget(vault_title)
        self.sidebar_vault_path = QLabel("Encrypted local storage")
        self.sidebar_vault_path.setObjectName("muted")
        self.sidebar_vault_path.setWordWrap(True)
        badge_layout.addWidget(self.sidebar_vault_path)
        side.addWidget(vault_badge)
        lock_button = QPushButton("⇥   Lock vault   ·   Ctrl+L")
        lock_button.setObjectName("lockButton")
        lock_button.clicked.connect(self.lock_vault)
        side.addWidget(lock_button)

        main = QWidget()
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(30, 24, 30, 22)
        main_layout.setSpacing(18)
        header = QHBoxLayout()
        titles = QVBoxLayout()
        self.page_title = QLabel("All Items")
        self.page_title.setObjectName("pageTitle")
        self.page_subtitle = QLabel("Everything you need, securely organized.")
        self.page_subtitle.setObjectName("muted")
        titles.addWidget(self.page_title)
        titles.addWidget(self.page_subtitle)
        header.addLayout(titles)
        header.addStretch()
        self.search = QLineEdit()
        self.search.setObjectName("searchBox")
        self.search.setPlaceholderText("⌕   Search credentials  ·  Ctrl+F")
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumWidth(245)
        self.search.setMaximumWidth(320)
        self.search.textChanged.connect(self.refresh_table)
        header.addWidget(self.search)
        self.add_button = QPushButton("＋  Add credential")
        self.add_button.setObjectName("primary")
        self.add_button.clicked.connect(self.new_credential)
        header.addWidget(self.add_button)
        main_layout.addLayout(header)

        self.content_stack = QStackedWidget()
        self.list_page = self._build_list_page()
        self.utility_page = QWidget()
        utility_outer = QVBoxLayout(self.utility_page)
        utility_outer.setContentsMargins(0, 0, 0, 0)
        self.utility_scroll = QScrollArea()
        self.utility_scroll.setWidgetResizable(True)
        self.utility_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.utility_content = QWidget()
        self.utility_layout = QVBoxLayout(self.utility_content)
        self.utility_layout.setContentsMargins(0, 0, 10, 8)
        self.utility_layout.setSpacing(16)
        self.utility_scroll.setWidget(self.utility_content)
        utility_outer.addWidget(self.utility_scroll)
        self.content_stack.addWidget(self.list_page)
        self.content_stack.addWidget(self.utility_page)
        main_layout.addWidget(self.content_stack, 1)
        shell.addWidget(self.sidebar)
        shell.addWidget(main, 1)
        return page

    def _build_list_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        stats = QHBoxLayout()
        stats.setSpacing(12)
        self.stat_total = self._stat_card("SAVED ITEMS", "0")
        self.stat_favorites = self._stat_card("FAVORITES", "0")
        self.stat_categories = self._stat_card("CATEGORIES", "0")
        stats.addWidget(self.stat_total[0])
        stats.addWidget(self.stat_favorites[0])
        stats.addWidget(self.stat_categories[0])
        layout.addLayout(stats)

        row = QHBoxLayout()
        self.list_summary = QLabel("Your credentials are encrypted in the local vault.")
        self.list_summary.setObjectName("muted")
        row.addWidget(self.list_summary)
        row.addStretch()
        self.category_filter = QComboBox()
        self.category_filter.setMinimumWidth(150)
        self.category_filter.currentTextChanged.connect(self.refresh_table)
        row.addWidget(self.category_filter)
        layout.addLayout(row)

        self.table = QTableWidget(0, 4)
        self.table.setObjectName("credentialsTable")
        self.table.setHorizontalHeaderLabels(["NAME", "USERNAME / EMAIL", "CATEGORY", "UPDATED"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.doubleClicked.connect(self.edit_selected)
        layout.addWidget(self.table, 1)

        actions = QHBoxLayout()
        for label, callback, object_name in (
            ("Open / Edit", self.edit_selected, ""),
            ("Copy username", lambda: self.copy_selected("username"), ""),
            ("Copy password", lambda: self.copy_selected("password"), ""),
            ("Toggle favorite", self.toggle_favorite, ""),
            ("Delete", self.delete_selected, "dangerButton"),
        ):
            button = QPushButton(label)
            if object_name:
                button.setObjectName(object_name)
            button.clicked.connect(callback)
            actions.addWidget(button)
        actions.addStretch()
        layout.addLayout(actions)
        return page

    def _stat_card(self, title: str, value: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setObjectName("statCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 13, 16, 13)
        heading = QLabel(title)
        heading.setObjectName("eyebrow")
        number = QLabel(value)
        number.setObjectName("statNumber")
        layout.addWidget(heading)
        layout.addWidget(number)
        return card, number

    def _apply_theme(self) -> None:
        theme = self.config.values.get("theme", "dark")
        if theme == "system":
            app = QApplication.instance()
            theme = "light" if app and app.palette().window().color().lightness() > 128 else "dark"
        app = QApplication.instance()
        if app:
            app.setStyleSheet(EXTRA_STYLE + (LIGHT if theme == "light" else DARK))

    def _show_start(self) -> None:
        self.root_stack.setCurrentWidget(self.start_page)
        self._idle_timer.stop()

    def _show_vault(self) -> None:
        if not self.vault or not self.vault.unlocked:
            return
        self.root_stack.setCurrentWidget(self.app_page)
        self.sidebar_vault_path.setText(self.vault.path.name)
        self._last_activity = time.monotonic()
        self._idle_timer.start()
        self.navigate("All Items")

    def _password_dialog(self, title: str, confirm: bool = False) -> tuple[str, str | None] | None:
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumWidth(430)
        layout = QVBoxLayout(dialog)
        heading = QLabel(title)
        heading.setObjectName("dialogTitle")
        layout.addWidget(heading)
        note = QLabel("Use a long, unique passphrase. espass cannot reset a forgotten master password.")
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        form = QFormLayout()
        password = QLineEdit()
        password.setEchoMode(QLineEdit.EchoMode.Password)
        password.setPlaceholderText("At least 12 characters")
        form.addRow("Master password", password)
        confirmation = None
        if confirm:
            confirmation = QLineEdit()
            confirmation.setEchoMode(QLineEdit.EchoMode.Password)
            confirmation.setPlaceholderText("Repeat master password")
            form.addRow("Confirm password", confirmation)
        layout.addLayout(form)
        reveal = QCheckBox("Show master password")
        reveal.toggled.connect(
            lambda visible: password.setEchoMode(
                QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
            )
        )
        layout.addWidget(reveal)
        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancel")
        proceed = QPushButton("Continue")
        proceed.setObjectName("primary")
        buttons.addWidget(cancel)
        buttons.addWidget(proceed)
        layout.addLayout(buttons)
        cancel.clicked.connect(dialog.reject)
        proceed.clicked.connect(dialog.accept)
        if confirmation is not None:
            password.returnPressed.connect(confirmation.setFocus)
            confirmation.returnPressed.connect(dialog.accept)
        else:
            password.returnPressed.connect(dialog.accept)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        return password.text(), confirmation.text() if confirmation else None

    def create_vault(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose where to save your encrypted vault",
            str(default_vault_path()),
            "espass vault (*.pyvault)",
        )
        if not path:
            return
        if Path(path).exists():
            QMessageBox.warning(self, "File already exists", "Choose a new filename. Existing files are never overwritten.")
            return
        if not path.lower().endswith(".pyvault"):
            path += ".pyvault"
        values = self._password_dialog("Create your master password", confirm=True)
        if not values:
            return
        try:
            vault = VaultService(path)
            vault.create(values[0], values[1])
            self.vault = vault
            self._show_vault()
        except Exception as exc:
            self._error(exc)

    def open_existing(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open an espass vault",
            str(default_vault_path().parent),
            "espass vault (*.pyvault);;All files (*)",
        )
        if not path:
            return
        values = self._password_dialog("Unlock your vault")
        if not values:
            return
        candidate = VaultService(path)
        try:
            candidate.unlock(values[0])
            self.vault = candidate
            self._show_vault()
        except Exception as exc:
            candidate.lock()
            self._error(exc)

    def navigate(self, name: str) -> None:
        if not self.vault or not self.vault.unlocked:
            return
        self.page = name
        for item, button in self.nav_buttons.items():
            button.setChecked(item == name)
        self.page_title.setText(name)
        subtitles = {
            "All Items": "Everything you need, securely organized.",
            "Favorites": "Your most important logins, close at hand.",
            "Recently Added": "The latest credentials added to your vault.",
            "Password Generator": "Create strong, unique passwords locally.",
            "Security Audit": "Review common password hygiene risks offline.",
            "Settings": "Personalize espass and manage secure backups.",
        }
        self.page_subtitle.setText(subtitles.get(name, "Your secure workspace."))
        if name in ("All Items", "Favorites", "Recently Added"):
            self.category_filter.setVisible(False)
            self.content_stack.setCurrentWidget(self.list_page)
            self.refresh_table()
        elif name == "Categories":
            self.category_filter.setVisible(True)
            self.content_stack.setCurrentWidget(self.list_page)
            self.refresh_table()
        elif name == "Password Generator":
            self._show_utility(self._generator_widget)
        elif name == "Security Audit":
            self._show_utility(self._audit_widget)
        elif name == "Settings":
            self._show_utility(self._settings_widget)

    def refresh_table(self, *_args) -> None:
        if not self.vault or not self.vault.unlocked:
            return
        try:
            all_items = self.vault.credentials()
            categories = self.vault.categories()
        except PyVaultError as exc:
            self._error(exc)
            return

        previous = self.category_filter.currentText()
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem("All categories")
        self.category_filter.addItems(categories)
        if previous and self.category_filter.findText(previous) >= 0:
            self.category_filter.setCurrentText(previous)
        self.category_filter.blockSignals(False)

        self.stat_total[1].setText(str(len(all_items)))
        self.stat_favorites[1].setText(str(sum(bool(item.get("favorite")) for item in all_items)))
        self.stat_categories[1].setText(str(len(categories)))

        items = list(all_items)
        query = self.search.text().casefold().strip()
        if self.page == "Favorites":
            items = [item for item in items if item.get("favorite")]
        elif self.page == "Recently Added":
            items = sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)[:20]
        elif self.page == "Categories":
            category = self.category_filter.currentText()
            if category and category != "All categories":
                items = [item for item in items if item.get("category") == category]
        if query:
            keys = ("title", "username", "url", "category", "notes", "tags")
            items = [
                item for item in items
                if query in " ".join(str(item.get(key, "")) for key in keys).casefold()
            ]
        if self.page != "Recently Added":
            items.sort(key=lambda item: str(item.get("title", "")).casefold())

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            values = (
                ("★  " if item.get("favorite") else "") + str(item.get("title", "Untitled")),
                str(item.get("username", "")),
                str(item.get("category", "Other")),
                str(item.get("updated_at", ""))[:10],
            )
            for column, value in enumerate(values):
                cell = QTableWidgetItem(value)
                cell.setData(Qt.ItemDataRole.UserRole, item.get("id"))
                self.table.setItem(row, column, cell)
        self.table.setSortingEnabled(True)
        self.list_summary.setText(
            f"{len(items)} shown  ·  {len(all_items)} saved  ·  Encrypted locally"
        )

    def selected_item(self) -> dict | None:
        row = self.table.currentRow()
        if row < 0 or not self.vault:
            return None
        cell = self.table.item(row, 0)
        if cell is None:
            return None
        return self.vault.get(str(cell.data(Qt.ItemDataRole.UserRole)))

    def new_credential(self) -> None:
        if not self.vault or not self.vault.unlocked:
            return
        dialog = CredentialDialog(self.vault.categories(), parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.vault.upsert(dialog.result_item())
                self.refresh_table()
                self.statusBar().showMessage("Credential saved securely.", 3000)
            except Exception as exc:
                self._error(exc)

    def edit_selected(self) -> None:
        item = self.selected_item()
        if not item or not self.vault:
            return
        dialog = CredentialDialog(self.vault.categories(), item, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.vault.upsert(dialog.result_item())
                self.refresh_table()
                self.statusBar().showMessage("Credential updated.", 3000)
            except Exception as exc:
                self._error(exc)

    def delete_selected(self) -> None:
        item = self.selected_item()
        if not item or not self.vault:
            return
        answer = QMessageBox.question(
            self,
            "Delete credential?",
            f"Permanently delete ‘{item.get('title', 'Untitled')}’ from this vault?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self.vault.delete(item["id"])
            self.refresh_table()
            self.statusBar().showMessage("Credential deleted.", 3000)
        except Exception as exc:
            self._error(exc)

    def toggle_favorite(self) -> None:
        item = self.selected_item()
        if not item or not self.vault:
            return
        item["favorite"] = not bool(item.get("favorite"))
        try:
            self.vault.upsert(item)
            self.refresh_table()
        except Exception as exc:
            self._error(exc)

    def copy_selected(self, field: str) -> None:
        item = self.selected_item()
        if not item:
            return
        value = str(item.get(field, ""))
        if not value:
            QMessageBox.information(self, "Nothing to copy", f"This item has no {field}.")
            return
        self._copy_value(value)
        self.statusBar().showMessage(
            f"{field.title()} copied. Clipboard clears in {self.config.values['clipboard_clear_seconds']} seconds.",
            4000,
        )

    def _copy_value(self, value: str) -> None:
        if not value:
            return
        QApplication.clipboard().setText(value)
        self._clipboard_token = value
        self._clipboard_timer.start(int(self.config.values["clipboard_clear_seconds"]) * 1000)

    def _clear_clipboard(self) -> None:
        clipboard = QApplication.clipboard()
        if self._clipboard_token is not None and clipboard.text() == self._clipboard_token:
            clipboard.clear()
        self._clipboard_token = None

    def _show_utility(self, builder) -> None:
        while self.utility_layout.count():
            item = self.utility_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        builder(self.utility_layout)
        self.content_stack.setCurrentWidget(self.utility_page)

    def _section_card(self, title: str, description: str = "") -> tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("sectionCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)
        heading = QLabel(title)
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)
        if description:
            note = QLabel(description)
            note.setObjectName("muted")
            note.setWordWrap(True)
            layout.addWidget(note)
        return card, layout

    def _generator_widget(self, layout: QVBoxLayout) -> None:
        card, form_layout = self._section_card(
            "Password generator",
            "Generated locally using Python's cryptographically secure random generator.",
        )
        options = QFormLayout()
        length = QSpinBox()
        length.setRange(12, 128)
        length.setValue(max(12, int(self.config.values.get("generator_length", 20))))
        uppercase = QCheckBox("Uppercase letters")
        uppercase.setChecked(True)
        lowercase = QCheckBox("Lowercase letters")
        lowercase.setChecked(True)
        digits = QCheckBox("Numbers")
        digits.setChecked(True)
        symbols = QCheckBox("Symbols")
        symbols.setChecked(True)
        ambiguous = QCheckBox("Exclude ambiguous characters")
        options.addRow("Password length", length)
        form_layout.addLayout(options)
        for checkbox in (uppercase, lowercase, digits, symbols, ambiguous):
            form_layout.addWidget(checkbox)
        result = QLineEdit()
        result.setReadOnly(True)
        result.setPlaceholderText("Your generated password appears here")
        result.setMinimumHeight(44)
        result.setEchoMode(QLineEdit.EchoMode.Password)
        reveal = QCheckBox("Show generated password")
        reveal.toggled.connect(
            lambda checked: result.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        strength = QLabel("Choose your options, then generate a password.")
        strength.setObjectName("muted")
        form_layout.addWidget(result)
        form_layout.addWidget(reveal)
        form_layout.addWidget(strength)

        actions = QHBoxLayout()
        generate = QPushButton("Generate password")
        generate.setObjectName("primary")
        copy = QPushButton("Copy password")
        actions.addWidget(generate)
        actions.addWidget(copy)
        actions.addStretch()
        form_layout.addLayout(actions)

        def do_generate() -> None:
            try:
                password = generate_password(
                    length.value(),
                    uppercase=uppercase.isChecked(),
                    lowercase=lowercase.isChecked(),
                    digits=digits.isChecked(),
                    symbols=symbols.isChecked(),
                    exclude_ambiguous=ambiguous.isChecked(),
                )
                result.setText(password)
                rating = estimate_strength(password)
                strength.setText(f"{rating['label']}  ·  {rating['suggestion']}")
            except ValueError as exc:
                QMessageBox.warning(self, "Generator options", str(exc))

        generate.clicked.connect(do_generate)
        copy.clicked.connect(lambda: self._copy_value(result.text()))
        layout.addWidget(card)
        layout.addStretch(1)

    def _audit_widget(self, layout: QVBoxLayout) -> None:
        if not self.vault:
            return
        items = self.vault.credentials()
        issues = audit_credentials(items)
        counts = {level: sum(issue["severity"] == level for issue in issues) for level in ("high", "medium", "low")}
        card, card_layout = self._section_card(
            "Security overview",
            "Offline heuristic checks only. Password values are never included in this report.",
        )
        stats = QLabel(
            f"{len(items)} credentials reviewed     ·     {counts['high']} high     ·     "
            f"{counts['medium']} medium     ·     {counts['low']} low"
        )
        stats.setObjectName("auditSummary")
        card_layout.addWidget(stats)
        table = QTableWidget(len(issues), 4)
        table.setHorizontalHeaderLabels(["SEVERITY", "ITEM", "OBSERVATION", "SUGGESTION"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        for row, issue in enumerate(issues):
            for col, key in enumerate(("severity", "title", "issue", "recommendation")):
                table.setItem(row, col, QTableWidgetItem(issue[key]))
        card_layout.addWidget(table)
        if not issues:
            ok = QLabel("✓  No issues detected by these basic checks.")
            ok.setObjectName("successText")
            card_layout.addWidget(ok)
        caveat = QLabel(
            "These checks can produce false positives. They do not check breach databases or prove a password is compromised."
        )
        caveat.setObjectName("muted")
        caveat.setWordWrap(True)
        card_layout.addWidget(caveat)
        layout.addWidget(card)

    def _settings_widget(self, layout: QVBoxLayout) -> None:
        appearance, appearance_layout = self._section_card("Appearance & privacy", "Preferences are saved locally on this device.")
        form = QFormLayout()
        theme = QComboBox()
        theme.addItems(["dark", "light", "system"])
        theme.setCurrentText(self.config.values["theme"])
        theme.currentTextChanged.connect(self._theme_changed)
        auto_lock = QComboBox()
        for minutes in (0, 1, 5, 10, 15, 30):
            auto_lock.addItem("Disabled" if minutes == 0 else f"{minutes} minutes", minutes)
        idx = auto_lock.findData(self.config.values["auto_lock_minutes"])
        auto_lock.setCurrentIndex(max(0, idx))
        auto_lock.currentIndexChanged.connect(lambda _: self._setting("auto_lock_minutes", auto_lock.currentData()))
        clipboard = QComboBox()
        for seconds in (15, 30, 60, 120, 300):
            clipboard.addItem(f"{seconds} seconds", seconds)
        clipboard.setCurrentIndex(max(0, clipboard.findData(self.config.values["clipboard_clear_seconds"])))
        clipboard.currentIndexChanged.connect(lambda _: self._setting("clipboard_clear_seconds", clipboard.currentData()))
        form.addRow("Theme", theme)
        form.addRow("Automatic lock", auto_lock)
        form.addRow("Clear copied secrets after", clipboard)
        appearance_layout.addLayout(form)
        manage_categories = QPushButton("Manage categories")
        manage_categories.clicked.connect(self.manage_categories)
        appearance_layout.addWidget(manage_categories, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(appearance)

        backups, backup_layout = self._section_card(
            "Encrypted backups",
            "Backups contain the encrypted vault file, not readable passwords. Keep the master password private and test recovery before relying on a backup.",
        )
        backup_actions = QHBoxLayout()
        create_backup = QPushButton("Create local backup")
        create_backup.clicked.connect(self.create_backup)
        restore_backup = QPushButton("Restore backup")
        restore_backup.clicked.connect(self.restore_backup)
        backup_actions.addWidget(create_backup)
        backup_actions.addWidget(restore_backup)
        backup_actions.addStretch()
        backup_layout.addLayout(backup_actions)
        layout.addWidget(backups)

        telegram, telegram_layout = self._section_card(
            "Telegram backup",
            "Optional. Sends a copy of your encrypted vault only after confirmation. Telegram stores the file; it cannot read the vault without your master password. Never share your bot token.",
        )
        telegram_form = QFormLayout()
        self.telegram_recipient = QLineEdit(str(self.config.values.get("telegram_recipient", "")))
        self.telegram_recipient.setPlaceholderText("@your_username or numeric chat ID")
        self.telegram_recipient.textChanged.connect(lambda value: self._setting("telegram_recipient", value.strip()))
        self.telegram_token = QLineEdit()
        self.telegram_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.telegram_token.setPlaceholderText("Bot token from @BotFather (kept only for this session)")
        telegram_form.addRow("Recipient username / ID", self.telegram_recipient)
        telegram_form.addRow("Bot token", self.telegram_token)
        telegram_layout.addLayout(telegram_form)
        hint = QLabel(
            "For a personal username, first open your bot in Telegram and press Start. "
            "If espass cannot find the username in the bot's recent updates, use the numeric chat ID. "
            "Usernames work directly only for public groups/channels; Telegram bots cannot message a private user by username alone."
        )
        hint.setObjectName("muted")
        hint.setWordWrap(True)
        telegram_layout.addWidget(hint)
        send = QPushButton("Send encrypted backup to Telegram")
        send.setObjectName("primary")
        send.clicked.connect(self.send_telegram_backup)
        telegram_layout.addWidget(send)
        self.telegram_auto_backup = QCheckBox("Automatically send an encrypted backup whenever espass closes")
        self.telegram_auto_backup.setChecked(bool(self.config.values.get("telegram_auto_backup", False)))
        self.telegram_auto_backup.toggled.connect(self._toggle_telegram_auto_backup)
        telegram_layout.addWidget(self.telegram_auto_backup)
        auto_hint = QLabel(
            "Off by default. When enabled, espass uploads the encrypted vault on each normal close while the vault is unlocked "
            "without asking again. The bot token is stored in the operating-system credential manager. "
            "Only enable this for a Telegram destination you control; turn it off any time."
        )
        auto_hint.setObjectName("muted")
        auto_hint.setWordWrap(True)
        telegram_layout.addWidget(auto_hint)
        layout.addWidget(telegram)

        about, about_layout = self._section_card("About espass")
        about_text = QLabel(
            "espass · Local-first password manager\n"
            "Not independently security-audited. Maintain an offline backup of your vault."
        )
        about_text.setObjectName("muted")
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)
        github = QPushButton("Open GitHub profile  ↗")
        github.clicked.connect(self._open_github)
        about_layout.addWidget(github, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(about)
        layout.addStretch(1)

    def _theme_changed(self, value: str) -> None:
        self.config.values["theme"] = value
        self.config.save()
        self._apply_theme()

    def _setting(self, key: str, value) -> None:
        self.config.values[key] = value
        self.config.save()

    def manage_categories(self) -> None:
        if not self.vault:
            return
        from PySide6.QtWidgets import QInputDialog

        current = "\n".join(self.vault.categories())
        text, accepted = QInputDialog.getMultiLineText(
            self,
            "Manage categories",
            "Enter one category per line. Removed categories will be reassigned.",
            current,
        )
        if accepted:
            try:
                self.vault.set_categories(text.splitlines())
                self.refresh_table()
            except Exception as exc:
                self._error(exc)

    def send_telegram_backup(self) -> None:
        if not self.vault or not self.vault.unlocked:
            QMessageBox.information(self, "Vault locked", "Unlock your vault before sending a backup.")
            return
        token = self.telegram_token.text().strip()
        recipient = self.telegram_recipient.text().strip()
        if not token:
            from pyvault.services.telegram_credentials import get_bot_token
            token = get_bot_token() or ""
        if not token or not recipient:
            QMessageBox.warning(self, "Telegram backup", "Enter a bot token and a username or numeric chat ID.")
            return
        answer = QMessageBox.warning(
            self,
            "Confirm encrypted backup",
            f"Send a COPY of your encrypted vault to {recipient}?\n\n"
            "The recipient will receive the encrypted file. The master password is still required to open it. "
            "Telegram will store the uploaded file. Continue only if you control this destination.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            TelegramBackupService().send_encrypted_backup(self.vault, token, recipient)
            self.telegram_token.clear()
            QMessageBox.information(self, "Backup sent", "The encrypted backup was sent successfully.")
        except Exception as exc:
            self._error(exc)

    def _toggle_telegram_auto_backup(self, enabled: bool) -> None:
        from pyvault.services.telegram_credentials import store_bot_token

        if not enabled:
            self.config.values["telegram_auto_backup"] = False
            self.config.save()
            return

        token = self.telegram_token.text().strip()
        if not token:
            from pyvault.services.telegram_credentials import get_bot_token
            token = get_bot_token() or ""
        recipient = self.telegram_recipient.text().strip()
        if not token or not recipient:
            self.telegram_auto_backup.blockSignals(True)
            self.telegram_auto_backup.setChecked(False)
            self.telegram_auto_backup.blockSignals(False)
            QMessageBox.warning(
                self, "Automatic Telegram backup",
                "Enter the bot token and your Telegram username or numeric chat ID first."
            )
            return

        answer = QMessageBox.warning(
            self,
            "Enable automatic encrypted backups?",
            "After you enable this, every normal app close while the vault is unlocked will automatically upload a copy of the "
            f"encrypted vault to {recipient}. The master password is not sent, but the file will be stored "
            "by Telegram. Only continue if you control this destination.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.telegram_auto_backup.blockSignals(True)
            self.telegram_auto_backup.setChecked(False)
            self.telegram_auto_backup.blockSignals(False)
            return
        try:
            store_bot_token(token)
            self.config.values["telegram_recipient"] = recipient
            self.config.values["telegram_auto_backup"] = True
            self.config.save()
            self.telegram_token.clear()
            QMessageBox.information(
                self, "Automatic backup enabled",
                "The bot token was stored in the operating-system credential manager. "
                "An encrypted vault copy will be sent on each normal close."
            )
        except Exception as exc:
            self.telegram_auto_backup.blockSignals(True)
            self.telegram_auto_backup.setChecked(False)
            self.telegram_auto_backup.blockSignals(False)
            self.config.values["telegram_auto_backup"] = False
            self.config.save()
            self._error(exc)

    def create_backup(self) -> None:
        if not self.vault:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save encrypted backup", str(Path.home() / "espass-backup.pyvault"), "espass backup (*.pyvault)"
        )
        if not path:
            return
        if not path.lower().endswith(".pyvault"):
            path += ".pyvault"
        try:
            BackupService().create(self.vault, path)
            QMessageBox.information(self, "Backup created", "Encrypted backup saved successfully.")
        except Exception as exc:
            self._error(exc)

    def restore_backup(self) -> None:
        if not self.vault:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Select encrypted backup", str(Path.home()), "espass backup (*.pyvault);;All files (*)"
        )
        if not path:
            return
        values = self._password_dialog("Verify backup master password")
        if not values:
            return
        answer = QMessageBox.question(
            self,
            "Replace current vault?",
            "The current vault will be replaced by the verified backup. Make sure you have a separate copy of the current vault first.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self.vault.replace_from_backup(path, values[0])
            self.refresh_table()
            QMessageBox.information(self, "Restore complete", "The backup was verified and restored.")
        except Exception as exc:
            self._error(exc)

    def show_generator(self) -> None:
        if self.vault and self.vault.unlocked:
            self.navigate("Password Generator")

    def show_settings(self) -> None:
        self.navigate("Settings")

    def focus_search(self) -> None:
        if self.root_stack.currentWidget() == self.app_page:
            self.search.setFocus()
            self.search.selectAll()

    def lock_vault(self) -> None:
        if not self.vault:
            self._show_start()
            return
        self._idle_timer.stop()
        self._clipboard_timer.stop()
        self._clear_clipboard()
        for dialog in self.findChildren(QDialog):
            dialog.close()
        self.vault.lock()
        self.vault = None
        self.table.setRowCount(0)
        self._show_start()
        self.statusBar().showMessage("Vault locked.", 3000)

    def _check_idle(self) -> None:
        timeout = int(self.config.values.get("auto_lock_minutes", 5))
        if timeout and time.monotonic() - self._last_activity >= timeout * 60:
            self.lock_vault()
            QMessageBox.information(self, "Vault locked", "espass locked after inactivity.")

    def eventFilter(self, obj, event) -> bool:
        if event.type() in (
            QEvent.Type.MouseMove,
            QEvent.Type.MouseButtonPress,
            QEvent.Type.KeyPress,
            QEvent.Type.Wheel,
        ):
            self._last_activity = time.monotonic()
        return super().eventFilter(obj, event)

    def _open_github(self) -> None:
        QDesktopServices.openUrl(QUrl(GITHUB_URL))

    def _error(self, exc: Exception) -> None:
        message = str(exc) if isinstance(exc, PyVaultError) else (
            "The operation failed. Check the vault file, network connection, and application permissions."
        )
        QMessageBox.warning(self, "espass", message)

    def closeEvent(self, event) -> None:
        # Auto-upload is strictly opt-in and sends only the encrypted vault file.
        if (
            self.config.values.get("telegram_auto_backup", False)
            and self.vault is not None
            and self.vault.unlocked
        ):
            from pyvault.services.telegram_credentials import get_bot_token

            token = get_bot_token()
            recipient = str(self.config.values.get("telegram_recipient", "")).strip()
            try:
                if not token or not recipient:
                    raise PyVaultError("Automatic backup is enabled, but its token or destination is missing.")
                TelegramBackupService().send_encrypted_backup(self.vault, token, recipient)
            except Exception as exc:
                answer = QMessageBox.warning(
                    self,
                    "Automatic backup failed",
                    f"espass could not send the encrypted backup.\n\n{exc}\n\nClose anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    event.ignore()
                    return

        self.config.values["window_width"] = self.width()
        self.config.values["window_height"] = self.height()
        self.config.save()
        if self.vault:
            self.vault.lock()
        self._clipboard_timer.stop()
        self._idle_timer.stop()
        self._clear_clipboard()
        app = QApplication.instance()
        if app:
            app.removeEventFilter(self)
        event.accept()


EXTRA_STYLE = """
QWidget { font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; }
QLabel#brand { font-size: 25px; font-weight: 800; padding: 5px 2px; }
QLabel#eyebrow { font-size: 10px; font-weight: 700; letter-spacing: 1.2px; padding: 4px 2px; }
QLabel#heroTitle { font-size: 37px; font-weight: 800; padding: 4px; }
QLabel#heroIcon { font-size: 54px; padding: 0; }
QLabel#pill { border-radius: 12px; padding: 8px 12px; font-size: 10px; font-weight: 700; }
QFrame#heroCard { border-radius: 24px; }
QFrame#featureCard, QFrame#statCard, QFrame#sectionCard { border-radius: 15px; }
QLabel#featureTitle { font-weight: 700; font-size: 14px; }
QFrame#sidebar { border-right: 1px solid; }
QFrame#vaultBadge { border-radius: 11px; }
QLabel#pageTitle { font-size: 29px; font-weight: 800; }
QLabel#sectionTitle { font-size: 19px; font-weight: 750; }
QLabel#statNumber { font-size: 25px; font-weight: 800; padding-top: 3px; }
QLabel#dialogTitle { font-size: 21px; font-weight: 750; }
QLabel#auditSummary { font-size: 16px; font-weight: 700; padding: 12px 0; }
QPushButton { border-radius: 9px; padding: 10px 14px; }
QPushButton#nav { padding: 12px 13px; }
QPushButton#linkButton { padding: 8px 10px; }
QLineEdit#searchBox { padding: 12px 14px; }
QTableWidget { border-radius: 13px; padding: 5px; }
QHeaderView::section { padding: 12px 9px; font-size: 10px; font-weight: 750; }
QTableWidget::item { padding-left: 8px; }
QScrollArea { border: 0; }
QScrollBar:vertical { width: 9px; margin: 2px; }
QScrollBar::handle:vertical { border-radius: 4px; min-height: 25px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QCheckBox { spacing: 8px; }
"""

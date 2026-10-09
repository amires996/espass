from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from pyvault.core.models import Credential, utc_now
from pyvault.services.password_generator import estimate_strength, generate_password


class CredentialDialog(QDialog):
    """Accessible credential editor with password visibility and local generation."""

    def __init__(self, categories: list[str], item: dict | None = None, parent=None):
        super().__init__(parent)
        self.item = dict(item or {})
        self.setWindowTitle("Edit credential" if item else "Add credential")
        self.setMinimumWidth(540)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(25, 24, 25, 22)
        root.setSpacing(15)
        heading = QLabel("Credential details")
        heading.setObjectName("dialogTitle")
        root.addWidget(heading)
        subtitle = QLabel("Store the details you need. All fields are encrypted in your vault.")
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        form = QFormLayout()
        form.setHorizontalSpacing(15)
        form.setVerticalSpacing(13)
        self.title = QLineEdit(str(self.item.get("title", "")))
        self.title.setPlaceholderText("e.g. Personal email")
        self.username = QLineEdit(str(self.item.get("username", "")))
        self.username.setPlaceholderText("Username or email address")
        self.password = QLineEdit(str(self.item.get("password", "")))
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Enter or generate a strong password")
        self.password.setMinimumHeight(40)
        self.url = QLineEdit(str(self.item.get("url", "")))
        self.url.setPlaceholderText("https://example.com (optional)")
        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.addItems(categories or ["Personal", "Work", "Other"])
        self.category.setCurrentText(str(self.item.get("category", "Personal")))
        self.tags = QLineEdit(", ".join(self.item.get("tags", [])))
        self.tags.setPlaceholderText("email, important, work")
        self.notes = QTextEdit(str(self.item.get("notes", "")))
        self.notes.setPlaceholderText("Optional notes…")
        self.notes.setMinimumHeight(86)
        self.notes.setMaximumHeight(125)
        self.favorite = QCheckBox("Keep this item in Favorites")
        self.favorite.setChecked(bool(self.item.get("favorite", False)))

        password_row = QHBoxLayout()
        password_row.setSpacing(8)
        password_row.addWidget(self.password, 1)
        generate = QPushButton("Generate")
        generate.clicked.connect(self._generate)
        password_row.addWidget(generate)
        reveal = QCheckBox("Show")
        reveal.toggled.connect(
            lambda visible: self.password.setEchoMode(
                QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
            )
        )
        password_row.addWidget(reveal)
        password_widget = QWidget()
        password_widget.setLayout(password_row)

        self.strength = QLabel("Password strength will appear here.")
        self.strength.setObjectName("muted")
        self.password.textChanged.connect(self._update_strength)

        form.addRow("Title *", self.title)
        form.addRow("Username", self.username)
        form.addRow("Password", password_widget)
        form.addRow("", self.strength)
        form.addRow("Website", self.url)
        form.addRow("Category", self.category)
        form.addRow("Tags", self.tags)
        form.addRow("Notes", self.notes)
        root.addLayout(form)
        root.addWidget(self.favorite)

        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Cancel")
        save = QPushButton("Save credential")
        save.setObjectName("primary")
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self._validate_accept)
        actions.addWidget(cancel)
        actions.addWidget(save)
        root.addLayout(actions)
        self.title.setFocus()
        self._update_strength(self.password.text())

    def _generate(self) -> None:
        self.password.setText(generate_password(24))
        self.password.setEchoMode(QLineEdit.EchoMode.Normal)

    def _update_strength(self, value: str) -> None:
        rating = estimate_strength(value)
        self.strength.setText(f"Strength: {rating['label']}  ·  {rating['suggestion']}")

    def _validate_accept(self) -> None:
        if not self.title.text().strip():
            QMessageBox.warning(self, "Title required", "Enter a title for this credential.")
            self.title.setFocus()
            return
        url = self.url.text().strip()
        if url and not (url.startswith("https://") or url.startswith("http://")):
            QMessageBox.warning(self, "Check website", "Website URLs must start with http:// or https://.")
            self.url.setFocus()
            return
        self.accept()

    def result_item(self) -> dict:
        base = dict(self.item)
        base.update(
            title=self.title.text().strip(),
            username=self.username.text().strip(),
            password=self.password.text(),
            url=self.url.text().strip(),
            category=self.category.currentText().strip() or "Other",
            tags=[tag.strip() for tag in self.tags.text().split(",") if tag.strip()],
            notes=self.notes.toPlainText(),
            favorite=self.favorite.isChecked(),
            updated_at=utc_now(),
        )
        if not base.get("id"):
            base["id"] = Credential(title=base["title"]).id
        return base

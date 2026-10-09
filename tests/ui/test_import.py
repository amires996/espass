def test_ui_module_imports_when_qt_is_installed():
    import pytest
    pytest.importorskip("PySide6")
    from pyvault.ui.main_window import MainWindow
    assert MainWindow is not None

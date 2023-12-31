import sys
from typing import Dict, Optional
from dataclasses import dataclass

from PySide2.QtGui import QKeyEvent, QStandardItem
from PySide2.QtCore import (Qt, Slot, QRect, QEvent, QObject, QModelIndex,
                            QCoreApplication, QStringListModel,
                            QSortFilterProxyModel)
from PySide2.QtWidgets import (QLabel, QDialog, QLineEdit, QListView,
                               QSplitter, QSizePolicy, QVBoxLayout,
                               QApplication, QPlainTextEdit, QDialogButtonBox,
                               QStyledItemDelegate)

from .settings import Settings
from .registers import Registers

# TODO: Test this module
# TODO: Implement elided text delegate
# TODO: Add delete, copy and clear buttons
# TODO: Add alt+j and alt+k to navigate the list view


@dataclass
class PreviewData:
    text: str
    value: str


RegisterItem = Dict[str, PreviewData]


class PreviewListModel(QStringListModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.register_data: RegisterItem = {}

    def flags(self, index: QModelIndex):
        flag = Qt.ItemIsSelectable | ~Qt.ItemIsEditable
        return Qt.ItemFlags(flag)

    def populate(self, items: RegisterItem):
        self.setStringList(list(items.keys()))
        self.register_data = items


class ElidedTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        text = index.model().data(index, Qt.DisplayRole)
        if text:
            painter.save()
            rect = QRect(option.rect)
            if len(text) > 40:
                text = f'{text[:40]}...'
            painter.drawText(rect, Qt.TextElideMode.ElideRight, text)
            painter.restore()
        else:
            super().paint(painter, option, index)


class PreviewListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._model = PreviewListModel()

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self._model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(0)
        self.setModel(self.proxy_model)

        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListView.SingleSelection)
        self.setSpacing(5)

    def get_item_data(self, index: QModelIndex) -> Optional[PreviewData]:
        key = index.data(Qt.DisplayRole)
        return self._model.register_data.get(key)


class PreviewView(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)

        self.previewer_name = QLabel()
        self.previewer_name.setAlignment(Qt.AlignCenter)
        self.previewer_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.text_preview = QPlainTextEdit()
        self.text_preview.setReadOnly(True)

        self.list_view = PreviewListView()

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.list_view)
        splitter.addWidget(self.text_preview)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.search_bar = QLineEdit()
        self.search_bar.setMaxLength(1)
        self.search_bar.setPlaceholderText('Filter')
        self.search_bar.setFocus()
        self.search_bar.setClearButtonEnabled(True)

        layout = QVBoxLayout()
        layout.addWidget(self.previewer_name)
        layout.addWidget(self.search_bar)
        layout.addWidget(splitter)
        layout.addWidget(buttons)
        self.setLayout(layout)

        self.installEventFilter(self)
        self.list_view.installEventFilter(self)
        self.search_bar.installEventFilter(self)

        self.text_value = ''

    def _press_enter_event(self):

        # BUG: This gets called twice when pressing enter on the search bar and
        # once when pressing enter on the list view.

        index = self.list_view.currentIndex()
        data = self.list_view.get_item_data(index)

        if not data:
            self.reject()
            return False

        # TODO: Refactor this. The search bar value plays a role when no item
        # is found. Keep it simple.

        self.search_bar.clear()
        self.text_value = data.value
        self.accept()
        return True

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.KeyPress:
            if event.key() in [Qt.Key_Enter, Qt.Key_Return]:
                return self._press_enter_event()

            if event.key() in [Qt.Key_Up, Qt.Key_Down]:
                self.list_view.setFocus()
                return super().eventFilter(watched, event)

            if event.text().isprintable():
                self.search_bar.setFocus()
                self.search_bar.setText(self.search_bar.text() + event.text())
                return True

        return super().eventFilter(watched, event)


class PreviewController:
    def __init__(self, view: PreviewView):

        self.view = view
        self.list_view = view.list_view
        self.list_model = view.list_view._model

        self.view.search_bar.textChanged.connect(self._on_filter_changed)
        self.view.list_view.clicked.connect(self._on_item_clicked)

        selection_model = self.list_view.selectionModel()
        selection_model.currentChanged.connect(self._on_item_clicked)

    @Slot(str)
    def _on_filter_changed(self, text: str):
        if not text:
            self.view.text_preview.setPlainText('')

        self.list_view.proxy_model.setFilterFixedString(text)

        row_count = self.list_view.model().rowCount()
        if row_count > 0:
            first_index = self.list_view.model().index(0, 0)
            self.list_view.setCurrentIndex(first_index)
            self._on_item_clicked(first_index)

        if (
            (row_count == 1 or not row_count) and
            Settings.previewer_auto_insert
        ):
            enter_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.NoModifier)
            QCoreApplication.sendEvent(self.view, enter_event)

    @Slot(QStandardItem)
    def _on_item_clicked(self, index: QModelIndex):
        data = self.list_view.get_item_data(index)
        if not data:
            return
        self.view.text_preview.setPlainText(data.text)

    def init(self, name: str, items: RegisterItem):
        self.view.search_bar.clear()
        self.view.previewer_name.setText(f'<h2>{name}</h2>')
        self.list_model.populate(items)


class PreviewRegister:
    def __init__(self, name: str):
        self.name = name
        self.view = PreviewView()
        self.controller = PreviewController(self.view)
        self.controller.init(name, self.prepare_items())

    def get_text_value(self) -> Optional[str]:
        self.controller.init(self.name, self.prepare_items())
        return self.view.text_value if self.view.exec_() else None

    def prepare_items(self) -> RegisterItem:
        raise NotImplementedError


class PreviewNamedRegister(PreviewRegister):
    def __init__(self):
        super().__init__('named')

    def get_text_value(self) -> Optional[str]:
        """Get the value of the selected named register.

        A named register allows assigning a value or returning the key for assignment.

        """
        return super().get_text_value() or self.view.search_bar.text()

    def prepare_items(self) -> RegisterItem:
        return {
            k: PreviewData(v, k)
            for k, v in Registers.get_named_register().items()
            if v
        }


class PreviewMarkRegister(PreviewRegister):
    def __init__(self):
        super().__init__('marks')

    def prepare_items(self) -> RegisterItem:
        return {
            k: PreviewData(f'pos:{v["position"]} line:{v["line"]}', str(v['position']))
            for k, v in Registers.get_marks().items()
            if v
        }


class PreviewNumberedRegister(PreviewRegister):
    def __init__(self):
        super().__init__('clipboard')
        self.view.search_bar.setMaxLength(-1)

    def prepare_items(self) -> RegisterItem:
        return {
            v.strip(): PreviewData(v.strip(), v)
            for v in Registers.get_clipboard()
        }


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PreviewRegister('clipboard')
    window.view.show()

    app.exec_()

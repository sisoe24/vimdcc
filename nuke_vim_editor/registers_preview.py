import sys
import json
from typing import Any, Dict

from PySide2.QtGui import QPalette, QKeyEvent, QStandardItem
from PySide2.QtCore import (Qt, Slot, QRect, QEvent, Signal, QObject,
                            QModelIndex, QStringListModel,
                            QSortFilterProxyModel)
from PySide2.QtWidgets import (QLabel, QStyle, QWidget, QLineEdit, QListView,
                               QSplitter, QHBoxLayout, QListWidget,
                               QPushButton, QSizePolicy, QToolButton,
                               QVBoxLayout, QApplication, QPlainTextEdit,
                               QListWidgetItem, QStyledItemDelegate)


def trim_text(text: str, max_length: int = 40):
    if len(text) > max_length:
        return f'{text[:max_length // 2]}...{text[-max_length // 2:]}'
    return text


Items = Dict[str, str]


class PreviewListModel(QStringListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_data = {}

    def flags(self, index: QModelIndex):
        flag = Qt.ItemIsSelectable | ~Qt.ItemIsEditable
        return Qt.ItemFlags(flag)

    def get_register_items(self, name: str) -> Items:
        with open('registers.json') as f:
            data = json.load(f)

        if name == 'numbered':
            return {v.strip(): v for v in data['numbered']}

        return data.get(name, {})

    def populate(self, items: Items):
        self.setStringList(list(items.keys()))
        self.user_data = items


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

        # TODO: Implement this delegate
        # delegate = ElidedTextDelegate()
        # self.setItemDelegate(delegate)

        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListView.SingleSelection)
        self.setSpacing(5)

    def get_item_data(self, index: QModelIndex):
        key = index.data(Qt.DisplayRole)
        return self._model.user_data.get(key)


class PreviewView(QWidget):
    on_enter = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.previewer_name = QLabel()
        self.previewer_name.setAlignment(Qt.AlignCenter)
        self.previewer_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.text_preview = QPlainTextEdit()
        self.text_preview.setReadOnly(True)

        self.list_view = PreviewListView()

        # TODO: Implement these buttons
        self.delete_btn = QToolButton()
        self.delete_btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))

        self.copy_btn = QToolButton()
        self.copy_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))

        self.clear_btn = QToolButton()
        self.clear_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addWidget(self.copy_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()

        splitter = QSplitter()
        splitter.addWidget(self.list_view)
        splitter.addWidget(self.text_preview)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('Filter')
        self.search_bar.setFocus()
        self.search_bar.setClearButtonEnabled(True)

        layout = QVBoxLayout()
        layout.addWidget(self.previewer_name)
        layout.addWidget(self.search_bar)
        layout.addWidget(splitter)
        # layout.addLayout(buttons_layout)
        self.setLayout(layout)

        self.installEventFilter(self)
        self.list_view.installEventFilter(self)
        self.search_bar.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.KeyPress:

            if event.key() in [Qt.Key_Enter, Qt.Key_Return]:
                index = self.list_view.currentIndex()
                self.on_enter.emit(self.list_view.get_item_data(index))
                return True

            # TODO: Handle also alt+j and alt+k

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

        if self.list_view.model().rowCount() > 0:
            first_index = self.list_view.model().index(0, 0)
            self.list_view.setCurrentIndex(first_index)
            self._on_item_clicked(first_index)

    @Slot(QStandardItem)
    def _on_item_clicked(self, index: QModelIndex):
        data = self.list_view.get_item_data(index)
        self.view.text_preview.setPlainText(data or '')

    def init(self, name: str):
        self.view.previewer_name.setText(f'<h2>{name}</h2>')
        self.list_model.populate(self.list_model.get_register_items(name))


class PreviewRegister:
    def __init__(self, name: str, parent=None):

        self.view = PreviewView()
        self.controller = PreviewController(self.view)
        self.controller.init(name)

        self.view.on_enter.connect(self.on_enter)

    def on_enter(self, text: str):
        print('----')
        print('on_enter', text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PreviewRegister('marks')
    window.view.show()

    app.exec_()

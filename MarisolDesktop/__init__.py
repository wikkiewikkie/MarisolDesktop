import sys
from PySide.QtCore import *
from PySide.QtGui import *

from collections import OrderedDict


class Application(QApplication):

    def __init__(self, args):
        super().__init__(args)
        self.window = MainWindow()
        self.window.show()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MarisolDesktop")

        self.menu_bar = QMenuBar()

        self.menus = OrderedDict()

        self.menus['File'] = self.menu_bar.addMenu("&File")
        action = self.menus['File'].addAction("Add Documents...")
        action.triggered.connect(self.add_documents)

        self.menus['Help'] = self.menu_bar.addMenu("&Help")

        self.setMenuWidget(self.menu_bar)

        self.list = DocumentList()
        self.dock = QDockWidget("File List", self)
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.dock.setWidget(self.list)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)

        self.add_documents_dialog = FileSelector(self, "Add Documents")

    def add_documents(self):
        """Opens the add file dialog."""
        self.add_documents_dialog.show()


class FileSelector(QFileDialog):
    def __init__(self, parent, title):
        super().__init__(parent, title)

        self.parent = parent

        self.setFileMode(QFileDialog.ExistingFiles)
        self.setNameFilter("PDF Files (*.pdf)")

        self.filesSelected.connect(self.handle)

    def handle(self, files):
        """Event handler for file selection."""
        for file in files:
            self.parent.list.add_document(file)


class DocumentList(QListWidget):

    def __init__(self):
        super().__init__()

        self.documents = []

    def add_document(self, name):
        """Add a document to the list."""
        widget = QListWidgetItem(name, self)
        self.documents.append(widget)


if __name__ == "__main__":
    app = Application(sys.argv)
    sys.exit(app.exec_())

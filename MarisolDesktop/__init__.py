import base64
import os
import PyPDF2
import sys
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

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
        self.setContentsMargins(0, 0, 0, 0)

        self.numbering_config = {"prefix": "ABC",
                                 "start": 1,
                                 "fill": 6,
                                 "position": "Bottom Left"}

        self.menu_bar = QMenuBar()

        self.documents = QStandardItemModel()

        self.documents.setHorizontalHeaderLabels(["File Name", "Folder", "Pages"])
        self.menus = OrderedDict()

        self.menus['File'] = self.menu_bar.addMenu("&File")
        self.menus['Help'] = self.menu_bar.addMenu("&Help")

        add_documents_action = self.menus['File'].addAction("Add Documents...")
        add_documents_action.triggered.connect(self.add_documents)

        self.menus['File'].addSeparator()

        exit_action = self.menus['File'].addAction("E&xit")
        exit_action.triggered.connect(exit)

        self.setMenuWidget(self.menu_bar)

        self.list = DocumentList(self)

        self.viewer = Viewer()
        self.setCentralWidget(self.viewer)

        self.documents_dock = QDockWidget("Documents", self)
        self.documents_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.documents_dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.documents_dock.setWidget(self.list)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.documents_dock)

        self.numbering_dock = QDockWidget("Numbering", self)
        self.numbering_dock.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        self.numbering_dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.numbering_form = NumberingForm(self.numbering_dock)
        self.numbering_dock.setWidget(self.numbering_form)
        self.addDockWidget(Qt.TopDockWidgetArea, self.numbering_dock)

        self.add_documents_dialog = FileSelector(self, "Add Documents")

    def add_documents(self):
        """Opens the add file dialog."""
        self.add_documents_dialog.show()


class Viewer(QWebEngineView):

    def __init__(self):
        """Viewer capable of displaying a PDF file."""
        super().__init__()
        self.data = None

        self.setContentsMargins(0, 0, 0, 0)
        self.setDisabled(True)

    def handle_load_finished(self, status):
        """
        Handler for loadFinished signal. Calls render_file is page loaded ok.

        Args:
            status (bool):

        Returns:
            bool
        """
        if status:
            self.render_file()
        return status

    def load_file(self, path):
        """
        Loads data from a PDF file into variable and then renders.

        Args:
            path (Str):  Full path to the PDF file.

        Returns:
            bool: True on success, false on failure.

        """
        with open(path, "rb") as pdf_file:
            self.data = pdf_file.read()
        return self.render_file()

    def render_file(self):
        """
        Draw the PDF from cached data.

        Returns:
            bool
        """
        if self.data is not None:

            if not self.isEnabled():  # initialize if not initialized
                self.setDisabled(False)
                self.setUrl(QUrl("file:///view.html"))
                self.loadFinished.connect(self.render_file) # wait for page to load, and then call again

            else:
                # encode as base 64 and then convert to UTF-8
                self.data = base64.b64encode(self.data)
                self.data = self.data.decode('utf-8')
                script = "qpdf_ShowPdfFile('{}')".format(self.data)
                self.page().runJavaScript(script)

                self.data = None  # get rid of cached data

            return True

        return False


class NumberingForm(QWidget):

    def __init__(self, parent):
        """
        The numbering form.

        Args:
            parent (QDockWidget): parent widget
        """
        super().__init__(parent)

        self.parent = parent
        self.config = parent.parentWidget().numbering_config

        self.layout = QFormLayout(self)
        self.setLayout(self.layout)

        # set up inputs
        self.fill_edit = QSpinBox(self)
        self.fill_edit.setValue(self.config['fill'])
        self.prefix_edit = QLineEdit(self.config['prefix'], self)
        self.position_edit = QComboBox(self)
        self.position_edit.addItems(["Bottom Left", "Bottom Right", "Top Left", "Top Right"])
        self.start_edit = QSpinBox(self)
        self.start_edit.setValue(self.config['start'])

        # add inputs to layout
        self.layout.addRow("&Prefix:", self.prefix_edit)
        self.layout.addRow("&Start:", self.start_edit)
        self.layout.addRow("&Fill:", self.fill_edit)
        self.layout.addRow("&Position:", self.position_edit)

        # connect handlers for changes to config
        self.fill_edit.valueChanged.connect(self.handle_fill_change)
        self.prefix_edit.textChanged.connect(self.handle_prefix_change)
        self.position_edit.currentTextChanged.connect(self.handle_position_change)
        self.start_edit.valueChanged.connect(self.handle_start_change)

    def handle_fill_change(self, value):
        self.config["fill"] = value

    def handle_position_change(self, text):
        self.config["position"] = text

    def handle_prefix_change(self, text):
        self.config["prefix"] = text

    def handle_start_change(self, value):
        self.config["start"] = value


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


class DocumentList(QTableView):

    def __init__(self, parent):
        """

        Args:
            parent (MainWindow) : parent window
        """
        super().__init__(parent)

        self.parent = parent

        self.setDisabled(True)

        self.header = self.horizontalHeader()
        self.clicked.connect(self.handle_document_change)

        self.setModel(self.parent.documents)

    def handle_document_change(self, index):
        row = self.parent.documents.itemFromIndex(index).row()
        file_name = self.parent.documents.item(row, 0).text()
        path = self.parent.documents.item(row, 1).text()
        path = os.path.join(path, file_name)
        self.parent.viewer.load_file(path)
        print(row, path)

    def add_document(self, path):
        """Add a document to the list."""
        self.setDisabled(False)
        with open(path, "rb") as pdf_file:
            reader = PyPDF2.PdfFileReader(pdf_file)
            page_count = str(reader.getNumPages())

        folder, filename = os.path.split(path)
        self.parent.documents.appendRow([QStandardItem(filename), QStandardItem(folder), QStandardItem(page_count)])




if __name__ == "__main__":
    app = Application(sys.argv)
    sys.exit(app.exec_())

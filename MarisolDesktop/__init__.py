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

        self.view = QWebEngineView()
        self.view.setUrl(QUrl("file:///view.html"))
        QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

        #self.view.page().settings().setAttribute()
        #self.view.
        #self.view.settingsQWebEngineSettings.setAttribute(, True)

        #self.view.setDisabled(True)
        self.setCentralWidget(self.view)

        self.documents_dock = QDockWidget("Documents", self)
        self.documents_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.documents_dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.documents_dock.setWidget(self.list)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.documents_dock)

        self.numbering_dock = QDockWidget("Numbering", self)
        self.numbering_dock.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        self.numbering_dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.TopDockWidgetArea, self.numbering_dock)

        self.add_documents_dialog = FileSelector(self, "Add Documents")



    def add_documents(self):
        """Opens the add file dialog."""
        self.add_documents_dialog.show()

    def load_file(self, path):
        with open(path, "rb") as pdf_file:
            self.pdf_data = pdf_file.read()
        return self.render_pdf()

    def render_pdf(self):
        """
        Draw the PDF using data cached in pdf_data.

        Returns:
            bool
        """
        # encode as base 64 and then convert to UTF-8
        self.pdf_data = base64.b64encode(self.pdf_data)
        self.pdf_data = self.pdf_data.decode('utf-8')
        script = "qpdf_ShowPdfFile('{}')".format(self.pdf_data)
        print(script)
        self.view.page().runJavaScript(script)
        # clear out variable once it is used
        self.pdf_data = None

        return True


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
        super().__init__(parent)

        self.parent = parent

        self.setDisabled(True)

        self.header = self.horizontalHeader()
        self.clicked.connect(self.doc_changed)

        self.setModel(self.parent.documents)

    def doc_changed(self, index):
        row = self.parent.documents.itemFromIndex(index).row()
        print(row)

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

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget


class TableWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        # self.tabs.resize(300, 200)

        self.tabs.addTab(self.tab1, "Configure")
        self.tabs.addTab(self.tab2, "Annotate")

        self.tab1.layout = QVBoxLayout(self.tab1)
        self.tab2.layout = QVBoxLayout(self.tab2)

        self.layout.addWidget(self.tabs)

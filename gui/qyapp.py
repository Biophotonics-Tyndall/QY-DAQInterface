# from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
from components.settings import SettingsForm
from components.chart import PanelWidget


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # set the title
        self.setWindowTitle("QY Controller")
        self.setGeometry(100, 100, 1200, 800)

        settingsForm = SettingsForm()
        # chartBox = ChartBox()
        panel = PanelWidget(parent=self)
        settingsForm.plot = panel.plot
        # settingsForm.plot = chartBox.plot
        layout = QHBoxLayout()

        layout.addWidget(settingsForm, 30)

        layout.addWidget(panel, 70)
        # layout.addWidget(chartBox, 70)
        # layout.addWidget(QPushButton('Save'), 70)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.statusBar()
        self.statusBar().addPermanentWidget(settingsForm.progress)
        # show all the widgets
        self.show()


# main method
if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)

    # create the instance of our Window
    window = Window()

    # start the app
    sys.exit(App.exec())

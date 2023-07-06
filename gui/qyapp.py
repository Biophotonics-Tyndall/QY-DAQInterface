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

        self.settingsForm = SettingsForm()
        # chartBox = ChartBox()
        panel = PanelWidget(parent=self)
        self.settingsForm.plot = panel.plot
        # self.settingsForm.plot = chartBox.plot
        layout = QHBoxLayout()

        layout.addWidget(self.settingsForm, 30)

        layout.addWidget(panel, 70)
        # layout.addWidget(chartBox, 70)
        # layout.addWidget(QPushButton('Save'), 70)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.statusBar()
        self.statusBar().addPermanentWidget(self.settingsForm.progress)
        status = 'Ready' if self.settingsForm.daq.devices else 'DAQ not found...'
        timeout = 3000 if self.settingsForm.daq.devices else 0
        self.statusBar().showMessage(status, msecs=timeout)
        # show all the widgets
        self.show()

    def eventFilter(self, obj, event):
        # Attempt to prevent the form to close on ESC button pressed (didn't work)
        print('Esc pressed 0')
        if obj is self.settingsForm and event.type() == QEvent.KeyPress:

            if event.key() in (Qt.Key_Return,
                               Qt.Key_Escape,
                               Qt.Key_Enter,):
                return True
        return super(Window, self).eventFilter(obj, event)


# main method
if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)

    # create the instance of our Window
    window = Window()

    # start the app
    sys.exit(App.exec())

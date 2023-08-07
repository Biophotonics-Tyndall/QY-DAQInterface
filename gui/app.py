"""
QY Controller GUI

This script initializes the QY Controller graphical user interface (GUI) application for controlling lab equipment. 
The GUI consists of a main window containing settings controls and a plotting panel.

Modules and Classes:
- Window: QMainWindow subclass representing the main application window.

Classes in Other Modules Used:
- SettingsForm: A class from the 'components.settingsarea.settings' module, representing the settings controls area.
- PanelWidget: A class from the 'components.plottingarea.panel' module, representing the plotting panel.

Usage:
1. Run this script to launch the QY Controller GUI.
2. Interact with the settings controls and observe the data plotted in the panel.

Dependencies:
- PyQt5.QtWidgets: The PyQt5 library is used to create the graphical user interface.
- components.settingsarea.settings.SettingsForm: The settings control area is implemented using this class.
- components.plottingarea.panel.PanelWidget: The plotting panel is implemented using this class.

"""

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QProgressBar,
    QMainWindow,
    QWidget
)
from components.settingsarea.settings import SettingsForm
from components.plottingarea.panel import PanelWidget


class Window(QMainWindow):
    def __init__(self, parent=None):
        """
        Initialize the QY Controller main window.

        This method sets up the main window, including the layout, settings controls area, and plotting panel.
        It also creates a status bar and connects it with the settings controls for displaying updates.

        Args:
            parent: Parent widget (default: None).

        Returns:
            None
        """
        super(Window, self).__init__(parent)

        self.setGeometry(100, 100, 1200, 800)
        self.setWindowTitle("QY Controller")
        centralWidget = QWidget()
        layout = QHBoxLayout()

        self.settingsWidget = SettingsForm()
        self.panel = PanelWidget(parent=self)
        self.settingsWidget.plot = self.panel.plot

        layout.addWidget(self.settingsWidget, 30)
        layout.addWidget(self.panel, 70)

        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self._createStatusBar()
        self.updateStatusBar()

        self.show()

    def _createStatusBar(self):
        """
        Create the status bar in the main window.

        This method creates a progress bar within the status bar and connects it to the updateStatusBar method.

        Args:
            None

        Returns:
            None
        """
        self.settingsWidget.progress = QProgressBar()
        self.settingsWidget.progress.hide()
        self.settingsWidget.updateStatusBar = self.updateStatusBar
        self.statusBar().addPermanentWidget(self.settingsWidget.progress)

    def updateStatusBar(self):
        """
        Update the status bar message.

        This method updates the status bar message with the current status of the settings controls.

        Args:
            None

        Returns:
            None
        """
        self.statusBar().showMessage(self.settingsWidget.status)


def main():
    """
    Main function to launch the QY Controller GUI.

    This function initializes the PyQt5 application, creates the main window, and starts the event loop.

    Args:
        None

    Returns:
        None
    """
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

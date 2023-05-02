from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from PyQt5.QtWidgets import QGroupBox, QWidget, QVBoxLayout, QScrollArea, QPushButton
import matplotlib
matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class ChartBox(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        # self.canvas.axes.plot([0, 1, 2, 3, 4], [10, 1, 20, 3, 40])
        toolbar = NavigationToolbar2QT(self.canvas, self)

        plotGroupBox = QGroupBox("Results")
        groupBoxVLayout = QVBoxLayout()

        groupBoxVLayout.addWidget(self.canvas)
        groupBoxVLayout.addWidget(toolbar)

        plotGroupBox.setLayout(groupBoxVLayout)

        scrollArea = QScrollArea()
        scrollArea.setWidget(plotGroupBox)
        scrollArea.setWidgetResizable(True)
        # self.scroll.setFixedHeight(400)

        # creating a vertical layout
        mainLayout = QVBoxLayout()

        # adding form group box to the layout
        mainLayout.addWidget(scrollArea)

        # adding button box to the layout
        saveButton = QPushButton("Save")
        mainLayout.addWidget(saveButton)

        # setting lay out
        self.setLayout(mainLayout)

    def plot(self):
        self.canvas.axes.cla()
        self.canvas.axes.plot([0, 1, 2, 3, 4], [10, 1, 20, 3, 40])
        self.canvas.draw()

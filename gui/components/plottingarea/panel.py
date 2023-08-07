import matplotlib.pyplot as pl
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QMessageBox
import matplotlib
matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        super(MplCanvas, self).__init__(self.fig)


class PanelWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(False)
        self.layout.addWidget(self.scroll)
        self.nAxes = 5
        self.createFig()
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.draw()
        self.scroll.setWidget(self.canvas)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.layout.addWidget(self.toolbar)
        self.setLayout(self.layout)

    def createFig(self):
        width = self.parent.frameGeometry().width() * 0.66 / 100
        height = self.nAxes * 3
        self.fig, self.axs = pl.subplots(self.nAxes, sharex=True,
                                         figsize=(width, height))
        self.axs[-1].set_xlabel('Time (s)')
        self.fig.tight_layout()

    def plot(self, daq):

        if not daq._data.empty:
            self.nAxes = daq._nChannels
            plottedData = []
            for ax in range(self.nAxes):
                plottedData.extend(self.axs[ax].lines)
            if plottedData:
                reply = QMessageBox.question(self, 'Overwrite', 'Do you want to overwrite the current plotted data?',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            else:
                reply = QMessageBox.Yes

            for ax in range(self.nAxes):
                if self.axs[ax].lines and (reply == QMessageBox.Yes):
                    self.axs[ax].cla()
                else:
                    pass
                label = daq._config['Channels'][f'ai{ax}']
                self.axs[ax].plot(daq._data['time'],
                                  daq._data[ax],
                                  label=daq._REFERENCE.capitalize() if label == 'pmr' else daq._SAMPLE.capitalize(),
                                  marker='h',
                                  ms=5,
                                  alpha=0.5,
                                  linestyle='-.',
                                  lw=1
                                  )
                self.axs[ax].set_ylabel('Input (V)')
                self.axs[ax].legend(
                    title=f"Ch.{ax}: {label.upper()}")
            self.fig.tight_layout()
            self.canvas.draw()

        else:
            print('No data to plot...')

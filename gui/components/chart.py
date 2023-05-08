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
            reply = QMessageBox.question(self, 'Overwrite', 'Do you want to overwrite the current plotted data?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            for ax in range(self.nAxes):
                if self.axs[ax].lines and (reply == QMessageBox.Yes):
                    self.axs[ax].cla()
                else:
                    pass
                label = daq._config['Channels'][f'ai{ax}']
                self.axs[ax].plot(daq._data['time'],
                                  daq._data[ax],
                                  label=daq._SAMPLE.capitalize(),
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

    # def plot_(self, daq):

    #     pl.rcParams.update({'font.size': 12})
    #     # 1 subplot per channel
    #     self.nAxes = daq._nChannels
    #     # self.resetLayout()
    #     self.canvas.axes = []
    #     if not daq._data.empty:
    #         reply = QMessageBox.question(self, 'Overwrite', 'Do you want to overwrite the current plotted data?',
    #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    #         if reply == QMessageBox.Yes:
    #             self.canvas.fig.clf()
    #         for ax in range(self.nAxes):
    #             label = daq._config['Channels'][f'ai{ax}']
    #             self.canvas.axes.append(
    #                 self.canvas.fig.add_subplot(int(f"{self.nAxes}1{ax+1}")))
    #             if reply == QMessageBox.Yes:
    #                 self.canvas.axes[ax].cla()
    #             self.canvas.axes[ax].plot(
    #                 daq._data['time'], daq._data[ax], label=daq._SAMPLE.capitalize())
    #             self.canvas.axes[ax].set_ylabel('Input (V)')
    #             self.canvas.axes[ax].legend(
    #                 title=f"Ch.{ax}: {label.upper()}")
    #         self.canvas.axes[0].get_shared_x_axes().join(
    #             self.canvas.axes[0], *self.canvas.axes[1:])
    #         self.canvas.axes[-1].set_xlabel('Time (s)')
    #         self.canvas.draw()
    #     pl.tight_layout()
        # pl.ion()
        # if not self._data.empty:
        #     if pl.get_fignums() == []:
        #         self.initializeplotgui()
        #     dynamConfig = configparser.ConfigParser()
        #     dynamConfig.read("config.txt")
        #     gConfig = dynamConfig['Graph Settings']
        #     cConfig = self._config['Channels']
        #     extraPConfig = self._config['Extra Parameters']

        #     self._axs[0].set_title(gConfig['title'])
        #     if self._axs[0].lines:
        #         action = input('Overwrite data? [y or press enter]: ')
        #         if action == 'y':
        #             for n in range(self._nChannels):
        #                 self._axs[n].lines = []
        #     for n in range(self._nChannels):
        #         label = extraPConfig[gConfig['label']
        #                              ] if gConfig['label'] in extraPConfig else gConfig['label']
        #         self._axs[n].plot(self._data['time'], self._data[n], label=label,
        #                           marker=gConfig['marker'],
        #                           ms=float(gConfig['marker size']),
        #                           color=gConfig['colour'],
        #                           alpha=float(gConfig['alpha']),
        #                           linestyle=gConfig['line style'],
        #                           lw=float(gConfig['line width'])
        #                           )
        #         self._axs[n].legend(
        #             title=f"Ch.{n}: {cConfig[self._IN_CHANNELS[n]]}")
        #         self._axs[n].set_ylabel('Input (V)')
        #         self._axs[n].grid(gConfig['grid'])

        #     self._fig.tight_layout()
        #     self._fig.show()
        #     print('Data plotted...')
        # else:
        #     print('No data to plot...')

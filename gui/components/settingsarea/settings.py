from PyQt5.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget
)
import numpy as np
from components.settingsarea.components.blocks import (
    LaserSettings,
    PowerMeterRSettings,
    PowerMeterSSettings,
    APD1Settings,
    APD2Settings,
    ControlSettings,
    AcquisitionSettings,
    MeasurementSettings
)
from components.device.device import LASERS
from utils.utils import STATUS
from backend.daq import Controller


class SettingsForm(QWidget):
    def __init__(self, parent=None):
        super(SettingsForm, self).__init__(parent)

        mainLayout = QVBoxLayout()

        form = self._createFormWidget()
        actionButtons = self._createButtonsAreaWidget()

        # bind handle on change method
        self.laserSettings.lineComboBox.currentIndexChanged.connect(
            self.handleOnChangeLaserLine
        )

        mainLayout.addWidget(form)
        mainLayout.addWidget(actionButtons)

        self.setLayout(mainLayout)

        self.initialiseController()

    def _createFormWidget(self):

        # Create Settings blocks objects
        self.laserSettings = LaserSettings()
        self.pmsSettings = PowerMeterSSettings()
        self.pmrSettings = PowerMeterRSettings()
        self.apd1Settings = APD1Settings()
        self.apd2Settings = APD2Settings()
        self.controlSettings = ControlSettings()
        self.acquisitionSettings = AcquisitionSettings()
        self.measurementSettings = MeasurementSettings()

        self._setDevicesToMonitor()

        # Create Layout
        formLayout = QVBoxLayout()
        formLayout.addWidget(self.laserSettings)
        formLayout.addWidget(self.pmsSettings)
        formLayout.addWidget(self.pmrSettings)
        formLayout.addWidget(self.apd1Settings)
        formLayout.addWidget(self.apd2Settings)
        formLayout.addWidget(self.controlSettings)
        formLayout.addWidget(self.acquisitionSettings)
        formLayout.addWidget(self.measurementSettings)

        # Create widget
        formWidget = QWidget()
        formWidget.setLayout(formLayout)

        # Creating a scroll area
        scrollArea = QScrollArea()
        scrollArea.setWidget(formWidget)
        scrollArea.setWidgetResizable(True)

        return scrollArea

    def _createButtonsAreaWidget(self):

        # create buttons
        self.runButton = QPushButton('Run')
        self.runButton.clicked.connect(self.run)
        self.saveButton = QPushButton('Save')
        self.saveButton.setEnabled(False)
        self.saveButton.clicked.connect(self.save)

        buttonsWidget = QWidget()
        layout = QHBoxLayout()
        layout.stretch(1)
        layout.addWidget(self.runButton)
        layout.addWidget(self.saveButton)
        buttonsWidget.setLayout(layout)

        return buttonsWidget

    def _setDevicesToMonitor(self):

        devicesToMonitor = [
            self.pmsSettings,
            self.pmrSettings,
            self.apd1Settings,
            self.apd2Settings,
            self.controlSettings
        ]

        for index in range(len(devicesToMonitor)):
            device = devicesToMonitor.pop(index)
            device.devicesToMonitor = tuple(devicesToMonitor)
            devicesToMonitor.insert(index, device)

    def initialiseController(self):
        self.daq = Controller()
        self.daq.updateProgress = self.updateProgress
        self.status = STATUS.READY if self.daq.devices else STATUS.DAQ404

    def handleOnChangeLaserLine(self, value):

        minVoltage, maxVoltage, step = LASERS.modulation(
            line=LASERS.LINES[value])
        self.controlSettings.setRangeAndStep(minVoltage, maxVoltage, step)

    def updateProgress(self, value):
        self.progress.setValue(round(value))

    def updateStatus(self, newStatus):
        self.status = newStatus
        self.updateStatusBar()

    def setDaqConfig(self):
        # Set channels
        channels = [
            self.laserSettings.chComboBox.currentText(),
            self.controlSettings.chComboBox.currentText(),
            self.pmsSettings.chComboBox.currentText(),
            self.pmrSettings.chComboBox.currentText(),
            self.apd1Settings.chComboBox.currentText(),
            self.apd2Settings.chComboBox.currentText()
        ]
        self.daq._OUT_CHANNEL = [ch.lower()
                                 for ch in channels if 'o' in ch.lower()]

        self.daq._IN_CHANNELS = sorted(
            [ch.lower() for ch in channels if 'i' in ch.lower()])

        self.daq._config = {'Channels': {
            self.laserSettings.chComboBox.currentText().lower(): 'laser',
            self.controlSettings.chComboBox.currentText().lower(): 'trigger',
            self.pmsSettings.chComboBox.currentText().lower(): 'pms',
            self.pmrSettings.chComboBox.currentText().lower(): 'pmr',
            self.apd1Settings.chComboBox.currentText().lower(): 'apd1',
            self.apd2Settings.chComboBox.currentText().lower(): 'apd2'
        }}

        self.daq._nChannels = len(self.daq._IN_CHANNELS)

        # Set power range
        self.daq._RANGE_START = float(self.controlSettings.startSpinBox.text())
        self.daq._RANGE_END = float(self.controlSettings.endSpinBox.text())
        self.daq._STEP_SIZE = float(self.controlSettings.stepSpinBox.text())
        self.daq._STEP_RESET = self.acquisitionSettings.pulsedCheckBox.isChecked()

        # Set timing
        self.daq._TIME_PER_STEP = float(
            self.acquisitionSettings.timingSpinBar.text())

        # Set sampling
        self.daq._INTERNAL_SAMPLES_PER_CH = int(
            self.acquisitionSettings.samplingSpinBar.text())
        self.daq._SAMPLING_RATE = self.daq._INTERNAL_SAMPLES_PER_CH / self.daq._TIME_PER_STEP
        self.daq._MIN_READING_VAL = 0.0
        self.daq._MAX_READING_VAL = 10.0

        self.daq._SAMPLE = self.measurementSettings.sampleLineEdit.text()
        self.daq._REFERENCE = self.measurementSettings.referenceLineEdit.text()
        self.daq._EXCITATION_WAVELENGTH = self.laserSettings.lineComboBox.currentText()
        self.daq._BEAM_SPOT = self.laserSettings.beamLineComboBox.currentText()
        self.daq._SAMPLE_POWER_METER_RANGE = self.pmsSettings.rangeComboBox.currentText()
        self.daq._REFERENCE_POWER_METER_RANGE = self.pmrSettings.rangeComboBox.currentText()
        self.daq._APD1_GAIN = self.apd1Settings.gainComboBox.currentText()
        self.daq._APD1_DETECTION_WAVELENGTH = self.apd1Settings.detectionWavelengthSpinBox.text()
        self.daq._APD2_GAIN = self.apd2Settings.gainComboBox.currentText()
        self.daq._APD2_DETECTION_WAVELENGTH = self.apd2Settings.detectionWavelengthSpinBox.text()

        self.daq._NOTES = self.measurementSettings.notesTextBox.toPlainText().replace(' ',
                                                                                      '').replace('\n', '/')

        self.daq._outputArr = np.arange(
            self.daq._RANGE_START, self.daq._RANGE_END, self.daq._STEP_SIZE)
        if self.daq._STEP_RESET:
            tempArr = np.delete(self.daq._outputArr,
                                np.where(self.daq._outputArr == 0))
            self.daq._outputArr = np.zeros(2 * tempArr.size)
            self.daq._outputArr[1::2] = tempArr

    def runAcquisition(self):
        self.daq.start()

    def stopAcquisition(self):
        if self.daq.isRunning():
            self.daq.quit()
            self.daq.wait()

    def save(self):
        self.updateStatus(STATUS.SAVINGDATA)
        self.daq.save()
        self.saveButton.setEnabled(False)
        self.updateStatus(STATUS.READY)

    def run(self):
        self.runButton.setEnabled(False)
        if self.status == STATUS.DATANOTSAVED:
            reply = QMessageBox.question(self, 'Save data', 'Do you want to save the last acquired data before continuing?\nAfter running a new experiment the data will be erased.',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.save()
            else:
                self.updateStatus(STATUS.READY)
                self.saveButton.setEnabled(False)

        if self.status == STATUS.READY:
            if self.measurementSettings.sampleLineEdit.text() \
                    and self.measurementSettings.referenceLineEdit.text():
                # self.runAcquisition()
                self.updateStatus(STATUS.RUNNING)
                self.progress.show()
                self.setDaqConfig()
                self.daq.run()
                self.daq.updatelog()
                # self.stopAcquisition()
                self.progress.hide()
                self.updateStatus(STATUS.DATANOTSAVED)
                self.saveButton.setEnabled(True)
                self.plot(self.daq)
            else:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setWindowTitle("Warning")
                msgBox.setText("Sample and reference fields must be filled")
                msgBox.exec_()
        else:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setWindowTitle("Warning")
            msgBox.setText(f"{self.status}. The system is not ready!")
            msgBox.exec_()

        self.runButton.setEnabled(True)

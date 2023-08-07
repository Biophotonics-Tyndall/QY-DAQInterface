from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget
)
from components.device.device import DAQ, LASERS, BEAMLINES, POWERMETERS, APDS


class SettingsBlock(QWidget):

    def __init__(self, parent=None):
        super(SettingsBlock, self).__init__(parent)
        self.rows = []

    def addRow(self, label='', labelToolTip='', widget=None):
        rowLayout = QHBoxLayout()
        labelWidget = QLabel(self)
        labelWidget.setText(label)
        if labelToolTip:
            labelWidget.setToolTip(labelToolTip)
        rowLayout.addWidget(labelWidget, stretch=1)
        if widget:
            rowLayout.addWidget(widget, stretch=2)
        self.rows.append(rowLayout)

    def createLayout(self):
        layout = QVBoxLayout()
        for row in self.rows:
            layout.addLayout(row)
        self.setLayout(layout)


class LaserSettings(SettingsBlock):

    def __init__(self, parent=None):
        super(LaserSettings, self).__init__(parent)

        self.addRow(label="Laser (?)",
                    labelToolTip='Laser settings: Set the power range to sweep')

        # Channels
        self.chComboBox = QComboBox()
        self.chComboBox.addItems(["None"] + DAQ.outputChannels)
        self.chComboBox.setCurrentText(DAQ.outputChannels[0])

        self.addRow(label="Channel", widget=self.chComboBox)

        # Laser line
        self.lineComboBox = QComboBox()
        self.lineComboBox.addItems(LASERS.LINES)

        self.addRow(label="Line", widget=self.lineComboBox)

        # Beam line combo box
        self.beamLineComboBox = QComboBox()
        self.beamLineComboBox.addItems(BEAMLINES)

        self.addRow(label="Beam spot", widget=self.beamLineComboBox)

        # Create layout
        self.createLayout()


class PowerMeterSSettings(SettingsBlock):

    def __init__(self, parent=None):
        super(PowerMeterSSettings, self).__init__(parent)

        self.addRow(label="Power Meter - Sample (?)",
                    labelToolTip='Power Meter connected to the cuvette holder with the sample')

        # Channels
        self.chComboBox = QComboBox()
        self.chComboBox.addItems(["None"] + DAQ.inputChannels)
        self.chComboBox.setCurrentText(DAQ.inputChannels[0])
        self.devicesToMonitor = []
        self.chComboBox.currentTextChanged.connect(
            self._handleOnChangeChComboBox)

        self.addRow(label="Channel", widget=self.chComboBox)

        # Measurement range
        self.rangeComboBox = QComboBox()
        self.rangeComboBox.addItems(POWERMETERS.PMSRANGES)

        self.addRow(label="Range", widget=self.rangeComboBox)

        # Create layout
        self.createLayout()

    def _handleOnChangeChComboBox(self, value):
        for device in self.devicesToMonitor:
            if device.chComboBox.currentText() == value:
                device.chComboBox.setCurrentText('None')


class PowerMeterRSettings(SettingsBlock):

    def __init__(self, parent=None):
        super(PowerMeterRSettings, self).__init__(parent)

        self.addRow(label="Power Meter - Reference (?)",
                    labelToolTip='Power Meter connected to the cuvette holder with the reference')

        # Channels
        self.chComboBox = QComboBox()
        self.chComboBox.addItems(["None"] + DAQ.inputChannels)
        self.chComboBox.setCurrentText(DAQ.inputChannels[1])
        self.devicesToMonitor = []
        self.chComboBox.currentTextChanged.connect(
            self._handleOnChangeChComboBox)

        self.addRow(label="Channel", widget=self.chComboBox)

        # Measurement range
        self.rangeComboBox = QComboBox()
        self.rangeComboBox.addItems(POWERMETERS.PMRRANGES)

        self.addRow(label="Range", widget=self.rangeComboBox)

        # Create layout
        self.createLayout()

    def _handleOnChangeChComboBox(self, value):
        for device in self.devicesToMonitor:
            if device.chComboBox.currentText() == value:
                device.chComboBox.setCurrentText('None')


class APD1Settings(SettingsBlock):

    def __init__(self, parent=None):
        super(APD1Settings, self).__init__(parent)

        self.addRow(label="APD1 (?)",
                    labelToolTip='APD on transmission mode after the dichroic mirror')

        # Channels
        self.chComboBox = QComboBox()
        self.chComboBox.addItems(["None"] + DAQ.inputChannels)
        self.chComboBox.setCurrentText(DAQ.inputChannels[2])
        self.devicesToMonitor = []
        self.chComboBox.currentTextChanged.connect(
            self._handleOnChangeChComboBox)

        self.addRow(label="Channel", widget=self.chComboBox)

        # Gain
        self.gainComboBox = QComboBox()
        self.gainComboBox.addItems(APDS.GAINS)

        self.addRow(label="Gain", widget=self.gainComboBox)

        # Wavelength of measurement
        self.detectionWavelengthSpinBox = QSpinBox()
        self.detectionWavelengthSpinBox.setRange(300, 1200)

        self.addRow(label="Wavelength", widget=self.detectionWavelengthSpinBox)

        # Create layout
        self.createLayout()

    def _handleOnChangeChComboBox(self, value):
        for device in self.devicesToMonitor:
            if device.chComboBox.currentText() == value:
                device.chComboBox.setCurrentText('None')


class APD2Settings(SettingsBlock):

    def __init__(self, parent=None):
        super(APD2Settings, self).__init__(parent)

        self.addRow(label="APD2 (?)",
                    labelToolTip='APD on reflection mode after the dichroic mirror')

        # Channels
        self.chComboBox = QComboBox()
        self.chComboBox.addItems(["None"] + DAQ.inputChannels)
        self.chComboBox.setCurrentText(DAQ.inputChannels[3])
        self.devicesToMonitor = []
        self.chComboBox.currentTextChanged.connect(
            self._handleOnChangeChComboBox)

        self.addRow(label="Channel", widget=self.chComboBox)

        # Gain
        self.gainComboBox = QComboBox()
        self.gainComboBox.addItems(APDS.GAINS)

        self.addRow(label="Gain", widget=self.gainComboBox)

        # Wavelength of measurement
        self.detectionWavelengthSpinBox = QSpinBox()
        self.detectionWavelengthSpinBox.setRange(300, 1200)

        self.addRow(label="Wavelength", widget=self.detectionWavelengthSpinBox)

        # Create layout
        self.createLayout()

    def _handleOnChangeChComboBox(self, value):
        for device in self.devicesToMonitor:
            if device.chComboBox.currentText() == value:
                device.chComboBox.setCurrentText('None')


class ControlSettings(SettingsBlock):

    def __init__(self, parent=None):
        super(ControlSettings, self).__init__(parent)

        self.addRow(label="Control (?)",
                    labelToolTip='Set the laser modulation settings')

        # Channels
        self.chComboBox = QComboBox()
        self.chComboBox.addItems(["None"] + DAQ.inputChannels)
        self.chComboBox.setCurrentText(DAQ.inputChannels[4])
        self.devicesToMonitor = []
        self.chComboBox.currentTextChanged.connect(
            self.handleOnChangeChComboBox)

        self.addRow(label="Feedback", widget=self.chComboBox)

        # Voltage to modulate the laser
        minV, maxV, step = LASERS.modulation(LASERS.LINES[0])
        # Starting voltage
        self.startSpinBox = QDoubleSpinBox()
        self.startSpinBox.setDecimals(3)
        self.startSpinBox.valueChanged.connect(
            self.handleOnChangeStartSpinBox
        )

        self.addRow(label="Start", widget=self.startSpinBox)

        # Ending point
        self.endSpinBox = QDoubleSpinBox()
        self.endSpinBox.setDecimals(3)

        self.endSpinBox.valueChanged.connect(
            self.handleOnChangeEndSpinBox
        )

        self.addRow(label="End", widget=self.endSpinBox)

        self.stepSpinBox = QDoubleSpinBox()
        self.stepSpinBox.setDecimals(3)
        self.stepSpinBox.setValue(step)
        self.stepSpinBox.setToolTip(
            'The step size affects the number of total data points to be acquired')

        self.addRow(label="Step", widget=self.stepSpinBox)

        self.setRangeAndStep(minV, maxV, step)

        # Create layout
        self.createLayout()

    def setRangeAndStep(self, minV, maxV, step):
        self.startSpinBox.setRange(minV, maxV)
        self.startSpinBox.setSingleStep(step)

        minV = self.startSpinBox.value()
        self.endSpinBox.setRange(minV, maxV)
        self.endSpinBox.setValue(maxV)
        self.endSpinBox.setSingleStep(step)

        self.setStepSpinBox()

    def setStepSpinBox(self):
        maxV = self.endSpinBox.value() - self.startSpinBox.value()
        minV = 0.001
        self.stepSpinBox.setRange(minV, maxV)
        self.stepSpinBox.setSingleStep(minV)

    def handleOnChangeEndSpinBox(self, value):
        self.startSpinBox.setMaximum(value)
        self.setStepSpinBox()

    def handleOnChangeStartSpinBox(self, value):
        self.endSpinBox.setMinimum(value)
        self.setStepSpinBox()

    def handleOnChangeChComboBox(self, value):
        for device in self.devicesToMonitor:
            if device.chComboBox.currentText() == value:
                device.chComboBox.setCurrentText('None')


class AcquisitionSettings(SettingsBlock):

    def __init__(self, parent=None):
        super(AcquisitionSettings, self).__init__(parent)

        self.addRow(label="Acquisition (?)",
                    labelToolTip='Set the acquisition settings')

        # Sampling
        self.samplingSpinBar = QSpinBox()
        self.samplingSpinBar.setMaximum(50000)
        self.samplingSpinBar.setValue(1000)
        self.samplingSpinBar.setSingleStep(50)
        self.samplingSpinBar.setToolTip('The number of samples per step')

        self.addRow(label="Samples per step", widget=self.samplingSpinBar)

        # Timing
        self.timingSpinBar = QDoubleSpinBox()
        self.timingSpinBar.setDecimals(1)
        self.timingSpinBar.setValue(0.3)
        self.timingSpinBar.setToolTip(
            'It refers to the time taken to acquire the number of samples per step set above')

        self.addRow(label="Time per step", widget=self.timingSpinBar)

        # Pulsed
        self.pulsedCheckBox = QCheckBox()

        self.addRow(label="Pulse", widget=self.pulsedCheckBox)

        # Create layout
        self.createLayout()


class MeasurementSettings(SettingsBlock):

    def __init__(self, parent=None):
        super(MeasurementSettings, self).__init__(parent)

        self.addRow(label="Measurement details (?)",
                    labelToolTip='Set the measurement details')

        # sample label
        self.sampleLineEdit = QLineEdit()
        self.sampleLineEdit.setText('s001')

        self.addRow(label="Sample", widget=self.sampleLineEdit)

        # reference label
        self.referenceLineEdit = QLineEdit()
        self.referenceLineEdit.setText('water')

        self.addRow(label="Reference", widget=self.referenceLineEdit)

        # Extra notes
        self.notesTextBox = QPlainTextEdit()
        self.notesTextBox.setPlainText("attenuation = 0")

        self.addRow(label="Notes", widget=self.notesTextBox)

        # Create layout
        self.createLayout()

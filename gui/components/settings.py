# importing libraries
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys
import numpy as np
from backend.daq import Controler


class SettingsForm(QDialog):

    # constructor
    def __init__(self):
        super(SettingsForm, self).__init__()

        self.initializeDaqController()
        # creating a group box
        self.formGroupBox = QGroupBox("Experiment settings")

        ############# Laser sweep settings ##############
        # Channels connections combo box
        outputChannels = ['AO0', 'AO1']
        self.laserChannelComboBox = QComboBox()
        self.laserChannelComboBox.addItems(outputChannels)
        self.laserChannelComboBox.setCurrentText('AO0')

        # Laser line combo box
        self.laserLineComboBox = QComboBox()
        self.laserLineComboBox.addItems(["405 nm", "785 nm", "976 nm"])
        self.laserLineComboBox.currentTextChanged.connect(
            self.setOnChangeLaserLine)

        # Beam spot combo box
        self.beamSpotComboBox = QComboBox()
        self.beamSpotComboBox.addItems(["Narrow", "Wide"])

        ############# Power-meter S settings ##############
        inputChannels = ['AI0', 'AI1', 'AI2', 'AI3',
                         'AI4', 'AI5', 'AI6', 'AI7', 'None']
        # Input channel combo box
        self.powerMeterSChannelComboBox = QComboBox()
        self.powerMeterSChannelComboBox.addItems(inputChannels)
        self.powerMeterSChannelComboBox.setCurrentText('AI1')
        self.powerMeterSChannelComboBox.currentTextChanged.connect(
            self.setOnChangePowerMeterS)

        # PMS range
        self.powerMeterSRangeComboBox = QComboBox()
        self.powerMeterSRangeComboBox.addItems(['69 mW'])

        ############# Power-meter R settings ##############
        # Input channel combo box
        self.powerMeterRChannelComboBox = QComboBox()
        self.powerMeterRChannelComboBox.addItems(inputChannels)
        self.powerMeterRChannelComboBox.setCurrentText('AI2')
        self.powerMeterRChannelComboBox.currentTextChanged.connect(
            self.setOnChangePowerMeterR)

        # PMS range
        self.powerMeterRRangeComboBox = QComboBox()
        self.powerMeterRRangeComboBox.addItems(['61 mW'])

        ############# APD1 settings ##############
        # Input channel combo box
        self.apd1ChannelComboBox = QComboBox()
        self.apd1ChannelComboBox.addItems(inputChannels)
        self.apd1ChannelComboBox.setCurrentText('AI3')
        self.apd1ChannelComboBox.currentTextChanged.connect(
            self.setOnChangeAPD1)

        # Gain combo box
        self.apd1GainComboBox = QComboBox()
        self.apd1GainComboBox.addItems(['Min', 'Max'])

        # Detection wavelength
        self.apd1DetectionWavelengthSpinBox = QSpinBox()
        self.apd1DetectionWavelengthSpinBox.setRange(300, 1200)

        ############# APD2 settings ##############
        # Input channel combo box
        self.apd2ChannelComboBox = QComboBox()
        self.apd2ChannelComboBox.addItems(inputChannels)
        self.apd2ChannelComboBox.setCurrentText('AI4')
        self.apd2ChannelComboBox.currentTextChanged.connect(
            self.setOnChangeAPD2)

        # Gain combo box
        self.apd2GainComboBox = QComboBox()
        self.apd2GainComboBox.addItems(['Min', 'Max'])

        # Detection wavelength
        self.apd2DetectionWavelengthSpinBox = QSpinBox()
        self.apd2DetectionWavelengthSpinBox.setRange(300, 1200)

        ############# Control and acquisition settings ##############
        # Trigger feedback channel combo box
        self.feedbackChannelComboBox = QComboBox()
        self.feedbackChannelComboBox.addItems(inputChannels)
        self.feedbackChannelComboBox.setCurrentText('AI0')
        self.feedbackChannelComboBox.currentTextChanged.connect(
            self.setOnChangeFeedback)

        # Starting point: creating spin box
        self.laserStartSpinBar = QDoubleSpinBox()
        self.laserStartSpinBar.setDecimals(3)
        self.laserStartSpinBar.setMaximum(0.16)
        self.laserStartSpinBar.setSingleStep(0.01)

        # Ending point: creating spin box
        self.laserEndSpinBar = QDoubleSpinBox()
        self.laserEndSpinBar.setDecimals(3)
        self.laserEndSpinBar.setMaximum(0.170)
        self.laserEndSpinBar.setSingleStep(0.01)
        self.laserEndSpinBar.setValue(0.170)

        # Step size: creating spin box
        self.laserStepSpinBar = QDoubleSpinBox()
        self.laserStepSpinBar.setDecimals(3)
        self.laserStepSpinBar.setMaximum(0.17)
        self.laserStepSpinBar.setValue(0.01)
        self.laserStepSpinBar.setSingleStep(0.01)
        self.laserStepSpinBar.setToolTip(
            'The step size affects the number of total data points to be acquired')

        # Sampling: creating spin box
        self.samplingSpinBar = QSpinBox()
        self.samplingSpinBar.setMaximum(50000)
        self.samplingSpinBar.setValue(1000)
        self.samplingSpinBar.setSingleStep(50)
        self.samplingSpinBar.setToolTip('The number of samples per step')

        # Timing: creating spin box
        self.timingSpinBar = QDoubleSpinBox()
        self.timingSpinBar.setDecimals(1)
        self.timingSpinBar.setValue(0.3)
        self.timingSpinBar.setToolTip(
            'It refers to the time taken to acquire the N samples per step')

        # Pulsed: creating a check box
        self.pulsedCheckBox = QCheckBox()

        ############# Acquisition time settings ##############
        # sample label Line edit
        self.sampleLineEdit = QLineEdit()
        self.sampleLineEdit.setText('s013')

        # reference label Line edit
        self.referenceLineEdit = QLineEdit()
        self.referenceLineEdit.setText('water')

        self.notesTextBox = QPlainTextEdit()
        self.notesTextBox.setPlainText("attenuation = 0")

        # calling the method that create the form
        self.createForm()

        # creating a dialog button for ok and cancel
        self.runButton = QPushButton("Run")
        self.runButton.clicked.connect(self.getInfo)
        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.save)
        self.saveButton.setEnabled(False)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton(self.runButton, QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(self.saveButton, QDialogButtonBox.AcceptRole)

        # adding action when form is accepted
        # self.buttonBox.accepted.connect(self.getInfo)

        # Creating a scroll area and put all the elements inside
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.formGroupBox)
        self.scroll.setWidgetResizable(True)
        # self.scroll.setFixedHeight(400)

        # creating a vertical layout
        mainLayout = QVBoxLayout()

        # adding form group box to the layout
        mainLayout.addWidget(self.scroll)

        # adding button box to the layout
        mainLayout.addWidget(self.buttonBox)

        # setting lay out
        self.setLayout(mainLayout)

    def initializeDaqController(self):
        self.daq = Controler()

    def save(self):
        self.daq.savelog()
        self.saveButton.setEnabled(False)

    def setOnChangeFeedback(self, value):
        devices = [
            self.powerMeterSChannelComboBox,
            self.powerMeterRChannelComboBox,
            self.apd1ChannelComboBox,
            self.apd2ChannelComboBox
        ]
        for device in devices:
            if device.currentText() == value:
                device.setCurrentText('None')

    def setOnChangePowerMeterS(self, value):
        devices = [
            self.feedbackChannelComboBox,
            self.powerMeterRChannelComboBox,
            self.apd1ChannelComboBox,
            self.apd2ChannelComboBox
        ]
        for device in devices:
            if device.currentText() == value:
                device.setCurrentText('None')

    def setOnChangePowerMeterR(self, value):
        devices = [
            self.feedbackChannelComboBox,
            self.powerMeterSChannelComboBox,
            self.apd1ChannelComboBox,
            self.apd2ChannelComboBox
        ]
        for device in devices:
            if device.currentText() == value:
                device.setCurrentText('None')

    def setOnChangeAPD1(self, value):
        devices = [
            self.feedbackChannelComboBox,
            self.powerMeterRChannelComboBox,
            self.powerMeterSChannelComboBox,
            self.apd2ChannelComboBox
        ]
        for device in devices:
            if device.currentText() == value:
                device.setCurrentText('None')

    def setOnChangeAPD2(self, value):
        devices = [
            self.feedbackChannelComboBox,
            self.powerMeterRChannelComboBox,
            self.powerMeterSChannelComboBox,
            self.apd1ChannelComboBox
        ]
        for device in devices:
            if device.currentText() == value:
                device.setCurrentText('None')

    # On change the laser line
    def setOnChangeLaserLine(self, value):

        if value == "405 nm":
            maxVoltage = 0.170
            step = 0.002
        elif value == "785 nm":
            maxVoltage = 1.678
            step = 0.01
        elif value == "976 nm":
            maxVoltage = 5.400
            step = 0.1

        self.laserStartSpinBar.setRange(0, maxVoltage)
        self.laserEndSpinBar.setMaximum(maxVoltage)
        self.laserEndSpinBar.setValue(maxVoltage)
        self.laserStepSpinBar.setMaximum(maxVoltage)
        self.laserStepSpinBar.setValue(step)

    def setDaqConfig(self):
        # Set channels
        channels = [
            self.laserChannelComboBox.currentText(),
            self.feedbackChannelComboBox.currentText(),
            self.powerMeterSChannelComboBox.currentText(),
            self.powerMeterRChannelComboBox.currentText(),
            self.apd1ChannelComboBox.currentText(),
            self.apd2ChannelComboBox.currentText()
        ]
        self.daq._OUT_CHANNEL = [ch.lower()
                                 for ch in channels if 'o' in ch.lower()]

        self.daq._IN_CHANNELS = sorted(
            [ch.lower() for ch in channels if 'i' in ch.lower()])

        self.daq._config = {'Channels': {
            self.laserChannelComboBox.currentText().lower(): 'laser',
            self.feedbackChannelComboBox.currentText().lower(): 'trigger',
            self.powerMeterSChannelComboBox.currentText().lower(): 'pms',
            self.powerMeterRChannelComboBox.currentText().lower(): 'pmr',
            self.apd1ChannelComboBox.currentText().lower(): 'apd1',
            self.apd2ChannelComboBox.currentText().lower(): 'apd2'
        }}

        self.daq._nChannels = len(self.daq._IN_CHANNELS)

        # Set power range
        self.daq._RANGE_START = float(self.laserStartSpinBar.text())
        self.daq._RANGE_END = float(self.laserEndSpinBar.text())
        self.daq._STEP_SIZE = float(self.laserStepSpinBar.text())
        self.daq._STEP_RESET = self.pulsedCheckBox.isChecked()

        # Set timing
        self.daq._TIME_PER_STEP = float(self.timingSpinBar.text())

        # Set sampling
        self.daq._INTERNAL_SAMPLES_PER_CH = int(self.samplingSpinBar.text())
        self.daq._SAMPLING_RATE = self.daq._INTERNAL_SAMPLES_PER_CH / self.daq._TIME_PER_STEP
        self.daq._MIN_READING_VAL = 0.0
        self.daq._MAX_READING_VAL = 10.0

        self.daq._SAMPLE = self.sampleLineEdit.text()
        self.daq._REFERENCE = self.referenceLineEdit.text()
        self.daq._EXCITATION_WAVELENGTH = self.laserLineComboBox.currentText()
        self.daq._BEAM_SPOT = self.beamSpotComboBox.currentText()
        self.daq._SAMPLE_POWER_METER_RANGE = self.powerMeterSRangeComboBox.currentText()
        self.daq._REFERENCE_POWER_METER_RANGE = self.powerMeterRRangeComboBox.currentText()
        self.daq._APD1_GAIN = self.apd1GainComboBox.currentText()
        self.daq._APD1_DETECTION_WAVELENGTH = self.apd1DetectionWavelengthSpinBox.text()
        self.daq._APD2_GAIN = self.apd2GainComboBox.currentText()
        self.daq._APD2_DETECTION_WAVELENGTH = self.apd2DetectionWavelengthSpinBox.text()

        self.daq._NOTES = self.notesTextBox.toPlainText().replace(' ', '').replace('\n', '/')

        self.daq._outputArr = np.arange(
            self.daq._RANGE_START, self.daq._RANGE_END, self.daq._STEP_SIZE)
        if self.daq._STEP_RESET:
            tempArr = np.delete(self.daq._outputArr,
                                np.where(self.daq._outputArr == 0))
            self.daq._outputArr = np.zeros(2 * tempArr.size)
            self.daq._outputArr[1::2] = tempArr

    # get info method called when form is accepted
    def getInfo(self):

        # printing the form information
        print(f"{self.laserChannelComboBox.currentText()=}")
        print(f"{self.laserLineComboBox.currentText()=}")
        print(f"{self.beamSpotComboBox.currentText()=}")
        print(f"{self.powerMeterSChannelComboBox.currentText()=}")
        print(f"{self.powerMeterSRangeComboBox.currentText()=}")
        print(f"{self.powerMeterRChannelComboBox.currentText()=}")
        print(f"{self.powerMeterRRangeComboBox.currentText()=}")
        print(f"{self.apd1ChannelComboBox.currentText()=}")
        print(f"{self.apd1GainComboBox.currentText()=}")
        print(f"{self.apd1DetectionWavelengthSpinBox.text()=}")
        print(f"{self.apd2ChannelComboBox.currentText()=}")
        print(f"{self.apd2GainComboBox.currentText()=}")
        print(f"{self.apd2DetectionWavelengthSpinBox.text()=}")
        print(f"{self.feedbackChannelComboBox.currentText()=}")
        print(f"{self.laserStartSpinBar.text()=}")
        print(f"{self.laserEndSpinBar.text()=}")
        print(f"{self.laserStepSpinBar.text()=}")
        print(f"{self.samplingSpinBar.text()=}")
        print(f"{self.timingSpinBar.text()=}")
        print(f"{self.pulsedCheckBox.isChecked()=}")
        print(f"{self.sampleLineEdit.text()=}")
        print(f"{self.referenceLineEdit.text()=}")
        print(f"{self.notesTextBox.toPlainText()=}")

        self.setDaqConfig()
        # self.daq.run()
        self.saveButton.setEnabled(True)
        self.daq.updatelog()
        # n = 2 if self.pulsedCheckBox.isChecked() else 5
        self.plot(self.daq)

    def plot(self, daq):
        pass

    # create form method
    def createForm(self):

        # creating a form layout
        layout = QFormLayout()

        # adding rows
        # for name and adding input text
        laserLabel = QLabel("Laser (?)")
        laserLabel.setToolTip(
            'Laser settings: Set the power range to sweep')
        layout.addRow(laserLabel)
        layout.addRow(QLabel("Channel"), self.laserChannelComboBox)
        layout.addRow(QLabel("Line"), self.laserLineComboBox)
        layout.addRow(QLabel("Beam spot"), self.beamSpotComboBox)

        powerMeterSLabel = QLabel("Power Meter - S (?)")
        powerMeterSLabel.setToolTip(
            'Power Meter connected to the cuvette holder with the sample')
        layout.addRow(powerMeterSLabel)
        layout.addRow(QLabel("Channel"), self.powerMeterSChannelComboBox)
        layout.addRow(QLabel("Range"), self.powerMeterSRangeComboBox)

        powerMeterRLabel = QLabel("Power Meter - R (?)")
        powerMeterRLabel.setToolTip(
            'Power Meter connected to the cuvette holder with the reference')
        layout.addRow(powerMeterRLabel)
        layout.addRow(QLabel("Channel"), self.powerMeterRChannelComboBox)
        layout.addRow(QLabel("Range"), self.powerMeterRRangeComboBox)

        apd1Label = QLabel("APD1 (?)")
        apd1Label.setToolTip(
            'APD1')
        layout.addRow(apd1Label)
        layout.addRow(QLabel("Channel"), self.apd1ChannelComboBox)
        layout.addRow(QLabel("Gain"), self.apd1GainComboBox)
        layout.addRow(QLabel("Wavelength"),
                      self.apd1DetectionWavelengthSpinBox)

        apd2Label = QLabel("APD2 (?)")
        apd2Label.setToolTip(
            'APD2')
        layout.addRow(apd2Label)
        layout.addRow(QLabel("Channel"), self.apd2ChannelComboBox)
        layout.addRow(QLabel("Gain"), self.apd2GainComboBox)
        layout.addRow(QLabel("Wavelength"),
                      self.apd2DetectionWavelengthSpinBox)

        controlAndAcquisitionLabel = QLabel("Control and Acquisition (?)")
        controlAndAcquisitionLabel.setToolTip(
            'Set the laser modulation and acquisition settings')
        layout.addRow(controlAndAcquisitionLabel)

        layout.addRow(QLabel("Feedback"), self.feedbackChannelComboBox)
        layout.addRow(QLabel("Start"), self.laserStartSpinBar)
        layout.addRow(QLabel("End"), self.laserEndSpinBar)
        layout.addRow(QLabel("Step"), self.laserStepSpinBar)
        layout.addRow(QLabel("Samples per step"), self.samplingSpinBar)
        layout.addRow(QLabel("Time per step"), self.timingSpinBar)

        layout.addRow(QLabel("Pulse"), self.pulsedCheckBox)

        layout.addRow(QLabel("Sample"), self.sampleLineEdit)
        layout.addRow(QLabel("Reference"), self.referenceLineEdit)
        # layout.addRow(QLabel("Attenuation"))
        layout.addRow(QLabel("Notes"), self.notesTextBox)

        self.formGroupBox.setLayout(layout)


# # main method
# if __name__ == '__main__':

#     # create pyqt5 app
#     app = QApplication(sys.argv)

#     # create the instance of our Window
#     window = SettingsForm()

#     # showing the window
#     window.show()

#     # start the app
#     sys.exit(app.exec())

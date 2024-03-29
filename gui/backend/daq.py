import json
from datetime import datetime
import time
import numpy as np
import nidaqmx as mx
import nidaqmx.system
from nidaqmx.constants import (
    AcquisitionType,
    READ_ALL_AVAILABLE
)
import getpass
import pandas as pd


class Controller():
    """
    """
    debug = False
    _daqdata = pd.DataFrame()
    _clock = {}
    _data = pd.DataFrame({
        'time': [0, 1, 2, 3, 4, 5],
        0: [0, 1, 2, 3, 4, 5],
        1: [0, 11, 22, 31, 41, 51],
        2: [10, 1, 22, 3, 4, 5],
        3: [0, 1, 2, 3, 42, 5],
        4: [20, 1, 22, 3, 4, 5],
    })
    _nChannels = 3
    _config = {}
    _appDetails = {}

    # Channels
    _OUT_CHANNEL = ['ao0']
    _IN_CHANNELS = ['ai0', 'ai1', 'ai2']

    # Ramping
    _RANGE_START = 0.0  # V
    _RANGE_END = 1.0  # V
    _STEP_SIZE = 0.1  # V
    _STEP_RESET = False  # resets the step to 0 before moving to next one
    _TIME_PER_STEP = 0.1  # s

    # DAQ uses this to calculate the buffer size
    _INTERNAL_SAMPLES_PER_CH = 100

    # I guess this should be lesser than _INTERNAL_SAMP_PER_CH,
    # otherwise the driver will try to read more samples than available
    # in the buffer
    # Reading Parameters
    _SAMPLES_PER_CH_TO_READ = READ_ALL_AVAILABLE
    _SAMPLING_RATE = _INTERNAL_SAMPLES_PER_CH / _TIME_PER_STEP
    _MIN_READING_VAL = -5.0
    _MAX_READING_VAL = 5.0

    _SAMPLE = ""
    _REFERENCE = ""
    _EXCITATION_WAVELENGTH = ""  # nm
    _BEAM_SPOT = ""
    _SAMPLE_POWER_METER_RANGE = ""
    _REFERENCE_POWER_METER_RANGE = ""
    _APD1_GAIN = ""  # Min or Max
    _APD1_DETECTION_WAVELENGTH = ""  # nm
    _APD2_GAIN = ""  # Min or Max
    _APD2_DETECTION_WAVELENGTH = ""  # nm

    _NOTES = ""

    def __init__(self, parent=None):
        """Initialize data and clock variables
        """

        with open('../docs/.software.json', 'r') as f:
            self._appDetails = json.load(f)

        self._daqdata = pd.DataFrame({key: []
                                      for key in range(self._nChannels)})

        self._clock = {'time': []}
        self._log = self._createlog()
        # pl.close()

        system = nidaqmx.system.System.local()
        try:
            self.devices = list(system.devices)
            for dev in self.devices:
                print(dev)
        except:
            self.devices = []
            print('No device found...')

        if self.debug:
            self.devices = ['dev1']
            self.run = self.runTest

    def _createlog(self):
        """ Creates dataframe to log the experimental details
        """
        return (pd.DataFrame(columns=[
            'exp_id', 'saved_name', 'out_ch', 'range_start', 'range_end', 'range_step_size',
            'pulsed', 'in_chs', 'time_per_step', 'samples_per_ch', 'sampling_rate',
            'min_reading_val', 'max_reading_val', 'samples_per_ch_to_read',
            'sample', 'reference',
            'excitation_wavelength', 'beam_spot',
            'pms_range', 'pmr_range',
            'apd1_gain', 'apd1_wavelength',
            'apd2_gain', 'apd2_wavelength',
            'notes', 'user', 'app_version'
        ]))

    def isdatasaved(self):
        """Checks if last collected data is saved.
        If log is empty means that the data was already saved and log was cleaned up.
        """
        return (self._log.empty)

    def updateProgress(self, value):
        pass

    def runTest(self):
        runningProgress = 0
        while runningProgress < 100:
            runningProgress += 100 / len(self._outputArr)
            time.sleep(0.1)
            self.updateProgress(runningProgress)
        runningProgress = 100.0
        self.updateProgress(runningProgress)

    def run(self):
        """Run method set to collect data at every N samples. 
        Time column gives the time when the samples were collected and 
        is measured locally with Python from the OS clock.
        To evaluate the time that the DAQ takes to start the task
        run the experiment with two samples with the following settings:
            **self._RANGE_START** 0.,
            **self._RANGE_END** = 1.,
            **self._STEP_SIZE** = 1.,
            **self._INTERNAL_SAMPLES_PER_CH** = 1
        """

        # Get params from config file
        # self._xpconfig()
        # reset data
        self._daqdata = pd.DataFrame({key: []
                                      for key in range(self._nChannels)})
        self._clock = {'time': []}

        taskMaster = mx.Task('Master')
        taskMaster.ao_channels.add_ao_voltage_chan(
            f'Dev1/{self._OUT_CHANNEL[0]}')

        # Slave perform readings
        taskSlave = mx.Task('Slave')
        # Add channels to slave
        taskSlave.ai_channels.add_ai_voltage_chan(
            f'Dev1/ai{self._IN_CHANNELS[0][-1]}:{self._IN_CHANNELS[-1][-1]}',
            min_val=self._MIN_READING_VAL, max_val=self._MAX_READING_VAL
        )

        taskSlave.timing.cfg_samp_clk_timing(
            rate=self._SAMPLING_RATE,
            sample_mode=AcquisitionType.CONTINUOUS,
            samps_per_chan=self._INTERNAL_SAMPLES_PER_CH  # buffer size
        )

        self.runningProgress = 0
        self.updateProgress(self.runningProgress)
        def callback(task_handle, every_n_samples_event_type,
                     number_of_samples, callback_data):

            self._clock['time'].append(time.time_ns())
            self._daqdata = pd.concat([
                self._daqdata,
                pd.DataFrame(
                    taskSlave.read(
                        number_of_samples_per_channel=number_of_samples)
                ).T
            ])
            self.runningProgress += 100 / len(self._outputArr)
            self.updateProgress(self.runningProgress)

            # write next value to output if it is within the range
            if self._outputArr.any():
                taskMaster.write([self._outputArr[0]])
                self._outputArr = np.delete(self._outputArr, 0)
            else:
                print('Stop')
                taskSlave.stop()

            return 0


        taskSlave.register_every_n_samples_acquired_into_buffer_event(
            self._INTERNAL_SAMPLES_PER_CH, callback)

        taskMaster.write([self._outputArr[0]])
        self._outputArr = np.delete(self._outputArr, 0)
        t0 = time.time_ns()  # acquire initial t in ns
        taskSlave.start()

        while self.runningProgress < 100:
            # wait until it's done
            # allow the daq to process the routine before it moves to next step
            time.sleep(0.001)

        taskSlave.stop()
        taskSlave.close()

        taskMaster.write([0.0])
        taskMaster.stop()
        taskMaster.close()

        self._daqdata.reset_index(drop=True, inplace=True)
        # arrange time to DataFrame
        # change this if self._SAMPLES_PER_CH_TO_READ is set to something different than READ_ALL_AVAILABLE
        self._clock = pd.DataFrame(
            self._clock,
            index=self._daqdata.iloc[self._INTERNAL_SAMPLES_PER_CH -
                                     1::self._INTERNAL_SAMPLES_PER_CH].index
        )

        # set initial to zero
        self._clock.loc[0, 'time'] = t0
        self._clock['time'] -= self._clock['time'][0]
        self._clock['time'] /= 10**(9)  # convert to seconds

        # concat clock and daqdata
        self._data = pd.concat([self._clock, self._daqdata], axis=1)

        # linear interpolation // it doesn't consider the 0.02 s between the tasks.
        self._data['time'].interpolate(inplace=True)

        # include details to log
        self.updatelog()

        self.runningProgress = 100.0
        self.updateProgress(self.runningProgress)

        print('Done!')

    def data(self):
        """Returns the consolidate data with time attached
        """
        return (self._data)

    def updatelog(self):
        """updatelog() logs last parameters and attributes a id to it.
        """
        now = datetime.now().strftime('%Y%m%d-%H%M%S')
        log = pd.DataFrame(columns=self._log.columns, index=[0])

        log['exp_id'] = now
        log['out_ch'] = '/'.join([
            f"{ch}={self._config['Channels'][ch]}" for ch in self._OUT_CHANNEL
        ])

        log['range_start'] = self._RANGE_START
        log['range_end'] = self._RANGE_END
        log['range_step_size'] = self._STEP_SIZE
        log['pulsed'] = self._STEP_RESET
        log['in_chs'] = '/'.join([
            f"{ch}={self._config['Channels'][ch]}" for ch in self._IN_CHANNELS
        ])
        log['time_per_step'] = self._TIME_PER_STEP
        log['samples_per_ch'] = self._INTERNAL_SAMPLES_PER_CH
        log['sampling_rate'] = self._SAMPLING_RATE
        log['min_reading_val'] = self._MIN_READING_VAL
        log['max_reading_val'] = self._MAX_READING_VAL
        log['samples_per_ch_to_read'] = 'READ_ALL_AVAILABLE' \
            if self._SAMPLES_PER_CH_TO_READ == -1 else self._SAMPLES_PER_CH_TO_READ

        log['sample'] = self._SAMPLE
        log['reference'] = self._REFERENCE
        log['excitation_wavelength'] = self._EXCITATION_WAVELENGTH
        log['beam_spot'] = self._BEAM_SPOT
        log['pms_range'] = self._SAMPLE_POWER_METER_RANGE
        log['pmr_range'] = self._REFERENCE_POWER_METER_RANGE
        log['apd1_gain'] = self._APD1_GAIN
        log['apd1_wavelength'] = self._APD1_DETECTION_WAVELENGTH
        log['apd2_gain'] = self._APD2_GAIN
        log['apd2_wavelength'] = self._APD2_DETECTION_WAVELENGTH

        log['notes'] = self._NOTES
        log['user'] = getpass.getuser()
        log['app_version'] = f"{self._appDetails['name']}-v{self._appDetails['version']}"

        self._log = pd.concat([self._log, log]).reset_index(drop=True)

    def savelog(self):
        """
        savelog() updates log file with all experiment details, including the ones not saved.
        """
        # check if file already exists and have same structure
        logfilePath = '../data/datalogs.csv'
        print(logfilePath)
        if not self._log.empty:
            try:
                # open existing log file
                savedLog = pd.read_csv(logfilePath)
                # concat and save
                pd.concat([savedLog, self._log]).to_csv(
                    logfilePath, index=False)

            except FileNotFoundError:
                print(f'Unable to find file: {logfilePath}...\n',
                      "Relax, I'll try to create it for you!"
                      )
                self._log.to_csv(logfilePath, index=False)

            print(f'Data logs file saved to: {logfilePath}')
        else:
            print("Empty log...")
        # reset log
        self._log = self._createlog()

    def save(self):
        """
        Save data to csv file and updates logfile
        """
        if not self._data.empty:
            if not self.isdatasaved():
                # gets exp id from last row of log
                expId = self._log.loc[self._log.shape[0] -
                                      1, 'exp_id'].replace('-', '_')
                fileName = f'../data/raw-data/qy_{expId}.csv'
                self._data.to_csv(fileName)
                print(f'Data saved to: {fileName}')

                # updates log before saving
                self._log.loc[self._log.shape[0] - 1, 'saved_name'] = fileName
                self.savelog()
            else:
                print('Data already saved...')
        else:
            print('No data to save...')

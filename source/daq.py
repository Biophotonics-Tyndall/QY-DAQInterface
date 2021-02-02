import nidaqmx as mx
from nidaqmx.constants import (
    AcquisitionType,
    READ_ALL_AVAILABLE
)
import configparser
import getpass
import os
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
# matplotlib.use('Agg') # Not a GUI backend
# matplotlib.use('Qt5Agg') # Need installation
import matplotlib.pyplot as pl
import numpy as np
import time
from datetime import datetime
from tqdm import tqdm
import json

class Controler():
    """
    """
    debug = False
    _daqdata = pd.DataFrame()
    _clock = {}
    _data = pd.DataFrame()
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
    _STEP_RESET = False # resets the step to 0 before moving to next one
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


    def __init__(self):
        """Initialize data and clock variables
        """
        with open('./docs/.software.json', 'r') as f:
            self._appDetails = json.load(f)

        self._xpconfig()

        self._daqdata = pd.DataFrame({key: []
                                      for key in range(self._nChannels)})

        self._clock = {'time': []}
        self._log = self._createlog()
        pl.close()
        if self.debug:
            fileName = './data/raw-data/qy_ddmmyy_hms.csv'
            self._data = pd.read_csv(fileName, usecols=[1, 2, 3, 4])
            self._data.columns = ['time', 0, 1, 2]
            self._log.loc[0] = ['test'] * self._log.shape[1]

    def status(self):
        """Returns message regarding data:
            1. No data to be saved
            2. Last measurement not saved
        """
        if self.isdatasaved():
            return('No data to be saved...')
        else: return('Data not saved...') 

    def _createlog(self):
        """ Creates dataframe to log the experimental details
        """
        return(pd.DataFrame(columns=[
            'exp_id', 'saved_name', 'out_ch', 'range_start', 'range_end', 'range_step_size',
            'step_reset', 'in_chs', 'time_per_step', 'samples_per_ch', 'sampling_rate',
            'min_reading_val', 'max_reading_val', 'samples_per_ch_to_read',
            'extra_params', 'user', 'app_version'
        ]))

    def isdatasaved(self):
        """Checks if last collected data is saved.
        If log is empty means that the data was already saved and log was cleaned up.
        """
        return(self._log.empty)

    def _xpconfig(self):
        """
        _get_xpconfig()
        Gets and sets experiment parameters from external .txt file.
        """
        self._config = configparser.ConfigParser()
        self._config.read("config.txt")

        # Set channels
        self._OUT_CHANNEL = [ch.strip().replace(' ', '')
                             for ch in list(self._config['Channels']) if ch[1] == 'o']
        self._IN_CHANNELS = sorted([ch.strip().replace(
            ' ', '') for ch in list(self._config['Channels']) if ch[1] == 'i'])
        self._nChannels = len(self._IN_CHANNELS)

        # Set power range
        self._RANGE_START = float(self._config['Laser']['start'])
        self._RANGE_END = float(self._config['Laser']['end'])
        self._STEP_SIZE = float(self._config['Laser']['step size'])
        self._STEP_RESET = True if self._config['Laser']['reset'] == 'yes' else False

        # Set timing
        self._TIME_PER_STEP = float(self._config['Timing']['time per step'])

        # Set sampling
        self._INTERNAL_SAMPLES_PER_CH = int(
            self._config['Sampling']['samples per channel per step'])
        self._SAMPLING_RATE = self._INTERNAL_SAMPLES_PER_CH / self._TIME_PER_STEP
        self._MIN_READING_VAL = float(self._config['Sampling']['min voltage'])
        self._MAX_READING_VAL = float(self._config['Sampling']['max voltage'])

        self._outputArr = np.arange(self._RANGE_START, self._RANGE_END, self._STEP_SIZE)
        if self._STEP_RESET:
            tempArr = np.delete(self._outputArr, np.where(self._outputArr==0))
            self._outputArr = np.zeros(2 * tempArr.size)
            self._outputArr[1::2] = tempArr

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
        self._xpconfig()
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

        # Configure the DAQ internal clock
        # samps_per_chan (Optional[long]): Specifies the number of
        #         samples to acquire or generate for each channel in the
        #         task if **sample_mode** is **FINITE_SAMPLES**. If
        #         **sample_mode** is **CONTINUOUS_SAMPLES**, NI-DAQmx uses
        #         this value to determine the buffer size.
        # access the sample_mode by:
        # print(taskSlave.timing.samp_quant_samp_mode)
        taskSlave.timing.cfg_samp_clk_timing(
            rate=self._SAMPLING_RATE,
            sample_mode=AcquisitionType.CONTINUOUS,
            samps_per_chan=self._INTERNAL_SAMPLES_PER_CH # buffer size
        )

        def callback(task_handle, every_n_samples_event_type,
                    number_of_samples, callback_data):

            # samples = task.read(number_of_samples_per_channel=200)
            # t = time.time_ns()
            self._clock['time'].append(time.time_ns())
            self._daqdata = pd.concat([
                self._daqdata,
                pd.DataFrame(
                    taskSlave.read(
                        number_of_samples_per_channel=number_of_samples)
                ).T
            ])
            pbar.update(number_of_samples)
            # write next value to output if it is within the range
            if self._outputArr.any():
                taskMaster.write([self._outputArr[0]])
                self._outputArr = np.delete(self._outputArr, 0)
            else:
                taskSlave.stop()
                pbar.close()

            # dt = (t - t0) / 10 ** 6 # convert ns to ms
            # print(f'{number_of_samples} samples in {dt:.3f}', end='\r')
            return 0

        # self._outputArr = np.arange(self._RANGE_START, self._RANGE_END, self._STEP_SIZE)


        taskSlave.register_every_n_samples_acquired_into_buffer_event(
            self._INTERNAL_SAMPLES_PER_CH, callback)

        # define progress bar
        pbar = tqdm(
            total=len(self._outputArr) * self._INTERNAL_SAMPLES_PER_CH,
            desc='Acquiring', unit='samples', position=0,
        )
        
        taskMaster.write([self._outputArr[0]])
        self._outputArr = np.delete(self._outputArr, 0)
        t0 = time.time_ns() # acquire initial t in ns
        taskSlave.start()

        os.system('cls' if os.name == 'nt' else 'clear')
        input('Task running... Press ENTER to stop.\n')

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
            index=self._daqdata.iloc[self._INTERNAL_SAMPLES_PER_CH-1::self._INTERNAL_SAMPLES_PER_CH].index
        )

        # set initial to zero
        self._clock.loc[0, 'time'] = t0
        self._clock['time'] -= self._clock['time'][0]
        self._clock['time'] /= 10**(9) # convert to seconds 

        # concat clock and daqdata
        self._data = pd.concat([self._clock, self._daqdata], axis=1)

        # linear interpolation // it doesn't consider the 0.02 s between the tasks.
        self._data['time'].interpolate(inplace=True)

        # include details to log
        self.updatelog()

        print('Done!')

    def run_(self):
        """
        run() is the core of the class.
            - It calls the experiment confg
            - Starts the tasks
            - Runs the routines and stores internally the data
        """
        # reset data
        self._xpconfig()
        self._daqdata = pd.DataFrame({key: []
                                      for key in range(self._nChannels)})
        self._clock = {'time': []}

        # Start tasks and add channels
        # Master modulates the laser
        taskMaster = mx.Task('Master')
        taskMaster.ao_channels.add_ao_voltage_chan(
            f'Dev1/{self._OUT_CHANNEL[0]}')

        # Slave perform readings
        taskSlave = mx.Task('Slave')
        # Add channels to slave
        taskSlave.ai_channels.add_ai_voltage_chan(
            f'Dev1/ai{self._IN_CHANNELS[0][-1]}:{self._IN_CHANNELS[-1][-1]}')

        # Configure the DAQ internal clock
        # samps_per_chan (Optional[long]): Specifies the number of
        #         samples to acquire or generate for each channel in the
        #         task if **sample_mode** is **FINITE_SAMPLES**. If
        #         **sample_mode** is **CONTINUOUS_SAMPLES**, NI-DAQmx uses
        #         this value to determine the buffer size.
        # access the sample_mode by:
        # print(taskSlave.timing.samp_quant_samp_mode)
        taskSlave.timing.cfg_samp_clk_timing(
            rate=self._SAMPLING_RATE,
            sample_mode=AcquisitionType.FINITE,
            samps_per_chan=self._INTERNAL_SAMPLES_PER_CH
        )

        # array with all steps linear arranged in a numpy array
        self._outputArr = np.arange(
            self._RANGE_START, self._RANGE_END, self._STEP_SIZE)

        # There's a faster way to do this ramping using a callback function
        # Switching tasks on and off consumes time (~ 0.02 s)
        for val in tqdm(self._outputArr, desc='Ramping.. '):

            # acquire time
            self._clock['time'].append(time.time_ns() / 10 ** 9)
            # set voltage output
            taskMaster.write([val], auto_start=True)
            taskMaster.stop()
            # self._clock['time1'].append(time.time_ns() / 10 ** 9)

            # read and concat to previous data
            self._daqdata = pd.concat([
                self._daqdata,
                pd.DataFrame(
                    taskSlave.read(
                        number_of_samples_per_channel=self._SAMPLES_PER_CH_TO_READ)
                ).T
            ])
            taskSlave.stop()
            # self._clock['time2'].append(time.time_ns() / 10 ** 9)

        taskMaster.write([0.0], auto_start=True)
        taskMaster.close()
        taskSlave.close()

        self._daqdata.reset_index(drop=True, inplace=True)
        # arrange time to DataFrame
        # change this if self._SAMPLES_PER_CH_TO_READ is set to somthing different than READ_ALL_AVAILABLE
        self._clock = pd.DataFrame(
            self._clock,
            index=self._daqdata.iloc[::self._INTERNAL_SAMPLES_PER_CH].index
        )

        # set initial to zero
        self._clock['time'] -= self._clock['time'][0]

        # concat clock and daqdata
        self._data = pd.concat([self._clock, self._daqdata], axis=1)

        # linear inerpolation // it doesn't consider the 0.02 s between the tasks.
        self._data['time'].interpolate(inplace=True)

        # include details to log
        self.updatelog()

        print('Done!')

    def data(self):
        """Returns the consolidate data with time attached
        """
        return(self._data)

    def updatelog(self):
        """updatelog() logs last parameters and attributes a id to it.
        """
        now = datetime.now().strftime('%Y%m%d-%H%M%S')
        log = pd.DataFrame(columns=self._log.columns, index=[0])

        log['exp_id'] = now
        # log['out_ch'] = self._OUT_CHANNEL[0]
        log['out_ch'] = '/'.join([
            f"{ch}={self._config['Channels'][ch]}" for ch in self._OUT_CHANNEL
        ])

        log['range_start'] = self._RANGE_START
        log['range_end'] = self._RANGE_END
        log['range_step_size'] = self._STEP_SIZE
        log['step_reset'] = self._STEP_RESET
        # log['in_chs'] = ' '.join(self._IN_CHANNELS)
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
        log['extra_params'] = '/'.join([
            f"{k}={self._config['Extra Parameters'][k]}" for k in self._config['Extra Parameters']
        ])
        log['user'] = getpass.getuser()
        log['app_version'] = f"{self._appDetails['name']}-v{self._appDetails['version']}"

        self._log = pd.concat([self._log, log]).reset_index(drop=True)

    def savelog(self):
        """
        savelog() updates log file with all experiment details, including the ones not saved.
        """
        # check if file already exists and have same structure
        logfilePath = './data/datalogs.csv'

        if not self._log.empty:
            try:
                # open existing log file
                savedLog = pd.read_csv(logfilePath)
                # concat and save
                pd.concat([savedLog, self._log]).to_csv(logfilePath, index=False)

            except FileNotFoundError:
                print(f'Unable to find file: {logfilePath}...\n',
                    "Relax, I'll try to create it for you!"
                    )
                self._log.to_csv(logfilePath, index=False)

            print(f'Data logs file saved to: {logfilePath}')

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
                fileName = f'./data/raw-data/qy_{expId}.csv'
                self._data.to_csv(fileName)
                print(f'Data saved to: {fileName}')

                # updates log before saving
                self._log.loc[self._log.shape[0] - 1, 'saved_name'] = fileName
                self.savelog()
            else:
                print('Data already saved...')
        else: print('No data to save...')

    def initializeplotgui(self):
        """Initialize matplotlib figure and axes interface.
        """
        # Get configs dynamically without the need to run the experiment again
        # in order to update the plot settings
        dynamConfig = configparser.ConfigParser()
        dynamConfig.read("config.txt")
        gConfig = dynamConfig['Graph Settings']
        pl.rcParams.update({'font.size': float(gConfig['font size'])})
        # 1 subplot per channel
        self._fig, self._axs = pl.subplots(self._nChannels, sharex=True,
                                    figsize=[
                                        float(i) for i in gConfig['graph size'].split(',')]
                                    )
        self._axs[-1].set_xlabel('Time (s)')

        pl.ion()

    def plot(self):
        """
        Plots the data from channels vs time
        """
        
        if not self._data.empty:
            if pl.get_fignums() == []:
                self.initializeplotgui()
            dynamConfig = configparser.ConfigParser()
            dynamConfig.read("config.txt")
            gConfig = dynamConfig['Graph Settings']
            cConfig = self._config['Channels']
            extraPConfig = self._config['Extra Parameters']

            self._axs[0].set_title(gConfig['title'])
            if self._axs[0].lines:
                action = input('Overwrite data? [y or press enter]: ')
                if action == 'y':
                    for n in range(self._nChannels): 
                        self._axs[n].lines = []
            for n in range(self._nChannels):
                label = extraPConfig[gConfig['label']] if gConfig['label'] in extraPConfig else gConfig['label']
                self._axs[n].plot(self._data['time'], self._data[n], label=label,
                            marker=gConfig['marker'],
                            ms=float(gConfig['marker size']),
                            color=gConfig['colour'],
                            alpha=float(gConfig['alpha']),
                            linestyle=gConfig['line style'],
                            lw=float(gConfig['line width'])
                            )
                self._axs[n].legend(title=f"Ch.{n}: {cConfig[self._IN_CHANNELS[n]]}")
                self._axs[n].set_ylabel('Input (V)')
                self._axs[n].grid(gConfig['grid'])

            self._fig.tight_layout()
            self._fig.show()
            print('Data plotted...')
        else:
            print('No data to plot...')

import nidaqmx as mx
from nidaqmx.constants import (
    AcquisitionType,
    READ_ALL_AVAILABLE
)
import configparser
import pandas as pd
import matplotlib.pyplot as pl
import numpy as np
import time


class Controler():
    _daqdata = {}
    _clock = {}
    _data = {}
    _RANGE_START = 0.0 # V
    _RANGE_END = 1.0 # V
    _STEP_SIZE = 0.1 # V
    _TIME_PER_STEP = 0.1 # s

    # DAQ uses this to calculate the buffer size
    _INTERNAL_SAMPLES_PER_CH = 100 

    # I guess this should be lesser than _INTERNAL_SAMP_PER_CH, 
    # otherwise the driver will try to read more samples than available 
    # in the buffer
    _SAMPLES_PER_CH_TO_READ = READ_ALL_AVAILABLE 
    _SAMPLING_RATE = _INTERNAL_SAMPLES_PER_CH / _TIME_PER_STEP

    def __init__(self):
        """Initialize data and clock variables
        """
        self._daqdata = pd.DataFrame({0: [], 1:[], 2: [], 3: []})
        self._clock = {'time': []}
        
    def _xpconfig(self):
        """
        _get_xpconfig()
        Gets and sets experiment parameters from external .ini file.
        """
        config = configparser.ConfigParser()
        config.read("measurement_config.txt")
        
        # Set power range
        self._RANGE_START = float(config['Laser']['start'])
        self._RANGE_END = float(config['Laser']['end'])
        self._STEP_SIZE = float(config['Laser']['step size'])
        
        # Set timing
        self._TIME_PER_STEP = float(config['Timing']['time per step'])
        
        # Set sampling
        self._INTERNAL_SAMPLES_PER_CH = int(config['Sampling']['samples per channel per step'])
        self._SAMPLING_RATE = self._INTERNAL_SAMPLES_PER_CH / self._TIME_PER_STEP

    def run(self):
        """
        run() is the core of the class.
            - It calls the experimentals params
            - Starts the tasks
            - Runs the routines and stores internaly the data
        """        
        # reset data
        self._daqdata = pd.DataFrame({0: [], 1:[], 2: [], 3: []})
        self._clock = {'time': []}
        self._xpconfig()


        # Start tasks and add channels
        # Master modulates the laser
        taskMaster = mx.Task('Master')
        taskMaster.ao_channels.add_ao_voltage_chan('Dev1/ao0')

        # Slave perform readings
        taskSlave = mx.Task('Slave')
        # Add channels to slave
        taskSlave.ai_channels.add_ai_voltage_chan('Dev1/ai0:3')
        
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
        outputArr = np.arange(self._RANGE_START, self._RANGE_END, self._STEP_SIZE)

        # There's a faster way to do this ramping using a callback function
        # Switching tasks on and off consumes time (~ 0.02 s)
        for val in outputArr:

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
                    taskSlave.read(number_of_samples_per_channel=self._SAMPLES_PER_CH_TO_READ)
                ).T
            ])
            taskSlave.stop()
            # self._clock['time2'].append(time.time_ns() / 10 ** 9)

        taskMaster.write([0.0], auto_start=True)
        taskMaster.close()
        taskSlave.close()

        self._daqdata.reset_index(inplace=True)
        # arrange time to DataFrame
        # change this if self._SAMPLES_PER_CH_TO_READ is set to somthing different than READ_ALL_AVAILABLE
        self._clock = pd.DataFrame(
            self._clock,
            index=self._daqdata.iloc[::self._INTERNAL_SAMPLES_PER_CH].index
        )
        
        # concat clock and daqdata
        self._data = pd.concat([self._clock, self._daqdata], axis=1)
        
        # linear inerpolation // it doesn't consider the 0.02 s between the tasks.
        self._data['time'].interpolate(inplace=True)

        print('Done!')

    def data(self):
        """
        """
        return(self._data)

    def save(self):
        """
        docstring
        """
        pass

    def plot(self):
        """
        docstring
        """
        # plot results
        # pl.ion()
        mrkr = ['o', 'v', 's', '>']
        for i in range(4):
            pl.plot(self._data.index, self._data[i], label=f'Channel: {i}',
                marker=mrkr[i], alpha=.5, linestyle='')

        """ 
        pl.plot(data.iloc[::SAMPLES_PER_CH].index, np.asarray(timeBeforeTask) - timeBeforeTask[0], label='Time B4 task', marker='<')
        pl.plot(data.iloc[::SAMPLES_PER_CH].index, np.asarray(timeAfterTask) - timeBeforeTask[0], label='Time after task', marker='>')
        pl.legend()
        pl.xlabel('Acquisition #')
        pl.ylabel('Time (s)')
        """

        pl.rcParams.update({'font.size': 18})
        pl.legend()
        pl.xlabel('Acquisition #')
        pl.ylabel('Output (V)')
        pl.show()


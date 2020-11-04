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
    _rawdata = {}
    _clock = {}
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
        self._rawdata = pd.DataFrame({0: [], 1:[], 2: [], 3: []})
        self._clock = {'stopwatch': []}
        
    def _xpconfig(self):
        """
        _get_xpconfig()
        Gets and sets experiment parameters from external .ini file.
        """
        config = configparser.ConfigParser()
        config.read("measurement_config.txt")
        
        # Set power range
        self._RANGE_START = config['Laser']['start']
        self._RANGE_END = config['Laser']['end']
        self._STEP_SIZE = config['Laser']['step size']
        
        # Set timing
        self._TIME_PER_STEP = config['Timing']['time per step']
        
        # Set sampling
        self._INTERNAL_SAMPLES_PER_CH = config['Sampling']['samples per channel per step']

    def run(self):
        """
        run() is the core of the class.
            - It calls the experimentals params
            - Starts the tasks
            - Runs the routines and stores internaly the data
        """        
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
            self._clock['stopwatch'].append(time.time_ns() / 10 ** 9)
            # set voltage output
            taskMaster.write([val], auto_start=True)
            taskMaster.stop()
            # self._clock['stopwatch1'].append(time.time_ns() / 10 ** 9)

            # read and concat to previous data
            self._rawdata = pd.concat([
                self._rawdata,
                pd.DataFrame(
                    taskSlave.read(number_of_samples_per_channel=self._SAMPLES_PER_CH_TO_READ)
                ).T
            ])
            taskSlave.stop()
            # self._clock['stopwatch2'].append(time.time_ns() / 10 ** 9)

            # dataDc['0'] += data[0]
            # dataDc['1'] += data[1]
            # dataDc['2'] += data[2]
            # dataDc['3'] += data[3]

        taskMaster.write([0.0], auto_start=True)
        taskMaster.close()
        taskSlave.close()
        self._rawdata.reset_index(inplace=True)
        print('Done!')


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
            pl.plot(self._rawdata.index, self._rawdata[i], label=f'Channel: {i}',
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

    def data(self):
        """
        """
        return(self._rawdata)


# # Set initial params
# # Debug
# debugging = False
# dataDc = {'0': [], '1':[], '2': [], '3': []}

# # GLOBAL PARAMS
# STARTING_RANGE = 0.0 # V
# ENDING_RANGE = 5.0 # V
# STEPS_SIZE = 0.1 # V
# TIME_PER_STEP = 0.1 # s

# # DAQ uses this to calculate the buffer size
# INTERNAL_SAMPLES_PER_CH = 100 

# # I guess it should be lesser than INTERNAL_SAMPLES_PER_CH, 
# # otherwise the driver will try to read more samples than available 
# # in the buffer
# SAMPLES_PER_CH_TO_READ = READ_ALL_AVAILABLE 
# # DELAY_TO_START_ACQUIS = 0.0 # s

# SAMPLING_RATE = INTERNAL_SAMPLES_PER_CH / TIME_PER_STEP

# # start tasks and add channels
# taskMaster = mx.Task('Master')
# taskMaster.ao_channels.add_ao_voltage_chan('Dev1/ao0')

# taskSlave = mx.Task('Slave')

# # Configure the DAQ internal clock
# # samps_per_chan (Optional[long]): Specifies the number of  
# #         samples to acquire or generate for each channel in the  
# #         task if **sample_mode** is **FINITE_SAMPLES**. If  
# #         **sample_mode** is **CONTINUOUS_SAMPLES**, NI-DAQmx uses  
# #         this value to determine the buffer size.
# taskSlave.timing.cfg_samp_clk_timing(
#     rate=SAMPLING_RATE,
#     sample_mode=AcquisitionType.FINITE, 
#     samps_per_chan=INTERNAL_SAMPLES_PER_CH
# )

# # print(taskSlave.timing.samp_quant_samp_mode)

# # Add channels to slave
# taskSlave.ai_channels.add_ai_voltage_chan('Dev1/ai0:3')

# # measure time
# timeBeforeTask = []
# timeAfterTask = []

# def acquire(
#     outRange=[STARTING_RANGE, ENDING_RANGE],
#     stepSize=STEPS_SIZE,
#     samplesPerCh=SAMPLES_PER_CH_TO_READ
#     ):

#     # if not debugging:
        
#     outputArr = np.arange(*outRange, stepSize)

#     for val in outputArr:
#         timeBeforeTask.append(time.time_ns() / 10 ** 9)
#         taskMaster.write([val], auto_start=True)
#         taskMaster.stop()
#         # timeAfterTask.append(time.time_ns() / 10 ** 9)

#         # timeBeforeTask.append(time.time_ns() / 10 ** 9)
#         data = taskSlave.read(number_of_samples_per_channel=samplesPerCh)
#         taskSlave.stop()
#         timeAfterTask.append(time.time_ns() / 10 ** 9)
        
#         dataDc['0'] += data[0]
#         dataDc['1'] += data[1]
#         dataDc['2'] += data[2]
#         dataDc['3'] += data[3]


#     taskMaster.write([0.0], auto_start=True)
#     taskMaster.close()
#     taskSlave.close()
#     print('Done!')

# t0 = time.time_ns()
# acquire()
# tf = time.time_ns()

# print(f'Exp concluded in: {(tf-t0) / 10**9} s')

# # plot results
# pl.ion()
# data = pd.DataFrame(dataDc)
# mrkr = ['o', 'v', 's', '>']
# for i in range(4):
#     pl.plot(data.index, data[f'{i}'], label=f'Channel: {i}',
#         marker=mrkr[i], alpha=.5, linestyle='')

# """ 
# pl.plot(data.iloc[::SAMPLES_PER_CH].index, np.asarray(timeBeforeTask) - timeBeforeTask[0], label='Time B4 task', marker='<')
# pl.plot(data.iloc[::SAMPLES_PER_CH].index, np.asarray(timeAfterTask) - timeBeforeTask[0], label='Time after task', marker='>')
# pl.legend()
# pl.xlabel('Acquisition #')
# pl.ylabel('Time (s)')
#  """

# pl.rcParams.update({'font.size': 22})
# pl.legend()
# pl.xlabel('Acquisition #')
# pl.ylabel('Output (V)')


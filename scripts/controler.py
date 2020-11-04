import nidaqmx as mx
from nidaqmx.constants import (
    AcquisitionType,
    READ_ALL_AVAILABLE
)
import pandas as pd
import matplotlib.pyplot as pl
import numpy as np
import time

# Set initial params
# Debug
debugging = False
dataDc = {'0': [], '1':[], '2': [], '3': []}

# GLOBAL PARAMS
STARTING_RANGE = 0.0 # V
ENDING_RANGE = 5.0 # V
STEPS_SIZE = 0.1 # V
TIME_PER_STEP = 0.1 # s

# DAQ uses this to calculate the buffer size
INTERNAL_SAMPLES_PER_CH = 100 

# I guess it should be lesser than INTERNAL_SAMPLES_PER_CH, 
# otherwise the driver will try to read more samples than available 
# in the buffer
SAMPLES_PER_CH_TO_READ = READ_ALL_AVAILABLE 
# DELAY_TO_START_ACQUIS = 0.0 # s

SAMPLING_RATE = INTERNAL_SAMPLES_PER_CH / TIME_PER_STEP

# start tasks and add channels
taskMaster = mx.Task('Master')
taskMaster.ao_channels.add_ao_voltage_chan('Dev1/ao0')

taskSlave = mx.Task('Slave')
# Add channels to slave
taskSlave.ai_channels.add_ai_voltage_chan('Dev1/ai0:3')

# Configure the DAQ internal clock
# samps_per_chan (Optional[long]): Specifies the number of  
#         samples to acquire or generate for each channel in the  
#         task if **sample_mode** is **FINITE_SAMPLES**. If  
#         **sample_mode** is **CONTINUOUS_SAMPLES**, NI-DAQmx uses  
#         this value to determine the buffer size.
taskSlave.timing.cfg_samp_clk_timing(
    rate=SAMPLING_RATE,
    sample_mode=AcquisitionType.FINITE, 
    samps_per_chan=INTERNAL_SAMPLES_PER_CH
)

# print(taskSlave.timing.samp_quant_samp_mode)



# Measurement

# Select V out range
# select step siz
# Select time/step
# Selct number of samples/step
 
# For v in steps:
    # collect time
    # 1. set out volt
        # (wait time > 0.2 ms ?)
    
    # 2. start readings:
        # collect n (max buffer 4000S) samples at sampling rate (max rate: 400kS/s)
        # rate: number samp/stp / time/stp


# measure time
timeBeforeTask = []
timeAfterTask = []

def acquire(
    outRange=[STARTING_RANGE, ENDING_RANGE],
    stepSize=STEPS_SIZE,
    samplesPerCh=SAMPLES_PER_CH_TO_READ
    ):

    # if not debugging:
        
    outputArr = np.arange(*outRange, stepSize)

    for val in outputArr:
        timeBeforeTask.append(time.time_ns() / 10 ** 9)
        taskMaster.write([val], auto_start=True)
        taskMaster.stop()
        # timeAfterTask.append(time.time_ns() / 10 ** 9)

        # timeBeforeTask.append(time.time_ns() / 10 ** 9)
        data = taskSlave.read(number_of_samples_per_channel=samplesPerCh)
        taskSlave.stop()
        timeAfterTask.append(time.time_ns() / 10 ** 9)
        
        dataDc['0'] += data[0]
        dataDc['1'] += data[1]
        dataDc['2'] += data[2]
        dataDc['3'] += data[3]


    taskMaster.write([0.0], auto_start=True)
    taskMaster.close()
    taskSlave.close()
    print('Done!')

t0 = time.time_ns()
acquire()
tf = time.time_ns()

print(f'Exp concluded in: {(tf-t0) / 10**9} s')

# plot results
pl.ion()
data = pd.DataFrame(dataDc)
mrkr = ['o', 'v', 's', '>']
for i in range(4):
    pl.plot(data.index, data[f'{i}'], label=f'Channel: {i}',
        marker=mrkr[i], alpha=.5, linestyle='')

""" 
pl.plot(data.iloc[::SAMPLES_PER_CH].index, np.asarray(timeBeforeTask) - timeBeforeTask[0], label='Time B4 task', marker='<')
pl.plot(data.iloc[::SAMPLES_PER_CH].index, np.asarray(timeAfterTask) - timeBeforeTask[0], label='Time after task', marker='>')
pl.legend()
pl.xlabel('Acquisition #')
pl.ylabel('Time (s)')
 """

pl.rcParams.update({'font.size': 22})
pl.legend()
pl.xlabel('Acquisition #')
pl.ylabel('Output (V)')


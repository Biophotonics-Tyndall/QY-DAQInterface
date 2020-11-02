import nidaqmx as mx
import pandas as pd
import matplotlib.pyplot as pl
import numpy as np
import time

# Debug
debugging = False


dataDc = {'0': [], '1':[], '2': [], '3': []}

# GLOBAL PARAMS
STARTING_RANGE = 0.0 # V
ENDING_RANGE = 5.0 # V
STEPS_SIZE = 0.1 # V

SAMPLES_PER_CH = 100
TIME_BEFORE_START_ACQUIS = 0.0 # s

taskMaster = mx.Task('Master')
taskMaster.ao_channels.add_ao_voltage_chan('Dev1/ao0')

taskSlave = mx.Task('Slave')
taskSlave.ai_channels.add_ai_voltage_chan('Dev1/ai0:3')

# measure time
timeBeforeTask = []
timeAfterTask = []

def acquire(
    outRange=[STARTING_RANGE, ENDING_RANGE],
    stepSize=STEPS_SIZE,
    samplesPerCh=SAMPLES_PER_CH
    ):

    # if not debugging:
        
    outputArr = np.arange(*outRange, stepSize)



    for val in outputArr:
        timeBeforeTask.append([time.time_ns()])
        taskMaster.write([val], auto_start=True)
        taskMaster.stop()
        timeAfterTask.append([time.time_ns()])

        timeBeforeTask.append([time.time_ns()])
        data = taskSlave.read(samplesPerCh)
        taskSlave.stop()
        timeAfterTask.append([time.time_ns()])
        
        dataDc['0'] += data[0]
        dataDc['1'] += data[1]
        dataDc['2'] += data[2]
        dataDc['3'] += data[3]
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
    pl.plot(data.index, data[f'{i}'], label=f'Channel: {i}', mrkr[i], alpha=.5)

plt.rcParams.update({'font.size': 22})
pl.legend()
pl.xlabel('Acquisition #')
pl.ylabel('Output (V)')


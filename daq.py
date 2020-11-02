import nidaqmx as mx
import pandas as pd
import matplotlib.pyplot as pl

""" with mx.Task() as task:
    task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
    task.write([2.2, 1.1], auto_start=True)
    
with mx.Task() as task:
    task.ai_channels.add_ai_voltage_chan('Dev1/ai0')
    print(task.read()
 """
dataDc = {'0': [], '1':[], '2': []}
for i in [0, 1, 2]:
    task = mx.Task('1')
    task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
    task.write([i], auto_start=True)
    task.stop()
    task.close()

    task1 = mx.Task('2')
    task1.ai_channels.add_ai_voltage_chan('Dev1/ai0:2')
    data = task1.read(5)
    dataDc['0'] += data[0]
    dataDc['1'] += data[1]
    dataDc['2'] += data[2]

    task1.stop()
    task1.close()

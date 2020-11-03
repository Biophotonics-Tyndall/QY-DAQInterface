# Internal computer clock

According to [stack overflow](https://stackoverflow.com/questions/1938048/high-precision-clock-in-python): 

    "The standard time.time() function provides sub-second precision, though that precision varies by platform. For Linux and Mac precision is +- 1 microsecond or 0.001 milliseconds. Python on Windows uses +- 16 milliseconds precision due to clock implementation problems due to process interrupts. The timeit module can provide higher resolution if you're measuring execution time."

run the following code to test it on the machine:

```python
# measure the smallest time delta by spinning until the time changes
import numpy as np
import time

def measure():
    # replace `time.time()` for `time.time_ns()` for higher resolution

    t0 = time.time()
    t1 = t0
    while t1 == t0:
        t1 = time.time()
    return (t0, t1, t1-t0)

resolution = np.mean([measure()[2] for i in range(1000)])

```

# API NIDAQMX full reference

[https://nidaqmx-python.readthedocs.io/en/latest/index.html](https://nidaqmx-python.readthedocs.io/en/latest/index.html)


# Few examples available on

[https://github.com/ni/nidaqmx-python/tree/master/nidaqmx_examples](https://github.com/ni/nidaqmx-python/tree/master/nidaqmx_examples)
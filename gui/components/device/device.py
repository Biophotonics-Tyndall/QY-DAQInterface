class DAQ:
    outputChannels = ['AO0', 'AO1']
    inputChannels = ['AI0', 'AI1', 'AI2', 'AI3', 'AI4', 'AI5', 'AI6', 'AI7']


class LASERS:
    LINES = ['405 nm', '785 nm', '976 nm']

    @classmethod
    def modulation(cls, line):
        assert line in cls.LINES, f"{line} is not a valid line. Select one of {cls.LINES}"

        minVoltage = 0.0
        if line == "405 nm":
            maxVoltage = 0.170
            step = 0.002
        elif line == "785 nm":
            maxVoltage = 1.678
            step = 0.01
        elif line == "976 nm":
            maxVoltage = 5.400
            step = 0.1

        return (minVoltage, maxVoltage, step)


class POWERMETERS:
    PMSRANGES = ['250 uW', '2.5 mW', '10 mW', '69 mW', '690 mW']
    PMRRANGES = ['2.2 mW', '6.1 mW', '9.5 mW', '22 mW', '61 mW']


class APDS:
    GAINS = ['Min', 'Max']


BEAMLINES = ['Narrow', 'Wide']

from scripts.daq import Controler
# import configparser
import os
import subprocess, os, platform

Daq = Controler()

def run_event(message):
    print(message)
    Daq.run()
    input('Press ENTER to continue...')

def plot_event(message):
    print(message)
    Daq.plot()
    input('Press ENTER to continue...')

def row(s):
    return('  ' + '\u2502' + s.ljust(width - 4) + '\u2502')
width = 70
upHline = '  ' + '\u250C' + '\u2500' * (width - 4) + '\u2510'
downHline = '  ' + '\u2514' + '\u2500' * (width - 4) + '\u2518'

running = True
while running:
    menu = '\n'.join([
        upHline,
        row(" "),
        row("       🔬 QY - System"), 
        row("       v.0.0.1"),
        row(" "),
        row(" "),
        row("    1. Settings"), 
        row("    2. Run"), 
        row("    3. Save"), 
        row("    4. Plot data"), 
        row("    5. Exit"), 
        row(" "),
        downHline,
    ])
    os.system('cls' if os.name == 'nt' else 'clear')
    print(menu)
    action = input('   >> ')

    os.system('cls' if os.name == 'nt' else 'clear')
    if action == '5':
        running = False
    elif action == '4':
        plot_event('Ploting...')
    elif action == '3':
        input('saving...')
    elif action == '2':
        run_event('Running...')
    elif action == '1':
        print('Change the file, save and close it.')
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', 'measurement_config.txt'))
        elif platform.system() == 'Windows':    # Windows
            os.startfile('measurement_config.txt')
        else:                                   # linux variants
            subprocess.call(('xdg-open', 'measurement_config.txt'))

        input('Press ENTER to continue...')
    else:
        print('Invalid option...')


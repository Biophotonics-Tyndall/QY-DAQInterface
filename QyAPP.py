from scripts.daq import Controler
# import configparser
import os
import subprocess, os, platform

Daq = Controler()

# def run_event(message):
#     print(message)
#     Daq.run()
#     input('\nPress ENTER to continue...')

# def plot_event(message):
#     print(message)
#     Daq.plot()
#     input('\nPress ENTER to continue...')

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
        row("       ⏱  QY - System"), 
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
        print('Closing...\n')

    elif action == '4':
        print('Plotting...\n')
        Daq.plot()

    elif action == '3':
        print('Saving...\n')

    elif action == '2':
        print('Running...\n')
        Daq.run()

    elif action == '1':
        print('Change the file, save and close it.')
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', 'measurement_config.txt'))
        elif platform.system() == 'Windows':    # Windows
            os.startfile('measurement_config.txt')
        else:                                   # linux variants
            subprocess.call(('xdg-open', 'measurement_config.txt'))

    else:
        print('Invalid option...')

    input('\nPress ENTER to continue...')


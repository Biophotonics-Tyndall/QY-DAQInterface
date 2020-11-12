from source.daq import Controler
# import configparser
import os
import subprocess, os, platform

Daq = Controler()

# menu = '\n'.join([
#         upHline,
#         row(" "),
#         row("       QY - System"), 
#         row("       \xa9 QyAPP v.0.0.1"),
#         row(" "),
#         row(" "),
#         row("    1. \u2699 Settings"), 
#         row("    2. \u25b6 Run"),
#         row("    3. \U0001f4be\u0000 Save"), 
#         row("    4. \U0001f4c8\u0000 Plot data"), 
#         row("    5. \u274c\u0000 Exit"), 
#         row(" "),
#         downHline,
#     ])

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
        row("       QY - System"), 
        row("       \xa9 QyAPP v.0.0.1"),
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
        Daq.savelog()
        # chack if the data is saved and ask for action
        # input('Do you ')

    elif action == '4':
        print('Plotting...\n')
        Daq.plot()

    elif action == '3':
        print('Saving...\n')
        Daq.save()

    elif action == '2':
        print('Running...\n')
        Daq.run()

    elif action == '1':
        print('Change the file, save and close it.')
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', 'config.txt'))
        elif platform.system() == 'Windows':    # Windows
            os.startfile('config.txt')
        else:                                   # linux variants
            subprocess.call(('xdg-open', 'config.txt'))

    else:
        print('Invalid option...')

    input('\nPress ENTER to continue...')


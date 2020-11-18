import os
import subprocess
import os
import platform
import logging

logging.basicConfig(
    filename='output/logs/errors.log',
    format='%(asctime)s | %(levelname)s: %(message)s',
    datefmt='%d/%m/%Y %I:%M:%S %p'
)


def main():
    from source.daq import Controler
    # import configparser

    # Create daq object
    Daq = Controler()

    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    # Menu creation
    def row(s):
        return('  ' + '\u2502' + s.ljust(width - 4) + '\u2502')

    width = 70
    upHline = '  ' + '\u250C' + '\u2500' * (width - 4) + '\u2510'
    downHline = '  ' + '\u2514' + '\u2500' * (width - 4) + '\u2518'

    menu = '\n'.join([
        upHline,
        row(" "),
        row("       QY - System"),
        row(f"       \xa9 {Daq._appDetails['name']} v{Daq._appDetails['version']}"),
        row(" "),
        row(" "),
        row("    t. Settings"),
        row("    r. Run"),
        row("    s. Save"),
        row("    p. Plot data"),
        row("    x. Exit"),
        row(" "),
        downHline,
    ])

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

    running = True
    while running:
        clear()
        print(menu)
        action = input('   >> ').lower().strip()

        clear()
        if action == 'x':
            running = False
            print('Closing...\n')
            if not Daq.isdatasaved():
                yORn = input(
                    'Would you like to save last data? [y/n]: ').lower().strip()
                while (yORn != 'y') and (yORn != 'n'):
                    clear()
                    yORn = input(
                        'Would you like to save last data? [y/n]: ').lower().strip()
                if yORn == 'y':
                    Daq.save()
                else:
                    Daq.savelog()

        elif action == 'p':
            print('Plotting...\n')
            Daq.plot()

        elif action == 's':
            print('Saving...\n')
            Daq.save()

        elif action == 'r':
            print('Running...\n')
            try:
                Daq.run()
            except Exception as e:
                logging.error(str(e))
                print('Something went wrong...\n',
                      'Check if device is connected and its name is Dev1, then try again.\n')

        elif action == 't':
            print('Change the file, save and close it.')
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', 'config.txt'))
            elif platform.system() == 'Windows':    # Windows
                os.startfile('config.txt')
            else:                                   # linux variants
                subprocess.call(('xdg-open', 'config.txt'), shell=False)

        else:
            print('Invalid option...')

        input('\nPress ENTER to continue...')


try:
    main()
except Exception as e:
    logging.error(str(e))

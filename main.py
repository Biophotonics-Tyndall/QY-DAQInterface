import os
import subprocess
import platform
import logging

logging.basicConfig(
    filename='output/logs/errors.log',
    format='%(asctime)s | %(levelname)s: %(message)s',
    datefmt='%d/%m/%Y %I:%M:%S %p'
)

debug = False

def main():
    from source.daq import Controler
    # import configparser

    # Create daq object
    Controler.debug = debug
    Daq = Controler()

    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    # Menu creation
    def row(s):
        return('  ' + '\u2502' + s.ljust(width - 4) + '\u2502')

    width = 70
    upHline = '  ' + '\u250C' + '\u2500' * (width - 4) + '\u2510'
    downHline = '  ' + '\u2514' + '\u2500' * (width - 4) + '\u2518'
    print('Atention! The saved data will be always the last run!')
    input('>> ')

    def menu(statusMsg):
        return(
            '\n'.join([
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
                row(f"  {statusMsg}"),
                downHline,
            ])
        )

    running = True
    while running:
        clear()
        print(menu(Daq.status()))
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
                # bug here. Should close the task after the error. 
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

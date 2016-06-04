
import argparse
import contextlib
import datetime
import sys
import time

import serial

import matrix
    

def main ():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--serial',
        help='Device file of the serial port to use.')
    parser.add_argument('-R', '--baud-rate', default=38400, type=int,
        help='Baud rate to use on the serial port.')

    parser.add_argument('-F', '--faux-sensor', default=False,
        action='store_true', help='Use faux sensor data (testing).')
    parser.add_argument('-T', '--test-sensor', default=False, 
       action='store_true', help='Sensor data ranging from 0 to 63 to verify the correct order.')

    parser.add_argument('file', help='Dump file', nargs='?',
        default=datetime.datetime.now().strftime('dump_%Y-%m-%d_%H-%M-%S.csv'))

    args = parser.parse_args()

    if not (args.serial or args.faux_sensor or args.test_sensor):
        print 'Either run in faux sensor mode (-F), test mode (-T), or supply a serial port'
        sys.exit(-1)

    if args.serial and args.faux_sensor or args.serial and args.test_sensor or args.test_sensor and args.faux_sensor:
        print 'Supply either -F, -T or -s options.'
        sys.exit(-2)

    if args.serial:
        try:
            serial_port_fp = int(args.serial)

        except ValueError:
            serial_port_fp = args.serial

        fp = serial.Serial(serial_port_fp, args.baud_rate)
    
    if args.test_sensor:
        fp = matrix.TestSensor()
        
    if args.faux_sensor:
        fp = matrix.FauxSensor()

    with matrix.LogWriter() as log:
        while True:
            data = [-1] * 64

            for _ in range(64):
                i, val = matrix.read_frame(fp)
                data[i] = val

            log.write(data)

if __name__ == '__main__':
    main()

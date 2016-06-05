'''
    heatmap
    ~~~~~~~
    Plot a heatmap from sensor data read from the serial port.

    Usage::
        python heatmap.py [options]

    or::
        python heatmap.py -h

    for additional help.
'''

import argparse
import datetime
import functools
import math
import os, os.path
import sys
import time
import threading

import numpy
import serial

if sys.platform == 'darwin':
    # OSX backend does not currently support blitting
    import matplotlib
    matplotlib.use('TkAgg')

import matplotlib.animation
import matplotlib.pylab as plt

import matrix


heatmap_data = numpy.ones(64)


def update_mesh (num, mesh, transform):
    global heatmap_data

    mesh.set_array(transform(heatmap_data))
    update_mesh._samples.append(datetime.datetime.now())

    if len(update_mesh._samples) >= 60:
        deltas = [(update_mesh._samples[i] - update_mesh._samples[i - 1]).total_seconds()
                  for i in range(1, len(update_mesh._samples))]

        if all(d > 0 for d in deltas):
            fps = [1.0 / d for d in deltas]
            print("Mesh: %.2ffps" % (sum(fps) / len(fps)))

        update_mesh._samples = []

    return mesh,


update_mesh._samples = []


def write_log (fp, fmt, data):
    fp.write(fmt.format(datetime.datetime.now().isoformat(), *data))


def update_data (read_frame, event, log):
    global heatmap_data

    while event.is_set():
        data = numpy.zeros(64)

        for _ in range(64):
            channel, val = read_frame()
            data[channel] = val

        if log:
            log.write(data)

        heatmap_data = data

        update_data._samples.append(datetime.datetime.now())
        if len(update_data._samples) >= 60:
            deltas = [(update_data._samples[i] - update_data._samples[i - 1]).total_seconds()
                          for i in range(1, len(update_data._samples))]

            if all(d > 0 for d in deltas):
                fps = [1.0 / d for d in deltas]
                print("Read: %.2ffps" % (sum(fps) / len(fps)))

            update_data._samples = []

update_data._samples = []


def main ():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--serial',
        help='Device file of the serial port to use.')
    parser.add_argument('-R', '--baud-rate', default=38400, type=int,
        help='Baud rate to use on the serial port.')

    parser.add_argument('-F', '--faux-sensor', default=False,
        action='store_true', help='Use faux sensor data (testing).')

    parser.add_argument('-b', '--log-base', default=None,
        type=int, help='Use base LOG_BASE logarithm as transformation')

    parser.add_argument('-f', '--fps', help='Rendering FPS', type=float,
        default=30.0)

    parser.add_argument('-L', '--log', help='Turn on logging.',
        action='store_true', default=False)

    args = parser.parse_args()

    if not (args.serial or args.faux_sensor):
        print 'Either run in faux sensor mode (-F) or supply a serial port'
        sys.exit(-1)

    if args.serial and args.faux_sensor:
        print 'Supply either -F or -s options.'
        sys.exit(-2)

    if args.log_base:
        transform = lambda x: math.log(x+1, args.log_base)
    else:
        transform = lambda x: x

    if args.serial:
        try:
            serial_port_fp = int(args.serial)

        except ValueError:
            serial_port_fp = args.serial

        fp = serial.Serial(serial_port_fp, args.baud_rate)

    else:
        fp = matrix.FauxSensor()

    zeros = numpy.zeros((8, 8))
    event = threading.Event()
    event.set()

    if args.log:
        log = matrix.LogWriter()

    else:
        log = None

    fig = plt.figure()
    mesh = plt.pcolor(zeros, vmin=transform(0), vmax=transform(600))
    plt.colorbar()

    read_frame = functools.partial(matrix.read_frame, fp)
    thread = threading.Thread(target=update_data,
        args=(read_frame, event, log))

    thread.daemon = True
    thread.start()

    mesh_anim = matplotlib.animation.FuncAnimation(fig,
        update_mesh, int(args.fps),
        fargs=(mesh, numpy.vectorize(transform)),
        interval=(1000.0/args.fps), blit=True)

    plt.show()

    print 'Stopping thread.'

    event.clear()
    thread.join()

    fp.close()

    if log:
        log.close()


if __name__ == '__main__':
    main()

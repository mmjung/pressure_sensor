
import datetime
import re
import sys
import time


def main ():
    path = sys.argv[1]
    last_ts = None
    cnt = 0

    fp = open(path)

    for line in fp:
        cnt += 1

        line = line.strip()
        data = line.split(',')

        if len(data) < 65:
            print('Line {} is too short {} != 65.'.format(cnt, len(data)))

        elif len(data) > 65:
            print('Line {} is too long {} != 65.'.format(cnt, len(data)))

        try:
            s = data[0]

            if '.' in s:
                ms = int(s.split('.')[1]) / 1000000.0

            else:
                ms = 0

            ts = datetime.datetime(*map(int, re.split('[^\d]', s)[:-1]))
            ts += datetime.timedelta(seconds=ms)

        except Exception as ex:
            print('Line {} contains an invalid date format.'.format(cnt))

        else:
            if last_ts and not ts > last_ts:
                print('Line {} has a date that is <= previous line: {} <= {}.'.format(cnt,
                    last_ts, ts))

            last_ts = ts

        try:
            vals = [int(float(v)) for v in data[1:]]

        except ValueError as ex:
            raise
            print('Line {} contains a non-int value'.format(cnt))

        else:
            for i in range(len(vals)):
                if not 0 <= vals[i] <= 1023:
                    print('Line {} column {} value out of range: {}.'.format(cnt, i + 1, vals[i]))

    fp.close()


if __name__ == '__main__':
    main()


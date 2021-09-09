#!/usr/bin/env python3

import subprocess
import sys

if __name__ == "__main__":

    print('sys.argv:')
    print(sys.argv)

    mvox_exec = 'mvox'
    mvox_args = sys.argv[1:]

    # FIXME: This workaround to use hyphens in arguments should not be required
    # see: https://github.com/Slicer/SlicerExecutionModel/issues/17
    for i in range(len(mvox_args)):
        if mvox_args[i].startswith('--'):
            # Replace _ with - in long flags
            # mvox_args[i].replace('_', '-')
            # Remove one - from long flags to convert to short flags
            mvox_args[i] = mvox_args[i].replace('--', '-')

    cmd = [mvox_exec] + mvox_args

    print('cmd:')
    print(cmd)

    subprocess.run(cmd)

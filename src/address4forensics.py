import sys
import re
from enum import enum

# first arg will always be this script
args = sys.argv[1:]
argsLen = len(sys.argv)
address4forensics(args)

DEFAULT_PARTITION_OFFSET = 0
DEFAULT_SECTOR_SIZE = 512
DEFAULT_FAT_TABLES = 2

def address4forensics(self, args):
    modes = solveModes(args)

# we'll create a list of the modes we find
def solveModes(self, args):
    mode = [-1]

    mode[0] = findMainMode(mode, args)
    mode.append(args,'-b', '--partition-start=')
    # this adds two values to the list
    mode.extend(byteMode(args))
    mode.append(args, '-s', '--sector-size=', DEFAULT_SECTOR_SIZE)
    mode.append(args, '-l', '--logical-known=')
    mode.append(args, '-p', '--logical-known=')
    mode.append(args, '-c', '--cluster-known=')
    mode.append(args, '-k', '--cluster-size=')
    mode.append(args, '-r', '--reserved=')
    mode.append(args, '-t', '--fat-tables=', DEFAULT_FAT_TABLES)
    mode.append(args, '-f', '--fat-length=')

    for element in mode:
        print element


def findMainMode(mode, args):
    # we expect that the first arg will tell us what mode we are in
    mode = -1
    arg = args[0]
    if arg == '-L' or arg == '--logical':
        mode = Mode.logical
    elif arg == '-P' or arg == '--physical':
        mode = Mode.physical
    elif arg == '-C' or arg == '--cluster':
        mode = Mode.cluster
    return mode

def getOffset(args):
    offset = 0
    pattern = re.compile('--partition-start=')
    for arg in args:
        if arg == '-b':
            index = args.index(arg)
            offset = int(args[index])
        elif pattern.match(arg) != None:
            index = args.index(arg)
            offset = int(args[index][18:])
    return offest

def byteMode(args):
    byteMode = [False, DEFAULT_SECTOR_SIZE]
    pattern = re.compile('--sector-size=')
    for arg in args:
        if arg == '-B' or arg == '--byte-address=':
            byteMode[0] = True

        # search for the size of sectors
        elif arg == '-s':
            index = args.index(arg)
            byteMode[1] = int(args[index+1])
        elif pattern.match(arg) != None:
            byteMode[1] = int(args[index][15:])
    return byteMode


def parseArgument(args, short, long):
    value = -1
    pattern = re.compiler(long)
    for arg in args:
        if arg = short:
            index = args.index(arg)
            address = int(args[index+1])
        elif pattern.match(arg) != None:
            size = int(arg[len(long)])

def parseArgument(args, short, long, default):
    value = default
    pattern = re.compiler(long)
    for arg in args:
        if arg = short:
            index = args.index(arg)
            address = int(args[index+1])
        elif pattern.match(arg) != None:
            size = int(arg[len(long)])


class Mode(Enum):
    default = 1000
    logical = 1001
    physical = 1002
    cluster = 1003

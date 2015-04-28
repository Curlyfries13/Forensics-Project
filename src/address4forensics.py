import sys
import re

# first arg will always be this script
args = sys.argv[1:]
argsLen = len(sys.argv)

DEFAULT_PARTITION_OFFSET = 0
DEFAULT_SECTOR_SIZE = 512
DEFAULT_FAT_TABLES = 2

DEFAULT = 1000
LOGICAL = 1001
PHYSICAL = 1002
CLUSTER = 1003


def main():
    address4forensics(args)

def address4forensics(args):
    modes = solveModes(args)
    calculate(modes)

def calculate(mode):
    if(mode[0] == LOGICAL):
        calculateLogical(mode[1:])
    elif(mode[0] == PHYSICAL):
        calculatePhysical(mode[1:])
    elif(mode[0] == CLUSTER):
        calculateCluster(mode[1:])

def calculateLogical(mode):
    # get all the variables declared and initialized here
    result = -1

    offset = -1
    sectorSize = -1
    physical = -1
    cluster = -1

    clusterSize = -1
    reservedSectors = -1
    fatTables = -1
    fatLength = -1


    offset = mode[0]
    if(mode[1]):
        sectorSize = mode[2]
    else:
        sectorSize = DEFAULT_SECTOR_SIZE
    if(mode[3] != -1):
        # this is the only argument we need in this case
        print mode[3]
        exit();
    if(mode[4] != -1):
        physical = mode[4]
    if(mode[5] != -1):
        cluster = mode[5]
        clusterSize = mode[6]
        reservedSectors = mode[7]
        fatTables = mode[8]
        fatLength = mode[9]

    if(physical == -1 and cluster == -1):
        print 'Error: no address to convert'
        exit();
    elif(physical != -1 and cluster != -1):
        print 'Error: conflicting address command, only enter one known address type'
        exit();
    elif(cluster != -1):

        if(clusterSize < 0 or reservedSectors < 0 or fatTables < 0 or fatLength < 0):
            comma = False;
            errorMessage = 'Error: '
            if(clusterSize < 0):
                if(comma):
                    errorMessage+=', '
                else:
                    comma = True;
                errorMessage += 'Invalid cluster size'
            elif(reservedSectors < 0):
                if(comma):
                    errorMessage+=', '
                else:
                    comma = True;
                errorMessage += 'Invalid number of reserved sectors'
            elif(fatTables < 0):
                if(comma):
                    errorMessage +=', '
                else:
                    comma = True;
                errorMessage += 'Invalid number of FAT tables'
            elif(fatLength < 0):
                if(comma):
                    errorMessage +=', '
                else:
                    comma = True;
                errorMessage += 'Invalid FAT length'
            print errorMessage
            exit()
        else:
            # solve the logical address based on cluster information
            result = reservedSectors + (fatTables * fatLength) + (cluster - 2) * clusterSize
            if(mode[1]):
                result = result * sectorSize
            print result
            exit();

    elif(physical != -1):
        # solve logical address based on physical information
        result = physical - offset
        if(mode[1]):
            result = result * sectorSize
        print result
        exit();
    print "Unknown Error"
    exit();

def calculatePhysical(mode):
    result = -1

    offset = -1
    sectorSize = -1
    logical = -1
    cluster = -1

    clusterSize = -1
    reservedSectors = -1
    fatTables = -1
    fatLength = -1

    offset = mode[0]
    if(mode[1]):
        sectorSize = mode[2]
    else:
        sectorSize = DEFAULT_SECTOR_SIZE
    if(mode[3] != -1):
        logical = mode[3]
    if(mode[4] != -1):
        # this is the only argument we need in this case
        print mode[4]
        exit();
    if(mode[5] != -1):
        cluster = mode[5]
        clusterSize = mode[6]
        reservedSectors = mode[7]
        fatTables = mode[8]
        fatLength = mode[9]

    # check for errors
    if(logical == -1 and cluster == -1):
        print 'Error: no address to convert'
        exit();
    elif(logical != -1 and cluster != -1):
        print 'Error conflicting address command, only enter one known address'
        exit();
    elif(cluster != -1):

        if(clusterSize < 0 or reservedSectors < 0 or fatTables < 0 or fatLength < 0):
            comma = False;
            errorMessage = 'Error: '
            if(clusterSize < 0):
                if(comma):
                    errorMessage+=', '
                else:
                    comma = True;
                errorMessage += 'Invalid cluster size'
            elif(reservedSectors < 0):
                if(comma):
                    errorMessage+=', '
                else:
                    comma = True;
                errorMessage += 'Invalid number of reserved sectors'
            elif(fatTables < 0):
                if(comma):
                    errorMessage+=', '
                else:
                    comma = True;
                errorMessage += 'Invalid number of FAT tables'
            elif(fatLength < 0):
                if(comma):
                    errorMessage+=', '
                else:
                    comma = True;
                errorMessage += 'Invalid FAT length'
            print errorMessage
            exit()
        else:
            # solve the logical address based on cluster information
            result = offset + reservedSectors + (fatTables * fatLength) + ((cluster - 2) * clusterSize)
            if(mode[1]):
                result = reslut * sectorSize
            print result
            exit()
    elif(logical != -1):
        result = logical + offset
        if(mode[1]):
            result = result * sectorSize
        print result
        exit();
    print "Unknown Error"
    exit();

def calculateCluster(mode):
    result = -1

    offset = -1
    sectorSize = -1
    logical = -1
    physical = -1

    clusterSize = -1
    reservedSectors = -1
    fatTables = -1
    fatLength = -1

    offset = mode[0]
    if(mode[1]):
        print "Error: byte address is not compatible with this mode"
        exit();
    else:
        sectorSize = DEFAULT_SECTOR_SIZE
    if(mode[3] != -1):
        logical = mode[3]
    if(mode[4] != -1):
        physical = mode[4]
    if(mode[5] != -1):
        # this is the only argument we need in this case
        print mode[5]
        exit();
    clusterSize = mode[6]
    reservedSectors = mode[7]
    fatTables = mode[8]
    fatLength = mode[9]

    if(logical == -1 and physical == -1):
        print 'Error: no address to convert'
        exit();
    elif(logical != -1 and cluster != -1):
        print 'Error conflicting address command, only eneter one known address'
        exit();
    elif(clusterSize < 0 or reservedSectors < 0 or fatTables < 0 or fatLength < 0):
        comma = False;
        errorMessage = 'Error: '
        if(clusterSize < 0):
            if(comma):
                errorMessage+=', '
            else:
                comma = True;
            errorMessage += 'Invalid cluster size'

            exit()
        elif(reservedSectors < 0):
            if(comma):
                errorMessage+=', '
            else:
                comma = True;
            errorMessage += 'Invalid number of reserved sectors'
            exit()
        elif(fatTables < 0):
            if(comma):
                errorMessage+=', '
            else:
                comma = True;
            print 'Invalid number of FAT tables'
            exit();
        elif(fatLength < 0):
            if(comma):
                errorMessage+=', '
            else:
                comma = True;
            print 'Invalid FAT length'
        print errorMessage
        exit()
    elif(logical != -1):
        result = ((logical - (fatTables * fatLength) - reservedSectors) / clusterSize) + 2
        print result
        exit()
    elif(physical != -1):
        result = ((physical - (fatTables * fatLength) - reservedSectors - offset) / clusterSize) + 2
        print result
        exit()
# we'll create a list of the modes we find
def solveModes(args):
    mode = [-1]

    mode[0] = findMainMode(mode, args)

    # 0
    mode.append(parseArgument(args,'-b','--partition-start=', -1))
    # this adds two values to the list
    # 1, 2; 1 is bool for byte-address, 2 is the sector size
    mode.extend(byteMode(args))
    #mode.append(parseArgument(args, '-s', '--sector-size=', DEFAULT_SECTOR_SIZE))
    # 3
    mode.append(parseArgument(args, '-l', '--logical-known=', -1))

    # 4
    mode.append(parseArgument(args, '-p', '--physical-known=', -1))

    # 5
    mode.append(parseArgument(args, '-c', '--cluster-known=', -1))

    # 6
    mode.append(parseArgument(args, '-k', '--cluster-size=', -1 ))

    # 7
    mode.append(parseArgument(args, '-r', '--reserved=', -1))

    # 8
    mode.append(parseArgument(args, '-t', '--fat-tables=', DEFAULT_FAT_TABLES))

    # 9
    mode.append(parseArgument(args, '-f', '--fat-length=', -1))

    return mode


def findMainMode(mode, args):
    # we expect that the first arg will tell us what mode we are in
    mode = -1
    arg = args[0]
    if arg == '-L' or arg == '--logical':
        mode = LOGICAL
    elif arg == '-P' or arg == '--physical':
        mode = PHYSICAL
    elif arg == '-C' or arg == '--cluster':
        mode = CLUSTER
    return mode

def byteMode(args):
    byteMode = [False, DEFAULT_SECTOR_SIZE]
    pattern = re.compile('--sector-size=')
    for arg in args:
        if arg == '-B' or arg == '--byte-address':
            byteMode[0] = True

        # search for the size of sectors
        elif arg == '-s':
            index = args.index(arg)
            byteMode[1] = int(args[index+1])
        elif pattern.match(arg) != None:
            byteMode[1] = int(args[index][15:])
    return byteMode


def parseArgument(args, short, long, default):
    value = default
    pattern = re.compile(long)
    for arg in args:
        if (arg == short):
            index = args.index(arg)
            value = int(args[index+1])
        elif pattern.match(arg) != None:
            value = int(arg[len(long):])
    return value



if __name__== "__main__":
    main()

import sys
TIME = 1004
DATE = 1005
args = sys.argv[1:]
argsLen = len(sys.argv)

scale = 16
num_of_bits = 16

def main():
    mode = -1
    file = False
    hexIn = False
    hexString = ''
    # print argsLen
    if(argsLen != 4):
        print 'Error missing params'
        exit()
    print args[2]
    if(args[0] == '-T'):
        mode = TIME
    elif(args[0] == '-D'):
        mode = DATE
    else:
        print 'Error mode not specified'
    if(args[1] == '-f'):
        file = True
        filePointer = open(args[2], 'rb')
        hexString = bin(int(filePointer.read(), scale))[2:].zfill(num_of_bits)
        # print len(hexString)
        # print hexString

    elif(args[1] == '-h'):
        hexIn = True
        hexString = bin(int(args[2],scale))[2:].zfill(num_of_bits)
        # print len(hexString)
        # print hexString
    else:
        print 'Error input not specified'

    if(mode == DATE):
        yearString = hexString[:7]
        dayString = hexString[-5:]
        monthString = hexString[7:11]

        # print
        # print yearString
        # print dayString
        # print monthString
        # print

        year = int(yearString, 2)
        day = int(dayString, 2)
        month = int(monthString, 2)

        # print year
        # print day
        # print month

        outYear = str(year + 1980)
        outDay = str(day)
        if(month == 1):
            outMonth = 'January'
        elif(month == 2):
            outMonth = 'February'
        elif(month == 3):
            outMonth = 'March'
        elif(month == 4):
            outMonth = 'April'
        elif(month == 5):
            outMonth = 'May'
        elif(month == 6):
            outMonth = 'June'
        elif(month == 7):
            outMonth = 'July'
        elif(month == 8):
            outMonth = 'August'
        elif(month == 9):
            outMonth = 'September'
        elif(month == 10):
            outMonth = 'October'
        elif(month == 11):
            outMonth = 'November'
        elif(month == 12):
            outMonth = 'December'

        print outMonth + ' ' + outDay + ', ' + outYear
    elif(mode == TIME):
        hourString = hexString[:5]
        minuteString = hexString[5:11]
        secondString = hexString[-5:]

        # print
        # print hourString
        # print minuteString
        # print secondString
        # print

        hour = int(hourString, 2)
        minute = int(minuteString, 2)
        second = int(secondString, 2)

        # print hour
        # print minute
        # print second

        if(len(str(hour%12)) == 1):
            outHour = '0' + str(hour%12)
        else:
            outHour = str(hour%12)

        if(len(str(minute)) == 1):
            outMinute = '0' + str(minute)
        else:
            outMinute = str(minute)

        if(len(str(second*2)) == 1):
            outSecond = '0' + str(second*2)
        else:
            outSecond = str(second*2)
        outString = 'Time: ' + outHour + ':' + outMinute + ':' + outSecond
        if( (hour/12) >= 1):
            outString += ' AM'
        else:
            outString += ' PM'

        print outString

if __name__== '__main__':
    main()

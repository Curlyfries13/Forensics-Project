import string
import hashlib
import sys
import struct
import os

def main():
    filePath = sys.argv[1]
    printCheckSums(filePath)
    analyzeImage(filePath)

def printCheckSums(filePath):
    md5 = hashlib.md5(open(filePath, 'rb').read()).hexdigest()
    sha1 = hashlib.sha1(open(filePath, 'rb').read()).hexdigest()

    fileName = os.path.splitext(filePath)[0]

    md5File = open("MD5-" + fileName + ".txt", "w+")
    shaFile = open("SHA1-" + fileName + ".txt", "w+")

    md5File.write(md5)
    shaFile.write(sha1)

    md5File.close()
    shaFile.close()

    print 'Checksums: '
    print '=' * 50
    print "MD5:  " + md5
    print "SHA1: " + sha1
    print '=' * 50

def analyzeImage(filePath):

    partitionEntryStruct = struct.Struct("bbhbbhii")
    vbrStruct = struct.Struct("3b8b2bb2bb2b2bb2b2b2b4b4b4b")

    with open(filePath, "rb") as imageFile:
        imageFileData = imageFile.read()

        partitionEntry0 = partitionEntryStruct.unpack(imageFileData[446:462])
        partitionEntry1 = partitionEntryStruct.unpack(imageFileData[462:478])
        partitionEntry2 = partitionEntryStruct.unpack(imageFileData[478:494])
        partitionEntry3 = partitionEntryStruct.unpack(imageFileData[494:510])

        analyzePartitionEntry(partitionEntry0)
        analyzePartitionEntry(partitionEntry1)
        analyzePartitionEntry(partitionEntry2)
        analyzePartitionEntry(partitionEntry3)

        if isFAT(partitionEntry0[3]):
            print '=' * 50
            fatVBR0 = vbrStruct.unpack(imageFileData[partitionEntry0[6]*512:partitionEntry0[6]*512+40])
            analyzeVBR(fatVBR0, 0, partitionEntry0[3], partitionEntry0[6])

        if isFAT(partitionEntry1[3]):
            print '=' * 50
            fatVBR0 = vbrStruct.unpack(imageFileData[partitionEntry1[6]*512:partitionEntry1[6]*512+40])
            analyzeVBR(fatVBR0, 1, partitionEntry1[3], partitionEntry1[6])

        if isFAT(partitionEntry2[3]):
            print '=' * 50
            fatVBR0 = vbrStruct.unpack(imageFileData[partitionEntry2[6]*512:partitionEntry2[6]*512+40])
            analyzeVBR(fatVBR0, 2, partitionEntry2[3], partitionEntry2[6])

        if isFAT(partitionEntry3[3]):
            print '=' * 50
            fatVBR0 = vbrStruct.unpack(imageFileData[partitionEntry3[6]*512:partitionEntry3[6]*512+40])
            analyzeVBR(fatVBR0, 3, partitionEntry3[3], partitionEntry3[6])


def analyzeVBR(vbrStruct, partitionNumber, partitionType, partitionStart):
    print "Partition " + str(partitionNumber) + "(" + typeOfPartition(partitionType) + "):"

    #Flip the order and put into binary for little endian, this took way too long to figure out
    reserved2 =  bin(vbrStruct[15] & 0b11111111)
    reserved1 =  bin(vbrStruct[14] & 0b11111111)

    reserved2 = string.replace(reserved2, '0b', '').zfill(8)
    reserved1 = string.replace(reserved1, '0b', '').zfill(8)

    reservedSize =  reserved2 + reserved1

    reservedSize = int(reservedSize, 2)

    #Calculate FAT area for 32FAT partitions
    if partitionType == 12 or partitionType == 11:
        fat3 = bin(vbrStruct[39] & 0b11111111)
        fat2 = bin(vbrStruct[38] & 0b11111111)
        fat1 = bin(vbrStruct[37] & 0b11111111)
        fat0 = bin(vbrStruct[36] & 0b11111111)

        fat3 = string.replace(fat3, '0b', '').zfill(8)
        fat2 = string.replace(fat2, '0b', '').zfill(8)
        fat1 = string.replace(fat1, '0b', '').zfill(8)
        fat0 = string.replace(fat0, '0b', '').zfill(8)

        fatArea = fat3 + fat2 + fat1 + fat0

    #Calculate FAT area for 16FAT partitions
    else:
        fat1 = bin(vbrStruct[23] & 0b11111111)
        fat0 = bin(vbrStruct[22] & 0b11111111)

        fat1 = string.replace(fat1, '0b', '').zfill(8)
        fat0 = string.replace(fat0, '0b', '').zfill(8)

        fatArea = fat1 + fat0


    fatArea = int(fatArea, 2)
    fatSize = fatArea*2 + reservedSize - 1

    #Calculate number of sectors root directory uses
    root1 = bin(vbrStruct[18] & 0b11111111)
    root0 = bin(vbrStruct[17] & 0b11111111)

    root1 = string.replace(root1, '0b', '').zfill(8)
    root0 = string.replace(root0, '0b', '').zfill(8)

    numOfRootDirectories = root1 + root0
    numOfRootDirectories = int(numOfRootDirectories, 2)
    rootDirectorySize = numOfRootDirectories*32/512


    addressOfCluster2 = reservedSize + fatArea*2+rootDirectorySize + partitionStart

    print "Reserved Area: Start sector: 0 Ending Sector: " + str(reservedSize-1) + " Size: " + \
          str(reservedSize) + " sectors"
    print "Sectors per cluster: " + str(vbrStruct[13]) + " sectors"
    print "FAT area: Start sector: " + str(reservedSize) + " Ending Sector: " + str(fatSize)
    print "# of FATs: " + str(vbrStruct[16])
    print "The size of each FAT: " + str(fatArea) + " sectors"
    print "The first sector of cluster 2: " + str(addressOfCluster2) + " sectors"

    pass

def analyzePartitionEntry(partitionStruct):
    print "(" + format(partitionStruct[3], '02x') + ") " + \
          typeOfPartition(partitionStruct[3]) + ", " + str(partitionStruct[6]).zfill(10) + ", " +\
          str(partitionStruct[7]).zfill(10)
    pass

def typeOfPartition(value):
    if value == 1:
        return "DOS 12-bit FAT"
    elif value == 4:
        return "DOS 16-bit FAT for partitions smaller than 32 MB"
    elif value == 5:
        return "Extended Partition"
    elif value == 6:
        return "DOS 16-bit FAT for partitions larger than 32 MB"
    elif value == 7:
        return "NTFS"
    elif value == 8:
        return "AIX bootable partition"
    elif value == 9:
        return "AIX data partition"
    elif value == 11:
        return "DOS 32-bit FAT"
    elif value == 12:
        return "DOS 32-bit FAT for interrupt 13 support"
    elif value == 23:
        return "Hidden NTFS partition (XP and earlier)"
    elif value == 27:
        return "Hidden FAT32 partition"
    elif value == 30:
        return "Hidden VFAT partition"
    elif value == 60:
        return "Partition Magic recovery partition"
    elif value == 102 or value == 103 or value == 104 or value == 105:
        return "Novell partitions"
    elif value == 129:
        return "Linux"
    elif value == 130:
        return "Linux swap partition (can also be associated with Solaris partitions)"
    elif value == 131:
        return "Linux native file systems (Ext2, Ext3, Reiser, xiafs)"
    elif value == 134:
        return "FAT16 volume/stripe set (Windows NT)"
    elif value == 135:
        return "High Performance File System (HPFS) fault-tolerant mirrored partition or NTFS volume/stripe set"
    elif value == 165:
        return "FreeBSD and BSD/386"
    elif value == 166:
        return "OpenBSD"
    elif value == 169:
        return "NetBSD"
    elif value == 199:
        return "Typical of a corrupted NTFS volume/stripe set"
    elif value == 235:
        return "BeOS"
    else:
        return "Not a recognized partition type"

def isFAT(partitionType):
    if partitionType == 4 or partitionType == 6 or partitionType == 11 or partitionType == 12:
        return True
    else:
        return False

if __name__== "__main__":
    main()

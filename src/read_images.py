import hashlib
import os
import string
import struct
import sys

#Opens file to obtain checksums, no operations in this module
def printCheckSums(filePath):

    filePointer = open(filePath, 'rb')
    fileName = os.path.splitext(filePath)[0]

    md5 = hashlib.md5(filePointer.read()).hexdigest()
    sha1 = hashlib.sha1(filePointer.read()).hexdigest()

    md5File = open("MD5-" + fileName + ".txt", "w+")
    shaFile = open("SHA1-" + fileName + ".txt", "w+")

    md5File.write(md5)
    shaFile.write(sha1)

    filePointer.close()
    md5File.close()
    shaFile.close()

    print 'Checksums: '
    print '=' * 50
    print "MD5:  " + md5 + '\n'
    print "SHA1: " + sha1
    print '=' * 50

#Contains the data structs and calls analyzePartitionEntry and analyzeVBR functions
def analyzeImage(filePath):

    '''
    The partitionEntryStruct has 8 fields for 16 bytes, these 8 are

    partitionEntryStruct[0]: Current State of Partition (1 Byte)
    partitionEntryStruct[1]: Beginning of Partition - Head (1 Byte)
    partitionEntryStruct[2]: Beginning of Partition - Cylinder/Sector (1 Word)
    partitionEntryStruct[3]: Type of Partition (1 Byte)
    partitionEntryStruct[4]: End of Partition - Head (1 Byte)
    partitionEntryStruct[5]: End of Partition - Cylinder/Sector (1 Word)
    partitionEntryStruct[6]: Number of Sectors between the MBR and the First
                             Sector in the Partition (1 Double Word)
    partitionEntryStruct[7]: Number of Sectors in the Partition (1 Double Word)
    '''
    partitionEntryStruct = struct.Struct("bbhbbhii")

    '''
    The vbrStruct has 15 fields for the first 39 bytes of the VBR. This code
    could be significantly cleaner, but Python was being dumb, so everything is
    in terms of bytes, making it a pain to convert.


    These fields are represented in the struct as:
    vbrStruct[0:2]:   Assembly instruction to jump to boot code (3 Bytes)
    vbrStruct[3:10]:  OEM Name in ASCII (8 Bytes)
    vbrStruct[11:12]: Bytes per sector (2 Bytes)
    vbrStruct[13]:    Sectors per cluster (1 Byte)
    vbrStruct[14:15]: Size in sectors of the reserved area (2 Bytes)
    vbrStruct[16]:    Number of FATs (1 Byte)
    vbrStruct[17:18]: Maximum number of files in the root directory (2 bytes)
    vbrStruct[19:20]: 16-bit value of number of sectors in FS (FAT32: 0) (2 Bytes)
    vbrStruct[21]:    Media Type (1 Byte)
    vbrStruct[22:23]: 16-bit size of sectors of each FAT (FAT32: 0) (2 Bytes)
    vbrStruct[24:25]: Sectors per track (2 Bytes)
    vbrStruct[26:27]: Number of heads (2 Bytes)
    vbrStruct[28:31]: Number of sectors before the start of the partition (4 Bytes)
    vbrStruct[32:35]: 32-bit value of number of sectors in FS (4 Bytes)
    vbrStruct[36:39]: 32-bit size in sectors of one FAT (4 Bytes)
    '''
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

        #partitionEntryX[3] is the type of partition for partition number X
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

#Analyzes FAT16 and FAT32 VBRs
def analyzeVBR(vbrStruct, partitionNumber, partitionType, partitionStart):

    #Flip the order and put into binary for little endian, this took way too long to figure out
    reserved2 =  convertToBinary(vbrStruct[15])
    reserved1 =  convertToBinary(vbrStruct[14])

    reservedSize =  reserved2 + reserved1

    reservedSize = int(reservedSize, 2)

    #Calculate FAT area for FAT32 partitions
    if partitionType == 12 or partitionType == 11:
        fat3 = convertToBinary(vbrStruct[39])
        fat2 = convertToBinary(vbrStruct[38])
        fat1 = convertToBinary(vbrStruct[37])
        fat0 = convertToBinary(vbrStruct[36])

        fatArea = fat3 + fat2 + fat1 + fat0

    #Calculate FAT area for FAT16 partitions
    else:
        fat1 = bin(vbrStruct[23] & 0b11111111)
        fat0 = bin(vbrStruct[22] & 0b11111111)

        fat1 = string.replace(fat1, '0b', '').zfill(8)
        fat0 = string.replace(fat0, '0b', '').zfill(8)

        fatArea = fat1 + fat0


    fatArea = int(fatArea, 2)
    fatSize = fatArea*2 + reservedSize - 1

    #Calculate number of sectors root directory uses
    root1 = convertToBinary(vbrStruct[18])
    root0 = convertToBinary(vbrStruct[17])

    numOfRootDirectories = root1 + root0
    numOfRootDirectories = int(numOfRootDirectories, 2)
    rootDirectorySize = numOfRootDirectories*32/512

    addressOfCluster2 = reservedSize + fatArea*2 + rootDirectorySize + partitionStart

    print "Partition " + str(partitionNumber) + "(" + typeOfPartition(partitionType) + "):"
    print "Reserved Area: Start sector: 0 Ending Sector: " + str(reservedSize-1) + " Size: " + \
          str(reservedSize) + " sectors"
    print "Sectors per cluster: " + str(vbrStruct[13]) + " sectors"
    print "FAT area: Start sector: " + str(reservedSize) + " Ending Sector: " + str(fatSize)
    print "# of FATs: " + str(vbrStruct[16])
    print "The size of each FAT: " + str(fatArea) + " sectors"
    print "The first sector of cluster 2: " + str(addressOfCluster2) + " sectors"

#Prints the data in a preformatted string to the console
def analyzePartitionEntry(partitionStruct):
    print "(" + format(partitionStruct[3], '02x') + ") " + \
          typeOfPartition(partitionStruct[3]) + ", " + str(partitionStruct[6]).zfill(10) + ", " +\
          str(partitionStruct[7]).zfill(10)


#Returns the type of partition
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

#Determines if value in partitiony entry corresponds to a FAT16/32 value
def isFAT(partitionType):
    if partitionType == 4 or partitionType == 6 or partitionType == 11 or partitionType == 12:
        return True
    else:
        return False

#It's main, it calls the other functions.
def main():
    filePath = sys.argv[1]
    printCheckSums(filePath)
    analyzeImage(filePath)

#Converts a byte to a binary bit string
def convertToBinary(byteToConvert):
    binaryString = bin(byteToConvert & 0b11111111)
    binaryString = string.replace(binaryString, '0b', '').zfill(8)
    return binaryString

if __name__== "__main__":
    main()

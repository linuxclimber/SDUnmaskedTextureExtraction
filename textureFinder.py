#!/usr/bin/python3
import os.path
from curses.ascii import islower, isupper, isalpha, isdigit
from os import path, mkdir, rename
import textureExtractor as texExtract
import sys, getopt

def main(argv):
    iFile = ""
    oFolder = ""
    try:
       opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
       print('test.py -i <inputfile> -o <outputfolder>')
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          print('test.py -i <inputfile> -o <outputfolder>')
          sys.exit()
       elif opt in ("-i", "--ifile"):
          iFile = arg
       elif opt in ("-o", "--ofolder"):
          oFolder = arg

    if iFile == "":
        iFile = "TEXDIC.htd"
    if oFolder == "":
        oFolder = input("Enter desired texture folder name: ")


    if not path.exists(iFile):
        print(iFile, " not found!  Please make sure '", iFile, "' exists before running")
        exit()
    textures = findTextures(iFile)
    print("Found ", len(textures), " images to extract")
    
    for tName in (textures):
        texExtract.extractTexture(iFile, tName)
    rename("textures", oFolder)
    mkdir("textures")

def findTextures(iFilename):
    f = open(iFilename, "rb")
    textures = []
    prevBytes = []
    while True:
        currByte = f.read(1)
        if not currByte:
            break #eof

        prevBytes.append(currByte)
        hexStr = b''.join(prevBytes[-8:]).hex()
        if hexStr == "0000000e00000000" or hexStr == "0000000600000000":
            index = -17
            while len(prevBytes)+index > 1 and index > -100:
                if prevBytes[index].hex() == "00":
                    isFilename, startIndex = fnCheck(prevBytes, index)
                    if isFilename:
                        fnStr = b''.join(prevBytes[startIndex:index]).decode("utf-8")
                        textures.append(fnStr)
                        prevBytes = []
                        break
                index -= 1
        
    return textures

def fnCheck(prevBytes, index):
    i = index - 1
    matchedBytes = 0
    prevByte = prevBytes[i+1]
    matchNull = True
    while len(prevBytes)+i > 1:
        currByte = prevBytes[i]
        if shouldMatch(currByte, prevByte, matchedBytes, matchNull):
            if currByte.hex() == "00":
                matchNull = False
            matchedBytes += 1
        else:
            if matchedBytes >= 2:
                if (matchedBytes == 2 and prevByte.hex() == "00"):
                    return False, i
                if (prevByte.hex() == "00"):
                    i += 1
                return True, i+1
            return False, i
        prevByte = currByte
        i -= 1
    return False, i

def shouldMatch(currByte, prevByte, matchedBytes, matchNull):
    currByteI = int.from_bytes(currByte, "big")
    prevByteI = int.from_bytes(prevByte, "big")
    shouldMatch = False

    if (islower(currByteI) or isdigit(currByteI)):
        shouldMatch = True
    elif (isupper(currByteI) and (not isupper(prevByteI))):
        shouldMatch = True
    elif currByte.hex() == "5f" or (matchNull and currByte.hex() == "00" and prevByte.hex() != "00"):
        shouldMatch = True
    return shouldMatch

if __name__ == "__main__":
    main(sys.argv[1:])

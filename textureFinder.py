#!/usr/bin/python3
import os.path
from curses.ascii import islower, isupper, isalpha, isdigit
from os import path, mkdir, rename
import textureExtractor as texExtract

def main():
    if not path.exists("TEXDIC.htd"):
        print("TEXDIC.htd not found!  Please copy a TEXDIC file into this folder to continue")
        exit()
    textures = findCMPRTextures()
    print(textures)
    newFolderName = input("Enter desired texture folder name: ")
    for tName in (textures):
        texExtract.extractTexture(tName)
    rename("textures", newFolderName)
    mkdir("textures")

def findCMPRTextures():
    f = open("TEXDIC.htd", "rb")
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
    while len(prevBytes)+i > 1:
        currByte = prevBytes[i]
        if shouldMatch(currByte, prevByte, matchedBytes):
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

def shouldMatch(currByte, prevByte, matchedBytes):
    currByteI = int.from_bytes(currByte, "big")
    prevByteI = int.from_bytes(prevByte, "big")
    shouldMatch = False

    if (islower(currByteI) or isdigit(currByteI)):
        shouldMatch = True
    elif (isupper(currByteI) and (not isupper(prevByteI))):
        shouldMatch = True
    elif currByte.hex() == "5f" or (currByte.hex() == "00" and prevByte.hex() != "00"):
        shouldMatch = True
    return shouldMatch

if __name__ == "__main__":
    main()

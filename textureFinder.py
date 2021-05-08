#!/usr/bin/python3
import os.path
from curses.ascii import isalpha, isdigit
from os import path, mkdir, rename
import textureExtractor as texExtract

def main():
    if not path.exists("TEXDIC.htd"):
        print("TEXDIC.htd not found!  Please copy a TEXDIC file into this folder to continue")
        exit()
    textures = findCMPRTextures()
    print(textures)
    for tName in (textures):
        texExtract.extractTexture(tName)
    newFolderName = input("Enter desired texture folder name: ")
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
            #print("CMPR Texture found.  Getting filename now")
            while len(prevBytes)+index > 1 and index > -70:
                #print(prevBytes[index].hex)
                if prevBytes[index].hex() == "00":
                    #print("Checking if filename")
                    isFilename, startIndex = fnCheck(prevBytes, index)
                    if isFilename:
                        #print(b''.join(prevBytes[startIndex:index]))
                        textures.append(b''.join(prevBytes[startIndex:index]).decode("utf-8"))
                        prevBytes = []
                        break
                index -= 1
        
    return textures

def fnCheck(prevBytes, index):
    #print("Checking filename")
    i = index - 1
    matchedBytes = 0
    while len(prevBytes)+i > 1:
        currByte = prevBytes[i]
        #print("currByte: " + str(currByte))
        if isalpha(int.from_bytes(currByte, "big")) or isdigit(int.from_bytes(currByte, "big")) or currByte.hex() == "5f":
            matchedBytes += 1
            #print(b''.join(prevBytes[i:index]))
        else:
            if matchedBytes >= 6:
                return True, i+1
            return False, i
        i -= 1
    return False, i

if __name__ == "__main__":
    main()

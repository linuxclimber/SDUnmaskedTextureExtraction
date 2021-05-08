#!/usr/bin/python3

import os.path
from os import path

from PIL import Image
import numpy as np
from curses.ascii import islower, isdigit

def main():
    if not path.exists("TEXDIC.htd"):
        print("TEXDIC.htd not found!  Please copy a TEXDIC file into this folder to continue")
        exit()
    textureName = input("Enter the texture name you want to extract: ")
    extractTexture(textureName)
    
def extractTexture(textureName):
    #print("Attempting to extract " + textureName + " from TEXDIC.htd")
    f = open("TEXDIC.htd", "rb")
    matchedBytes = 0
    prevByte = None
    
    while True:
        currByte = f.read(1)
        if not currByte:
            #eof
            print("Texture: '" + textureName + " not found in file")
            exit()

        if currByte == textureName[matchedBytes].encode('utf-8'):
            if matchedBytes == 0 and (islower(int.from_bytes(prevByte, "big")) or isdigit(int.from_bytes(prevByte, "big")) or prevByte.hex() == "5f"):
                matchedBytes = 0
            else:
                matchedBytes += 1
        else:
            matchedBytes = 0

        if (matchedBytes >= len(textureName)):
            if f.read(1).hex() == "00":
                break
            else:
                matchedBytes = 0

        prevByte = currByte




    #print("Successfully found texture '" + textureName + "' in file! Extracting...")
    #Skip over the unknown metadata stuff
    prevBytes = []
    consecutiveNulls = 0
    iTypeHex = ""
    while True:
        currByte = f.read(1)
        prevBytes.append(currByte)

        if not currByte:
            print("End of file reached while searching for image metadata!")
            break #eof
        
        if currByte.hex() == "00":
            consecutiveNulls += 1
            if (consecutiveNulls == 4) and (f.tell() % 4 == 0):
                iTypeHex = b''.join(prevBytes[-8:-4]).hex()
                if (iTypeHex == "00000006" or iTypeHex == "0000000e"):
                    break
        else:
            consecutiveNulls = 0


        
    #Read the height/width
    width = int.from_bytes(b''.join(prevBytes[-16:-12]), byteorder='big')
    height = int.from_bytes(b''.join(prevBytes[-12:-8]), byteorder='big')
    #print("Texture Size: " + str(width) + "x" + str(height))

    if width <=0 or height <= 0:
        print("Invalid size.  Skipping")
        return
    
    if width > 1920 or height > 1080:
        print("Texture size too large. Skipping")
        return

    iTypeHex = b''.join(prevBytes[-8:-4]).hex()

    if iTypeHex == "0000000e":
        imageBytes = (width*height)//2
        imageData = f.read(imageBytes)
        f.read(32)
        createPNGFromCMPR(width, height, imageData, textureName)
    elif iTypeHex == "00000006":
        imageBytes = width*height*4
        imageData = f.read(imageBytes)
        createPNGFromRGBA32(width, height, imageData, textureName)
    else:
        print("Not a CMPR or RGBA32 image- may not extract properly")
        return
        

         
def createPNGFromRGBA32(width, height, imageData, fileName):
    full = [0]*4
    full = [full]*width
    full = [full]*height
    full = np.array(full, dtype=np.uint8)
    
    blockSize=4
    for x in range(height//blockSize):
        for y in range(width//blockSize):
            imageData, block = generateNextRGBA32Block(imageData)
            for blockx in range(blockSize):
                for blocky in range(blockSize):
                    full[(x*blockSize) + blockx, (y*blockSize) + blocky, 0] = block[blockx,blocky,0]
                    full[(x*blockSize) + blockx, (y*blockSize) + blocky, 1] = block[blockx,blocky,1]
                    full[(x*blockSize) + blockx, (y*blockSize) + blocky, 2] = block[blockx,blocky,2]
                    full[(x*blockSize) + blockx, (y*blockSize) + blocky, 3] = block[blockx,blocky,3]

    new_image = Image.fromarray(full, "RGBA")
    new_image.save("textures/" + fileName + ".png")


def createPNGFromCMPR(width, height, imageData, fileName):
    full = [0]*4
    full = [full]*width
    full = [full]*height
    full = np.array(full, dtype=np.uint8)
    
    for x in range(height//8):
        for y in range(width//8):
            imageData, block = generateNextCMPRBlock(imageData)
            for blockx in range(8):
                for blocky in range(8):
                    full[(x*8) + blockx, (y*8) + blocky, 0] = block[blockx,blocky,0]
                    full[(x*8) + blockx, (y*8) + blocky, 1] = block[blockx,blocky,1]
                    full[(x*8) + blockx, (y*8) + blocky, 2] = block[blockx,blocky,2]
                    full[(x*8) + blockx, (y*8) + blocky, 3] = block[blockx,blocky,3]

    new_image = Image.fromarray(full, "RGBA")
    new_image.save("textures/" + fileName + ".png")

def generateNextCMPRBlock(imageData):
    block=[0]*4
    block=[block]*8
    block=[block]*8
    block = np.array(block, dtype=np.uint8)
    for x in range(2):
        for y in range(2):
            imageData, subBlock = generateCMPRSubBlock(imageData)
            for subx in range(4):
                for suby in range(4):
                    block[(x*4) + subx, (y*4) + suby, 0] = subBlock[subx,suby,0]
                    block[(x*4) + subx, (y*4) + suby, 1] = subBlock[subx,suby,1]
                    block[(x*4) + subx, (y*4) + suby, 2] = subBlock[subx,suby,2]
                    block[(x*4) + subx, (y*4) + suby, 3] = subBlock[subx,suby,3]
    return imageData, block

def generateNextRGBA32Block(imageData):
    block=[0]*4
    block=[block]*4
    block=[block]*4
    block = np.array(block, dtype=np.uint8)

    i = 0

    for x in range(4):
        for y in range(4):
            block[x,y,3] = imageData[i]
            block[x,y,0] = imageData[i+1]
            i += 2

    for x in range(4):
        for y in range(4):
            block[x,y,1] = imageData[i]
            block[x,y,2] = imageData[i+1]
            i += 2

    return imageData[64:], block


def generateCMPRSubBlock(imageData):
    sub=[0]*4
    sub=[sub]*4
    sub=[sub]*4
    sub = np.array(sub, dtype=np.uint8)

    color0 = convertRGB(int.from_bytes(imageData[0:2], byteorder="big"))
    color1 = convertRGB(int.from_bytes(imageData[2:4], byteorder="big"))
    color2, color3 = getOtherColors(color0, color1)
    colors = [color0, color1, color2, color3]

    for x in range(4):
        rowByte = imageData[4+x]
        for y in range(4):
            RGB = colors[(rowByte >> ((3-y)*2) & 0b11)]
            sub[x,y,0] = RGB[0]
            sub[x,y,1] = RGB[1]
            sub[x,y,2] = RGB[2]
            sub[x,y,3] = RGB[3]
    return imageData[8:], sub


def convertRGB(RGB565):
    R = (RGB565 & 0b1111100000000000) >> 8
    G = (RGB565 & 0b0000011111100000) >> 3
    B = (RGB565 & 0b0000000000011111) << 3
    return [R, G, B, 0xFF]

def getOtherColors(c0, c1):
    c2 = [0,0,0,0xFF]
    c3 = [0,0,0,0xFF]
    if c0 > c1:
        for i in range(3):
            interval = abs(c0[i]-c1[i])/3
            c2[i] = round(min(c0[i], c1[i]) + interval)
            c3[i] = round(max(c0[i], c1[i]) - interval)
    else:
        c3[3] = 0x00 #Set last color to transparent
        for i in range(3):
            c2[i] = (c0[i] + c1[i])//2

    return c2, c3

if __name__ == "__main__":
    main()

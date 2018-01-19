"""
Description:
Functions to extract apple loop meta data from .caf files

Authors:
Chris Misa, chris@chrismisa.com
"""

import sys
import mmap
import struct

APPLE_LOOP_METADATA_UUID = "\x29\x81\x92\x73\xb5\xbf\x4a\xef\xb7\x8d\x62\xd1\xef\x90\xbb\x2c"

def getMetaDataChunk(filepath):
  """
    Opens the given file, finds the uuid chunk with meta data uuid,
    dumps the data section minus headers and uuid as string
  """
  with open(filepath, "r+b") as f:
    cafData = mmap.mmap(f.fileno(), 0)
    addr = 0
    while True:
      addr = cafData.find(b"uuid")
      dataLength, dataUUID = struct.unpack(">Q16s", cafData[addr + 4 : addr + 28])
      if dataUUID == APPLE_LOOP_METADATA_UUID:
        return cafData[addr+28:addr+dataLength+12]

def decodeMetaData(md):
  """
    Converts the given meta data chunk into a dict
  """
  num, = struct.unpack(">L", md[0:4])
  result = {}
  mdSplit = md[4:].split("\x00")
  for i in range(0, len(mdSplit) - 1, 2):
    key = mdSplit[i].replace(" ", "_")
    result[key] = mdSplit[i+1]
  return result

def loadMetaData(filepath):
  """
    Convenience method to properly call getMetaDataChunk and decodeMetaData.
    Returns a dictionary with meta data extracted form the given file
  """
  return decodeMetaData(getMetaDataChunk(filepath))

def main():
  print(str(loadMetaData(sys.argv[1])))

if __name__ == "__main__":
  main()

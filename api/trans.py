"""

Get transposition track data.

Note: Note data is already transposed when saved in regions.

"""


import sys
import mmap
import struct
import pprint

TRANS_CHUNK_TAG = "\x71\x53\x76\x45\x01\x00\x19"
TIME_OFFSET = 0x9600
VALUE_OFFSET = 0x3c00
VALUE_SCALE = 256

def getTransChunk(pd):
  """
    Finds and returns the transposition chunk from given
    mmap'd ProjectData file
  """
  transAddr = pd.find(TRANS_CHUNK_TAG)
  (chunkSize,) = struct.unpack("<Q", pd[transAddr+28:transAddr+36])
  return pd[transAddr+36:transAddr+36+chunkSize]

def decodeTransChunk(t):
  """
    Split the given transposition chunk into records,
    pull out points, return as array of dicts: {time: , value}
  """
  offset = 0
  points = []
  while t[offset] == "\x70":
    time, value = struct.unpack("<4xL13xH", t[offset:offset+0x17])
    time -= TIME_OFFSET
    value -= VALUE_OFFSET
    value /= VALUE_SCALE
    points.append({"time":time, "value":value})
    offset += 0x30
  return points

def main():
  with open(sys.argv[1],'r+b') as f:
    pd = mmap.mmap(f.fileno(),0)
    #sys.stdout.write(getTransChunk(pd))
    trans = decodeTransChunk(getTransChunk(pd))
    pprint.pprint(trans)

if __name__ == "__main__":
  main()

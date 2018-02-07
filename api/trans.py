"""

Get transposition track data.

Might not be necessary if GB actually stores regions as transposed,
as it seems to more them in the display as transposition move.

Still, this track would provide a simpler centralized method for
decerning properly realized transpositions.

The data chunk seems to be formed from 0x40-byte records.
offset 0x15 to 0x16 is some two-byte transposition value.
offset 0x2 is probably some 8-byte time code.

"""


import sys
import mmap
import struct

TRANS_CHUNK_TAG = "\x71\x53\x76\x45\x01\x00\x19"

def getTransChunk(pd):
  """
    Finds and returns the transposition chunk from given
    mmap'd ProjectData file
  """
  transAddr = pd.find(TRANS_CHUNK_TAG)
  (chunkSize,) = struct.unpack("<Q", pd[transAddr+28:transAddr+36])
  return pd[transAddr+36:transAddr+36+chunkSize]

def main():
  with open(sys.argv[1],'r+b') as f:
    pd = mmap.mmap(f.fileno(),0)
    sys.stdout.write(getTransChunk(pd))

if __name__ == "__main__":
  main()

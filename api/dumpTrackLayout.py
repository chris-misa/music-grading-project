"""
  Dumps track layout information
"""

import sys
import mmap
import pprint

ARR_HEADER_TAG = "\x71\x65\x53\x4d\x02\x00\x17\x00\x00\x00\x04"
KART_TAG = "\x6b\x61\x72\x54\x04\x00\x17"

def getTrackEntries(pd):
  """
    Returns karT track entries
  """
  arrAddr = pd.find(ARR_HEADER_TAG)
  startAddr = pd.find(KART_TAG,arrAddr)
  karts = []
  while pd[startAddr:startAddr+7] == KART_TAG:
    karts.append(pd[startAddr:startAddr+0x5c])
    startAddr += 0x5c
  return karts

def main():
  with open(sys.argv[1],'r+b') as f:
    mm = mmap.mmap(f.fileno(),0)
    t = getTrackEntries(mm)
    sys.stdout.write(('\xff'*4).join(t))

if __name__ == "__main__":
  main()

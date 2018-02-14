import struct
import mmap
import sys
import pprint

UCUA_TAG_BASE = "\x55\x43\x75\x41\x01\x00\x0e\x00\x00\x00\x24"

LENGTH_OFFSET = 0x1c

def getUCUAChunk(pd, start, end):
  startAddr = pd.find(UCUA_TAG_BASE, start, end)
  if startAddr == -1:
    return
  length, = struct.unpack("<L", pd[startAddr+LENGTH_OFFSET:startAddr+LENGTH_OFFSET+4])
  dataStart = startAddr+LENGTH_OFFSET+8
  return (pd[dataStart:dataStart+length], dataStart)

def getUCUAChunks(pd, instTag):
  instAddr = pd.find(instTag)
  ocuaAddr = pd.find("OCuA", instAddr)
  chunks = []
  while True:
    c = getUCUAChunk(pd, instAddr, ocuaAddr)
    if c == None:
      break
    chunk, instAddr = c
    chunks.append(chunk)
  return chunks

def getTrackInfo(pd, instTag):
  """
    Returns the gain, and first two sends of the given track
  """
  chunks = getUCUAChunks(pd, instTag)
  send1, = struct.unpack("<L", chunks[0][0x18:0x1c])
  send2, = struct.unpack("<L", chunks[1][0x18:0x1c])
  gain = None
  for c in chunks:
    if "Gain" in c:
      gain, = struct.unpack("<f", c[0xd8:0xdc])
  return {'gain_plugin':gain, 'send1': send1, 'send2': send2}

def main():
  with open(sys.argv[1],'r+b') as f:
    mm = mmap.mmap(f.fileno(),0)
    pprint.pprint(getTrackInfo(mm, "Inst 1"))

if __name__ == "__main__":
  main()

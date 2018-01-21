"""
  Extracts MIDI data from a given ProjectData file
"""
import struct
import sys
import mmap #qSvE tag of arrangement data chunk
ARRANGMENT_CHUNK_TAG = "\x71\x53\x76\x45\x01\x00\x17\x00\x00\x00\x04"
NO_LOOP_VALUE = 0x3FFFFFFF00000000
START_TIME_OFFSET = 0x8700

def getArrChunk(pd):
  """
    Finds and returns the arrangment chunk from the given mmap'ed
    ProjectData file
  """
  arrChunkAddr = pd.find(ARRANGMENT_CHUNK_TAG)
  (chunkSize,) = struct.unpack("<Q", pd[arrChunkAddr+28:arrChunkAddr+36])
  return pd[arrChunkAddr+36:arrChunkAddr+36+chunkSize]

def decodeArrChunk(arrChunk):
  """
    Breaks the given arrangment chunk into events
    returns a list of events
  """
  events = []
  offset = 0
  while arrChunk[offset:offset+8] != "\xf1\x00\x00\x00\xff\xff\xff\x3f":
    events.append(decodeArrEvent(arrChunk[offset:offset+0x50]))
    offset += 0x50
  return events
      

def decodeArrEvent(e):
  """
    Interprits the arrangement chunk's event structs
  """
  eventType, startTime, trackID, loopTime, eventID = \
     struct.unpack("<L L 12x B 3x Q L", e[0:36])
  # Only the upper 6 bytes of loopTime seem to mater
  loopTime = loopTime >> 16 if loopTime != NO_LOOP_VALUE else None
  # Normalize start times
  startTime -= START_TIME_OFFSET
  return {"type":eventType, "start":startTime, "track_id":trackID, \
          "loop_time":loopTime, "id":eventID}

def main():
  """
    Main mostly for testing
  """
  with open(sys.argv[1],'r+b') as f:
    mm = mmap.mmap(f.fileno(), 0)
    events = decodeArrChunk(getArrChunk(mm))
    for e in events:
      print(str(e))

if __name__ == "__main__":
  main()

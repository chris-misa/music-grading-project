"""
  Extracts MIDI data from a given ProjectData file

In progress:

Mapping from global track numer to inst track number
Realization of looped segments

"""
import struct
import sys
import mmap
import pprint

ARRANGMENT_CHUNK_TAG = "\x71\x53\x76\x45\x01\x00\x17\x00\x00\x00\x04"
EVENT_CHUNK_HEADER_TAG = "\x71\x65\x53\x4d\x02\x00\x17\x00\x00\x00"
EVENT_CHUNK_TAG = "\x71\x53\x76\x45\x01\x00\x17\x00\x00\x00"
END_OF_LIST_SENTINEL = "\xf1\x00\x00\x00\xff\xff\xff\x3f"
NO_LOOP_VALUE = 0x3FFFFFFF
EVENT_START_TIME_OFFSET = 0x8700
NOTE_START_TIME_OFFSET = 0x9600

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
  while arrChunk[offset:offset+8] != END_OF_LIST_SENTINEL:
    events.append(decodeArrEvent(arrChunk[offset:offset+0x50]))
    offset += 0x50
  return events
      

def decodeArrEvent(e):
  """
    Interprits the arrangement chunk's event structs
  """
  eventType, startTime, trackID, loopTime, eventID = \
     struct.unpack("<L L 12x B 7x L 4s", e[0:36])
  loopTime = loopTime if loopTime != NO_LOOP_VALUE else None
  # Normalize start times
  startTime -= EVENT_START_TIME_OFFSET
  return {"type":eventType, "start":startTime, "track_id":trackID, \
          "loop_time":loopTime, "id":eventID}

def getEventChunk(pd, eventID, startOffset = 0):
  """
    Finds and returns the event chunk with the given id from the mmap'ed
    ProjectData file
    Returns a tuple with first element as qeSM header chunk and second
    as qSvE body chunk
  """
  eventHeaderAddr = pd.find(EVENT_CHUNK_HEADER_TAG + eventID, startOffset)
  eventBodyAddr = pd.find(EVENT_CHUNK_TAG + eventID, eventHeaderAddr)
  (chunkSize,) = struct.unpack("<Q", pd[eventBodyAddr+28:eventBodyAddr+36])
  eventHeader = pd[eventHeaderAddr:eventBodyAddr]
  eventBody = pd[eventBodyAddr+36:eventBodyAddr+36+chunkSize]
  return (eventHeader, eventBody)


def decodeEventHeader(header):
  """
    Pulls interesting data from the given event header
    Returns as a dictionary
  """
  nameLength, = struct.unpack("<H", header[0x34:0x36])
  # subsiquent addresses are align 2
  nameLength = nameLength if nameLength % 2 == 0 else nameLength + 1
  startOffsetAddr = 0x3a + nameLength
  lengthAddr = 0x72 + nameLength
  startOffset, = struct.unpack("<L", header[startOffsetAddr:startOffsetAddr+4])
  length, = struct.unpack("<L", header[lengthAddr:lengthAddr+4])
  return {"length":length,"start_offset":startOffset}

def decodeEventBody(body, startOffset):
  """
    Converts the data in the event body into note events
    Returns a list of dicts
  """
  offset = 0
  notes = []
  bodyLen = len(body) - 4
  while body[offset:offset+8] != END_OF_LIST_SENTINEL and offset < bodyLen:
    if body[offset:offset+4] == "\xC0\x00\x00\x00":
      # start of event marker: skipping for now
      offset += 16
    elif body[offset:offset+4] == "\xb0\x00\x00\x00":
      # modulation or cc events: skipped
      offset += 16
    elif body[offset:offset+4] == "\xe0\x00\x00\x00":
      # pitch bend events: skipped
      offset += 16
    elif body[offset:offset+4] == "\x90\x00\x00\x00":
      # note event
      time, vel, pitch, dur = struct.unpack("<7s B B 15x L",body[offset+4:offset+32])
      # hack the 7 bytes into an 8 byte int
      time, = struct.unpack("<Q", time + "\x00")
      time -= NOTE_START_TIME_OFFSET + startOffset
      notes.append({"time":time, "vel":vel, "pitch":pitch, "duration":dur})
      offset += 32
    else:
      # Assume that things are 16 byte aligned so unknown sections will wrap at 16 bytes
      offset += 16
  return notes

def cropNotes(notes, length):
  """
    Cuts off all notes after length or before time = 0
    Adjust last note's duration to make sure it doesn't exceed length
    Returns the modified note list
  """
  startIndex = 0
  endIndex = len(notes) - 1
  while notes[startIndex]['time'] < 0 and startIndex < endIndex:
    startIndex += 1
  while notes[endIndex]['time'] >= length and endIndex > 0:
    endIndex -= 1
  if notes[endIndex]['time'] + notes[endIndex]['duration'] > length:
    notes[endIndex]['duration'] = length - notes[endIndex]['time']
  return notes[startIndex:endIndex+1]

def assembleTracks(pd, events):
  """
    Performs lookups, translations, and grouping of a list of event dictionaries
    Events are merged into their tracks using the above crop function to handle notes
    Which don't actually fall into the event
    Returns a list of track dictionaries
  """ 
  tracks = {}
  for e in events:
    if e['type'] == 32: # Instrument event
      h, b = getEventChunk(pd, e['id'])
      #sys.stdout.write(h + "\xee"*16 + b + "\xff"*16)
      header = decodeEventHeader(h)
      notes = decodeEventBody(b, header['start_offset'])
      notes = cropNotes(notes, header['length'])
      if e['track_id'] not in tracks.keys(): # set up a new track if needed
        tracks[e['track_id']] = {'notes':[]}
      for n in notes:
        n['time'] += e['start'] # add event start time to note start times
        tracks[e['track_id']]['notes'].append(n)
  return tracks
  
def main():
  with open(sys.argv[1],'r+b') as f:
    mm = mmap.mmap(f.fileno(), 0)
    events = decodeArrChunk(getArrChunk(mm))
    tracks = assembleTracks(mm, events)
    pprint.pprint(tracks)
    

if __name__ == "__main__":
  main()

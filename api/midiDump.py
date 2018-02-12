"""
  Description: Extracts MIDI data from a given GarageBand file

  Author: Chris Misa, chris@chrismisa.com

  Dependencies: python-midi (https://github.com/vishnubob/python-midi.git)
                  -> for writeToMIDIFile()
"""
import struct
import sys
import mmap
import pprint
import os
import argparse
import heapq
import copy
import re

import midi

ARR_HEADER_TAG = "\x71\x65\x53\x4d\x02\x00\x17\x00\x00\x00\x04"
KART_TAG = "\x6b\x61\x72\x54\x04\x00\x17"
IVNE_TAG_BASE = "\x69\x76\x6e\x45\x04\x00\x14\x00\x00\x00"
ARRANGMENT_CHUNK_TAG = "\x71\x53\x76\x45\x01\x00\x17\x00\x00\x00\x04"
EVENT_CHUNK_HEADER_TAG = "\x71\x65\x53\x4d\x02\x00\x17\x00\x00\x00"
EVENT_CHUNK_TAG = "\x71\x53\x76\x45\x01\x00\x17\x00\x00\x00"
END_OF_LIST_SENTINEL = "\xf1\x00\x00\x00\xff\xff\xff\x3f"
NO_LOOP_VALUE = 0x3FFFFFFF
EVENT_START_TIME_OFFSET = 0x8700
NOTE_START_TIME_OFFSET = 0x9600


#
# Functions for getting track labels (names)
#####################################################

def getTrackEntries(pd):
  """
    Returns karT arrangment header track entries
  """
  arrAddr = pd.find(ARR_HEADER_TAG)
  startAddr = pd.find(KART_TAG,arrAddr)
  karts = []
  while pd[startAddr:startAddr+7] == KART_TAG:
    karts.append(pd[startAddr:startAddr+0x5c])
    startAddr += 0x5c
  return karts

def getLabelEntry(pd, labelID):
  """
    Returns the label chunk for the given id
    by looking up the ivnE tag
  """
  startAddr = pd.find(IVNE_TAG_BASE + labelID)
  length, = struct.unpack("<L", pd[startAddr+28:startAddr+32])
  return pd[startAddr+36:startAddr+36+length]

def collectTrackLabels(pd):
  """
    Collects labels for each track
    return: array of track labels
  """
  arrTracks = getTrackEntries(pd)
  labels = []
  for t in arrTracks:
    tag = t[0x2c:0x2e]
    labelChunk = getLabelEntry(pd, tag)
    nameLen, = struct.unpack("<H", labelChunk[0x9E:0xA0])
    name = labelChunk[0xA0:0xA0+nameLen]
    labels.append((name, tag))
  return labels

#
# Parsing main events structure
#############################################

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
     struct.unpack("<H 2x L 12x B 7x L 4s", e[0:36])
  loopTime = loopTime if loopTime != NO_LOOP_VALUE else None
  # Normalize start times
  startTime -= EVENT_START_TIME_OFFSET
  return {"type":eventType, "start":startTime, "track_id":trackID, \
          "loop_time":loopTime, "id":eventID}

#
# Finding and interpriting Event headers and bodies
########################################################

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
  return {"length":length, "start_offset":startOffset,\
      "region_name":header[0x36:0x36+nameLength].strip('\x00')}

def decodeEventBody(body, startOffset):
  """
    Converts the data in the event body into note events
    Returns a list of dicts
  """
  offset = 0
  notes = []
  bodyLen = len(body) - 4
  while body[offset:offset+8] != END_OF_LIST_SENTINEL and offset < bodyLen:
    if body[offset:offset+2] == "\xC0\x00":
      # start of event marker: skipping for now
      offset += 16
    elif body[offset:offset+2] == "\xb0\x00":
      # modulation or cc events: skipped
      offset += 16
    elif body[offset:offset+2] == "\xe0\x00":
      # pitch bend events: skipped
      offset += 16
    elif body[offset:offset+2] == "\x90\x00":
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

#
# Auxilary functions for dealing with GarageBand features
#############################################################

def getCurrentTake(header, body):
  """
    Handle multiple takes in same region.
    Basically we have the same structure as the arrangement header, body.
    Returns the eventID of the currently selected event.
  """
  # Find a karT entry with 00 at position 0x27 -> the selected take
  startAddr = header.find(KART_TAG)
  while header[startAddr:startAddr+7] == KART_TAG:
    kart = header[startAddr:startAddr+0x5c]
    if kart[0x27] == "\x00":
      curEvent, = struct.unpack("B", kart[0x12])
      break
    startAddr += 0x5c
  # Just in case,
  if curEvent == None:
    return
  # Jump to the relevant chunk and grab the eventID
  return body[0x50 * curEvent + 0x20]

def cropNotes(notes, length):
  """
    Cuts off all notes after length or before time = 0
    Adjust last note's duration to make sure it doesn't exceed length
    Returns the modified note list
  """
  startIndex = 0
  endIndex = len(notes) - 1
  while startIndex < endIndex and notes[startIndex]['time'] < 0:
    startIndex += 1
  while endIndex > 0 and notes[endIndex]['time'] >= length:
    endIndex -= 1
  for i in range(startIndex,endIndex+1):
    if notes[i]['time'] + notes[i]['duration'] > length:
      notes[i]['duration'] = length - notes[i]['time']
  return notes[startIndex:endIndex+1]

def loopNotes(notes, length, loopDuration):
  """
    Repeate the events between time = 0 and time = length until time = loopDuration
    Assumes the event has already been cropped (note times all between 0 and length)
    Returns the modified note list
  """
  scope = len(notes)
  i = 0
  start = length
  while notes[i]['time'] + start < loopDuration:
    newNote = copy.copy(notes[i])
    newNote['time'] += start
    if newNote['time'] + newNote['duration'] > loopDuration:
      newNote['duration'] = loopDuration - newNote['time']
    notes.append(newNote)
    i += 1
    if i == scope:
      i = 0
      start += length
  return notes

def assembleTracks(pd, events):
  """
    Performs lookups, translations, and grouping of a list of region dictionaries
    Regions are merged into their tracks using the above crop function to handle notes
    which don't actually fall into the region boundaries.
    Returns a list of track dictionaries
  """ 
  tracks = {}
  for e in events:
    if e['type'] == 32: # Instrument event
      h, b = getEventChunk(pd, e['id'])
      # Check if there are multiple takes
      if b[0] == "\x20":
        curTake = getCurrentTake(h, b)
        if curTake != None:
          h, b = getEventChunk(pd, curTake)
        else: # Give up
          print("Dropped multi-take region tagged {}".format(hex(e['id'])))
          continue
      header = decodeEventHeader(h)
      notes = decodeEventBody(b, header['start_offset'])
      notes = cropNotes(notes, header['length'])
      regionLength = header['length']
      if e['loop_time'] != None:
        notes = loopNotes(notes, header['length'], e['loop_time'])
        regionLength = e['loop_time']
      # set up a new track if needed
      if e['track_id'] not in tracks.keys():
        tracks[e['track_id']] = {'notes':[], 'type':'instrument', 'regions':[]}
      # Add region data
      tracks[e['track_id']]['regions'].append({'name':header['region_name'], \
          'start':e['start'], 'length':regionLength, 'notes':notes})
      # Add note stream
      for n in notes:
        newNote = copy.copy(n)
        newNote['time'] += e['start'] # add event start time to note start times
        tracks[e['track_id']]['notes'].append(newNote)
    else:
      if e['track_id'] not in tracks.keys(): # set up a new track if needed
        tracks[e['track_id']] = {'type':'audio'}
  # Add track labels and convert tracks into list
  labels = collectTrackLabels(pd)
  for i, l in enumerate(labels):
    # Skip deactivated tracks which seem to be product of multiple takes
    if l[0] == "No Output":
      continue
    # Make a new empty track incase there were no events
    if i+1 not in tracks.keys():
      tracks[i+1] = {'type':'empty'}
    label, tag = l
    tracks[i+1]["label"] = label
    tracks[i+1]["tag"], = struct.unpack("<H", tag)
  return tracks
  
#  
# File handling functions
############################

PATH_TO_PROJECT = "Alternatives/000"

def getProjectData(fp):
  """Returns ProjectData file in an mmap object"""
  pdPath = os.path.join(fp, PATH_TO_PROJECT, "ProjectData")
  with open(pdPath, "r+b") as f:
    mm = mmap.mmap(f.fileno(), 0)
    return mm

# Time resolution to convert GarageBand times to MIDI ticks
GB_NOTE_RESOLUTION = 960

def writeToMIDIFile(tracks, filepath):
  """Writes the tracks to a standard MIDI file"""
  pattern = midi.Pattern()
  pattern.resolution = GB_NOTE_RESOLUTION
  for t in tracks.values():
    if t['type'] == 'instrument':
      track = midi.Track()
      pattern.append(track)
      offs = []
      currentTime = 0
      # Go through each note in track interleaving into on/off events
      for n in t['notes']:
        # Insert note off events from queue
        while len(offs) > 0 and offs[0][0] < n['time']:
          off = heapq.heappop(offs)
          dif = off[0] - currentTime
          currentTime = off[0]
          offEvent = midi.NoteOffEvent(tick=dif, velocity=60, pitch=off[1])
          track.append(offEvent)
        # Add note on
        dif = n['time'] - currentTime
        currentTime = n['time']
        onEvent = midi.NoteOnEvent(tick=dif, velocity=n['vel'], pitch=n['pitch'])
        track.append(onEvent)
        # Add note off to queue
        heapq.heappush(offs, (n['time']+n['duration'], n['pitch']))
      # Insert leftover note off events from queue
      while offs:
        off = heapq.heappop(offs)
        dif = off[0] - currentTime
        currentTime = off[0]
        offEvent = midi.NoteOffEvent(tick=dif, pitch=off[1])
        track.append(offEvent)
      track.append(midi.EndOfTrackEvent(tick=1))
  midi.write_midifile(filepath, pattern)

def getTracks(pd):
  """
    Convenience method to return all track data in a dict strucure
  """
  events = decodeArrChunk(getArrChunk(pd))
  tracks = assembleTracks(pd, events)
  return tracks

def makeTracks(filepath):
  mm = getProjectData(filepath)
  events = decodeArrChunk(getArrChunk(mm))
  tracks = assembleTracks(mm, events)

  return tracks

def main():
  parser = argparse.ArgumentParser(description="Extract MIDI data from GarageBand files.")
  parser.add_argument('filepath',help="Path to GarageBand project directory")
  parser.add_argument('-o',help="Dump here as MIDI file", metavar="outfile")
  args = parser.parse_args()
  mm = getProjectData(args.filepath)
  events = decodeArrChunk(getArrChunk(mm))
  tracks = assembleTracks(mm, events)
  if args.o != None:
    writeToMIDIFile(tracks, args.o)
  else:
    pprint.pprint(tracks)
    

if __name__ == "__main__":
  main()

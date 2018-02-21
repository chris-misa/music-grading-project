"""
 Attempts to pull out information about the arragement markers

 If standalone, first argument is path to grageband project

 Still need to translate rtf formating and remove last char of plain formated
 in decodeTextChunk

 Length is in some wierd units: probably 1/4 of beats?
 This will need to be translated via time signature into measures. . .
"""

import sys
import mmap
import struct
import re

START_ARR_TAG = "\x71\x53\x76\x45\x01\x00\x05"
END_ARR_TAG = "\xf1\x00\x00\x00\xff\xff\xff\x3f"

START_TXT_TAG = "\x71\x53\x78\x54\x01\x00\x20\x00\x00\x00"

def stripRTF(txt):
  """
    Crude function to strip rtf control words and groups
  """
  txt = re.sub(r"[\n]", "", txt)
  txt = re.sub(r"\{.*\}", "", txt)
  txt = re.sub(r"\\\S*\s", "", txt)
  return txt

# Converts a text chunk given as a byte string
# returns a tuple with key, text
def decodeTextChunk( textChunk ):
  key, = struct.unpack("<I", textChunk[10:14])
  size, = struct.unpack("<I", textChunk[28:32])
  kind, = struct.unpack("B", textChunk[60])
  text = textChunk[0x48:size+36].strip("\x00}")
  # Translate rtf if needed
  if kind == 0x13:
    text = stripRTF(text)
  return {key : text}
  

# Converts an arrangement chunk given as a byte string
# returns an array of tuples with textKey, length
def decodeArrEvents( arrChunk ):
  # Compute start of arrangement data
  dataStart = 0x24
  
  # Get size of data chunk
  size, = struct.unpack("<Q", arrChunk[0x1C:0x24])

  # Break into event chunks
  chunks = [arrChunk[i:i+48] for i in range(dataStart, dataStart+size-48, 48)]

  # Parse events
  events = []
  for e in chunks:
    key, = struct.unpack("<I", e[0x10:0x14])
    length, = struct.unpack("<I", e[0x1C:0x20])
    events.append((key, length))

  return events

# Method to pull out arrangment facts from ProjectData file in a mmap
def getArr(pd):
  # Find the start of the arragement track record
  recAddr = pd.find(START_ARR_TAG)
  if recAddr == -1:
    return "Arrangement data not found"
  # Decode arrangement events into an array
  events = decodeArrEvents(pd[recAddr:])
  # Go through and decode text records
  txtAddr = recAddr
  texts = {}
  while True:
    txtAddr = pd.find(START_TXT_TAG, txtAddr + len(START_TXT_TAG))
    if txtAddr == -1:
      break
    texts.update(decodeTextChunk(pd[txtAddr:]))
  # Build result by cross-referencing texts
  result = []
  for e in events:
    tag, length = e
    text = texts[tag].strip("\x00")
    result.append((text, length))
  return result

def main():
  # Load ProjectData file into an mmap
  projectDataPath = sys.argv[1] + "/Alternatives/000/ProjectData"
  f = open(projectDataPath, "r+b")
  mm = mmap.mmap(f.fileno(), 0)
  arr = getArr(mm)
  for a in arr:
    if len(a) == 2:
      print "Length: %s, Text: %d" % a

if __name__ == "__main__":
  main()

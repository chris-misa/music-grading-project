"""
Attempts to generate a list of the tracks by name in the given GB project

Only returns software instrument tracks

If standalone, first argument is path to grageband project

Doesn't work for some tracks and probably more research is needed. . . 
"""

import sys
import mmap
import struct

GAIN_OFFSET = 0x37

def getTrackGain( pd, instAddr ):
  gainAddr = instAddr + GAIN_OFFSET
  gain, = struct.unpack("I", pd[gainAddr:gainAddr+4])
  return gain
  

def getTrackList(pd):
  tracks = []
  for i in range(1, 256):
    # Get address of inst record
    instAddr = pd.find("Inst " + str(i))
    # Get gain byte
    gain = getTrackGain(pd, instAddr)
    # Get address of OCuA marker
    ocuaAddr = pd.find(b"OCuA", instAddr)
    # Check for UCuA markers between Inst and OCuA
    p = pd.find(b"UCuA", instAddr, ocuaAddr)
    if p != -1:
      # Move to third UCuA marker
      p = pd.find(b"UCuA", p + 4)
      p = pd.find(b"UCuA", p + 4)
      # Some times there might be empty instrument slots with one UCuA. . .
      if p > ocuaAddr:
        continue
      # add offset of preset name from third UCuA marker
      p += 0x34
      # hack to strip anything after a dot from preset name:
      # apple loops generate tracks with .pst
      end = pd.find(b'.', p, p + 64)
      if end == -1:
        end = p + 64
      # append preset name
      tracks.append((i, pd[p:end].strip("\x00"), gain))
  return tracks

  
def main():
  projectDataPath = sys.argv[1] + "/Alternatives/000/ProjectData"
  f = open(projectDataPath, "r+b")
  mm = mmap.mmap(f.fileno(), 0)
  tracks = getTrackList(mm)
  for t in tracks:
    trackNumber, preset, gain = t
    print("Track " + str(trackNumber) + ": " + preset + " gain: " + str(gain))

if __name__ == "__main__":
  main()

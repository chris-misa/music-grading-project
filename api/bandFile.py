"""
Author: Chris Misa, cmisa@cs.uoregon.edu

Description:

Read a .band file created by Apple's GarageBand.
Convert certain information from the ProjectData
and MetaData.plist files into a python dict by calling

bandFile.load( file-path )


Keys of the resulting dict include:

"key" -> the key of the song as one of two characters e.x. "G"
"gender" -> "major" or "minor"
"metronome" -> True if the metronome is on, False otherwise
"arrangement" -> Returns the arrangement track as a list of tuples with form
                 (section name, duration). DURATION UNITS?
"drummer" -> Returns a list of character identifiers for all drummers in the project
             These identifiers seem to be mapped to drummer names as presented to user.
"audio_loops" -> Returns a list of audio apple loops used in the project.
"inst_tracks" -> Returns a list of the preset used to create each instrument track
                 in the project.  Each list element is a tuple with form
                 (track number, preset, channel strip gain)
                 Currently the gain is expressed as the raw 4-byte int used by
                 GarageBand internally.
                 FIGURE OUT HOW THIS MAPS TO +/- DB.
                 ADD CHECK FOR GAIN PLUGIN.

Dependencies:

ccl_bplist.py, CCL Forensics
arr.py
drummer.py
tracklist.py

If run as standalone, loads first arugment as GarageBand file and prints the
above information

"""

import mmap
import os
import struct
import io
import pprint
import sys

import ccl_bplist
import arr
import drummer
import tracklist

def load(filepath):
  try:
    projectData= getProjectData(filepath)
  except OSError as error:
    print("Failed to load ProjectData for project at {}".format(filepath))
    return
  try:
    metaData = getMetaData(filepath)
  except OSError as error:
    print("Failed to load MetaData.plist for project at {}".format(filepath))
    return
  result = {}
  result["key"] = getKey(metaData)
  result["gender"] = getGender(metaData)
  result["metronome"] = getMetronome(projectData)
  result["arrangement"] = getArrangement(projectData)
  result["drummer"] = getDrummer(projectData)
  result["audio_loops"] = getAudioLoops(projectData)
  result["inst_tracks"] = getInstTracks(projectData)
  return result

#  
# File handling functions
#

PATH_TO_PROJECT = "Alternatives/000"

def getProjectData(fp):
  """Returns ProjectData file in an mmap object"""
  pdPath = os.path.join(fp, PATH_TO_PROJECT, "ProjectData")
  with open(pdPath, "r+b") as f:
    mm = mmap.mmap(f.fileno(), 0)
    return mm

def getMetaData(fp):
  """Returns MetaData.plist as a python object via ccl_bplist"""
  mdPath = os.path.join(fp, PATH_TO_PROJECT, "MetaData.plist")
  with open(mdPath) as f:
    pl = ccl_bplist.load(f)
    return pl

#
# MetaData.plist reading functions  
#

META_DATA_KEY_SONG_KEY = "SongKey"
META_DATA_KEY_SONG_GENDER = "SongGenderKey"
def getKey(md):
  """Returns the song key from the given object"""
  return md[META_DATA_KEY_SONG_KEY]

def getGender(md):
  """Returns the key's gender from the given object"""
  return md[META_DATA_KEY_SONG_GENDER]

#
# ProjectData reading functions
#

METRO_FLAG_OFFSET = 0x11C
def getMetronome(pd):
  """Reads the metronome status bit and returns a boolean value"""
  flag, = struct.unpack("B",pd[METRO_FLAG_OFFSET])
  return True if flag & 1 else False


def getArrangement(pd):
  """Extract the arrangment chunk as return list of tuples: (label, duration).
     Requires arr.py to be imported.
  """
  return arr.getArr(pd)


def getDrummer(pd):
  """Extract the drummer info plist, decode using ccl_bplist,
     and dump the drummer identifiers.
     Requires drummer.py to be imported
  """
  drummersPlist = io.BytesIO(drummer.getDrummerChunk(pd))
  return drummer.decodeDrummersPlist(drummersPlist)


LFUATag = b"\x4c\x46\x55\x41\x01\x11"
PMOCTag = b"\x50\x4d\x4f\x43"
def getAudioLoops(pd):
  """Returns a list with file names of audio loops"""
  LFUAAddr = 0
  loops = []
  while True:
    LFUAAddr = pd.find(LFUATag, LFUAAddr + 6)
    if LFUAAddr == -1:
      break
    PMOCAddr = pd.find(PMOCTag, LFUAAddr)
    loops.append(pd[LFUAAddr + 10:PMOCAddr].strip("\x00"))
  return loops


def getInstTracks(pd):
  """Returns a list with info about each instrument track as tuples:
     (track number, base preset name, gain).
     Requires tracklist to be imported
  """
  return tracklist.getTrackList(pd)

def main():
  pprint.pprint(load(sys.argv[1]))

if __name__ == "__main__":
  main()

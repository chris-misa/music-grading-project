"""
  Test garageband files against chater 4 rubric
"""

import sys
sys.path.append("../api")
import bandFile
from errors import TestError, TestCode

def hasCorrectInstruments(bf):
  """
    Returns true if given bandFile object has the correct instruments.
    Identifies tracks by looking for keywords in keywords and label fields
  """
  # There should be six elements in the tracks array: five plus master track
  if len(bf['tracks']) != 6:
    return False
  # First four tracks are taken care of through this list,
  # Last track not being bass is taken care of later
  insts = [(1, ["Vintage Electric Piano"]), \
           (2, ["Drum Kit"]), \
           (3, ["Bass"]), \
           (4, ["Piano","Synths","Electric Piano","Organ","Guitar","Clavinet"])]
  for trackNum, words in insts:
    trackOk = False
    track = bf['tracks'][trackNum]
    if not track:
      return False
    for word in words:
      if track['keywords']:
        for k in track['keywords']:
          if word in k:
            trackOk = True
            break
      if track['label']:
        if word in track['label']:
          trackOk = True
          break
    if not trackOk:
      return False
  # Make sure last track is not bass
  track = bf['tracks'][5]
  if not track:
    return False
  if track['keywords']:
    for k in track['keywords']:
      if "Bass" in k:
        return False
  if track['label']:
    if "Bass" in track['label']:
      return False
  return True

def test(fp):
  """
    Runs chapter 4 tests against the given gb project
  """
  failedCodes = []
  bf = bandFile.load(fp)
  if not hasCorrectInstruments(bf):
    failedCodes.append(TestCode(4,1,description="Wrong tracks"))

  if failedCodes:
    raise TestError(failedCodes)
  else:
    return True

def main():
  """
    Main for testing
  """
  print(test(sys.argv[1]))

if __name__ == "__main__":
  main()

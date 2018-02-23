"""
  Test garageband files against chater 4 rubric
"""

import sys
sys.path.append("../api")
sys.path.append("../appleloops")
import bandFile
import appleLoops
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
      # Check keywords
      if track['keywords']:
        for k in track['keywords']:
          if word in k:
            trackOk = True
            break
      # Check label
      if track['label']:
        if word in track['label']:
          trackOk = True
          break
      # Check region names
      if 'regions' in track.keys():
        for r in track['regions']:
          if word in r['name']:
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

def trackOneIsEmpty(bf):
  """
    Returns true if track one is empty
  """
  if 'regions' in bf['tracks'][1].keys():
    return len(bf['tracks'][1]['regions']) == 0
  return True

def trackThreeFourInst(bf):
  """
    Returns true is track three and four are instument tracks
  """
  if bf['tracks'][3]['type'] != "instrument":
    return False
  if bf['tracks'][4]['type'] != "instrument":
    return False
  return True

def trackFiveHasCorrectLoop(bf):
  """
    Returns true if track five has an instrument loop or an audio loop
    from the correct category
  """
  # Fail if there is not track 5
  if 5 not in bf['tracks'].keys():
    return False
  track = bf['tracks'][5]
  # Fine is it's an instrument track
  if track['type'] == "instrument":
    return True
  elif track['type'] == "audio":
    # Fail if there are no regions
    if 'regions' not in track.keys():
      return False
    # Else check that each region qualifies
    for r in track['regions']:
      metadata = appleLoops.getLoopMetadata(r['name'])
      for md in metadata:
        if "Percussion" not in md['category']:
          return False
    return True
  else:
    # Not instrument or audio track
    return False
  

def test(fp):
  """
    Runs chapter 4 tests against the given gb project
  """
  failedCodes = []
  bf = bandFile.load(fp)
  if not hasCorrectInstruments(bf):
    failedCodes.append(TestCode(4,1,description="Wrong track layout"))

  if not trackOneIsEmpty(bf):
    failedCodes.append(TestCode(4,2,description="Track one is not empty"))

  if not trackThreeFourInst(bf):
    failedCodes.append(TestCode(4,3,description="Track three of four does not have a software instrument loop"))
  
  if not trackFiveHasCorrectLoop(bf):
    failedCodes.append(TestCode(4,4,description="Wrong type of loop in track five"))

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

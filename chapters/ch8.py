"""
  Strategy ideas:
    Compute presence for each track in each section then
    test for tiered entrance form
"""

import sys
sys.path.append("../api")
import bandFile
from errors import TestError, TestCode
from pprint import pprint

TICKS_PER_MEASURE = 4 * 960

# Array of tuples with expected section boundaries
SECTIONS_MEASURES = [(0,4),(4,12),(12,20),(20,28),(28,36),(36,44),(44,52),(52,60),(60,68)]
SECTIONS_TICKS = [(sec[0]*TICKS_PER_MEASURE,sec[1]*TICKS_PER_MEASURE) \
                  for sec in SECTIONS_MEASURES]

def isPresent(notes, section):
  """
    Returns true if the given notes array contains notes in the given section
    boundary.
  """
  if len([note for note in notes if note['time'] > section[0] \
                                  and note['time'] < section[1]]) > 0:
    return True
  else:
    return False

def getSectionalForm(tracks):
  """
    Returns a 2-dimensional array with boolean values for each track X section
    If the tracks and section are correct this will be a 5 by 9 array
  """
  return [[isPresent(track['notes'],section) for section in SECTIONS_TICKS] \
           for key, track in tracks.items() if 'notes' in track.keys()]

def testSectionalForm(form):
  """
    Returns true if the given form fits the prescribed model
    Only checks tracks through the 5th section (Verse 3)
    If violation are encountered, the return value is a message describing
    the violation
  """
  # Test Melody is in right place (not in intro, in verse 1, 2, 3 and chorus 1
  if not (form[0][0] == False and form[0][1] == True and form[0][2] == True \
          and form[0][3] == True and form[0][4] == True):
    return "Melody (track 1) is not correct"
  # Test drums go throughout
  if not (form[1][0] == True and form[1][1] == True and form[1][2] == True \
          and form[1][3] == True and form[1][4] == True):
    return "Drums (track 2) are not correct"
  # Check for layered entrances among other three tracks
  accomp = form[2:]
  accomp.sort()
  # Test longest laying-out track lays out for long enough
  if not (accomp[0][0] == False and accomp[0][1] == False \
          and accomp[0][2] == False and accomp[0][3] == False \
          and accomp[0][4] == True):
    return "Longest laying-out track not correct"
  # Test next longest laying out track comes in right
  if not (accomp[1][0] == False and accomp[1][1] == False \
          and accomp[1][2] == True and accomp[1][3] == True \
          and accomp[1][4] == True):
    return "First entering track not correct"
  # Test accompaniment track from intro is not deleted in subsequent sections
  if not (accomp[2][0] == True and accomp[2][1] == True \
          and accomp[2][2] == True and accomp[2][3] == True \
          and accomp[2][4] == True):
    return "Intro accompaniment track not correct"
  # If we get to here everything passed to return true
  return True

def test(fp):
  """
    Runs chapter 8 tests against the given garageband project
  """
  
  failedCodes = []
  bf = bandFile.load(fp)
  result = testSectionalForm(getSectionalForm(bf['tracks']))
  if result != True:
    failedCodes.append(TestCode(8,1,description = result))

  if failedCodes:
    raise TestError(failedCodes)
  else:
    return True


def main():
  """
    Main for testing the tests
  """
  print(test(sys.argv[1]))

if __name__ == "__main__":
  main()

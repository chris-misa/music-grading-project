import sys
sys.path.append("../api")
import bandFile
from errors import TestError, TestCode

"""
  Test garageband files against chapter 2 rubric
"""

def hasAnInstrument(bf):
  """
    Looks through the tracks field to make sure one of them is an insturment.
    Acheiving this basically by just makeing sure we've found keywords
    for one of the tracks.  Since keywords can only be found for instrument tracks,
    this should work.
  """
  for k, v in bf['tracks'].items():
    if v['keywords'] != None:
      return True
  return False

def hasGoodKey(bf):
  """
    Returns true if the key is in the list of accepted keys
  """
  KEYS = [('C', 'major'),('G','major'),('A','minor')]
  return (bf['key'], bf['gender']) in KEYS

def test(fp):
  """
    Runs chapter 2 tests against the given garageband project
  """

  failedCodes = []
  bf = bandFile.load(fp)
  if not hasAnInstrument(bf):
    failedCodes.append(TestCode(2,1,description = "no software instrument found"))

  if bf['metronome']:
    failedCodes.append(TestCode(2,2, description = "metronome is on"))

  if not hasGoodKey(bf):
    failedCodes.append(TestCode(2,3, description = " key is not accepted: " + bf['key'] + " " + bf['gender']))

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

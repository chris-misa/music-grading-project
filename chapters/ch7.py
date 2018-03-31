import sys
sys.path.append("../api")
import bandFile
from errors import TestError, TestCode

# Array of where transposition points are allowed to happend (in measures)
TARGET_TRANS_POINTS = [20,28,36,44,52]

TICKS_PER_MEASURE = 4 * 960

def testTranspositionTrack(trans):
  """
    Walk through transposition track and check requirements
    Returns 0 if all passed,
            1 if 7.1 failed (bad placement)
            2 if 7.2 failed (doesn't change to same key)
  """
  prevValue = None
  values = {}
  for p in trans:
    values[p['value']] = True
    if prevValue == None:
      prevValue = p['value'];
    elif p['value'] != prevValue:
      if p['time'] / TICKS_PER_MEASURE not in TARGET_TRANS_POINTS:
        return 1
      else:
        prevValue = p['value']
  if len(values) > 2:
    return 2
  else:
    return 0

def test(fp):
  """
    Runs chapter 7 tests against the given garageband project
  """
  
  failedCodes = []
  bf = bandFile.load(fp)

  result = testTranspositionTrack(bf['transposition'])
  if result == 1:
    failedCodes.append(TestCode(7,1,description = "Bad placement of transposition points"))
  elif result == 2:
    failedCodes.append(TestCode(7,2,description = "More then two different keys transposed to"))

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

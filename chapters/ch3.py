import sys
sys.path.append("../api")
import bandFile
from errors import TestError, TestCode

ticksPerMeasure = 3840


"""
    Test garageband against chapter 3 rubric
"""

def hasVerseChorusInArrangment(bf):
    global verseTicks
    global chorusTicks
    try:
        if bf['arrangement'][0][0] == 'Verse 1' and bf['arrangement'][0][1]/ticksPerMeasure == 8 and bf['arrangement'][1][0] == "Chorus 1" and bf['arrangement'][1][1]/ticksPerMeasure == 8:
            verseTicks = bf['arrangement'][0][1]
            chorusTicks = bf['arrangement'][1][1]
            return True
    except:
        return False

def hasDrummerTrack(bf):
    for _, v in bf['tracks'].items():
        try:
            if 'Drum Kit' in v['keywords']:
                try:
                    if 'Verse 1' in v['regions'][0]['name'] and v['regions'][0]['length'] == verseTicks and 'Chorus 1' in v['regions'][1]['name'] and v['regions'][1]['length'] == chorusTicks:
                        return True
                except:
                    return False
        except:
            return False
    return False

def test(fp):
    """
        Runs chapter 3 tests against the given garageband project
    """
    failedCodes = []
    bf = bandFile.load(fp)
    if not hasVerseChorusInArrangment(bf):
        failedCodes.append(TestCode(3,1,description = "Verse/Chorus with 8 measures is not in Arrangment"))

    if not hasDrummerTrack(bf):
        failedCodes.append(TestCode(3,2, description = "No Drummer track containing a Verse/Chorus exists with the correct number of measures"))

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

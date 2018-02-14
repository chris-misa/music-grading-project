"""
  Get general information about instrument patch categories by finding
  them in the GarageBand instrument patch directories.

  Notes:
    sometimes apple loops will load presets not found in main GarageBand
    preset directories. In this case we should be able to look for metadata
    about the loop instead.

  Improvements:
    reload the pickle if it doesn't exists
"""
import sys
import os
import re
import pprint
import pickle

GARAGEBAND_APP_PATH = "/Applications/GarageBand.app"
INST_PATCHES_PATH = "Contents/Resources/Patches/Instrument"
PICKLE_TARGET = "instruments"

def getInstrument(inst):
  """
    Looks up the given instrument in the pickled instruments file
    and returns its category key words
  """
  instruments = loadInstruments()
  if inst not in instruments.keys():
    return None
  else:
    return instruments[inst]
  

def getInstrumentPatches():
  """
    Returns a dictionary of GarageBand's instrument plug ins with
    category keywords adapted from their position in the directory structure.
  """
  patchesPath = os.path.join(GARAGEBAND_APP_PATH, INST_PATCHES_PATH)
  patches = {}
  for p, d, f in os.walk(patchesPath):
    r = re.match(r"^.*/Instrument/(.*)\.patch$", p)
    if r:
      path, name = os.path.split(r.group(1))
      patches[name] = []
      while path:
        path, word = os.path.split(path)
        patches[name].append(word)
  return patches

def dumpInstruments(fp = PICKLE_TARGET):
  """
    Pickles a dictionary of GarageBand instruments at the given filepath
  """
  with open(fp,'w') as f:
    pickle.dump(getInstrumentPatches(), f)

def loadInstruments(fp = PICKLE_TARGET):
  """
    Unpickles and returns stored GarageBand instruments dictionary
  """
  with open(fp,"r") as f:
    return pickle.load(f)

def main():
  """
    Dumps the current GarageBand instruments and prints the dumped dictionary
    to stdout
  """
  dumpInstruments()
  pprint.pprint(loadInstruments())

if __name__ == "__main__":
  main()

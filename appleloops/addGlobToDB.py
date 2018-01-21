"""
  Reads all files referenced by the given glob and tries to add them to the database
  Paths which include spaces must be in quotes.
"""

import sys
import glob
import os
import appleLoops
import cafLib 

def main():
  if len(sys.argv) != 2:
    print("Usage: python addBlobToDB.py path/to/some/files/*.caf")
    return
  db = appleLoops.Database()
  count = 0
  for path in glob.glob(sys.argv[1]):
    try:
      data = cafLib.loadMetaData(path)
    except:
      print("Failed to load meta data from: {}".format(path))
      continue
    data['filename'] = os.path.basename(path)
    if db.addFilename(data) == 0:
      count += 1
    else:
      print("Failed to add meta data loaded from: {}".format(path))
  print("Added {} loops to database".format(count))
    

if __name__ == "__main__":
  main()

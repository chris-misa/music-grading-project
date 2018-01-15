#
# Pulls out some information about the drummer tracks, if any
#
# If standalone, first argument is path to grageband project

import sys
import io
import mmap
import ccl_bplist

OgnSTag = "\x4f\x67\x6e\x53\x01"
qeSMTag = "\x71\x65\x53\x4d\x02"

# Convert objects of form UID: number to ints
def UIDtoInt( uid ):
  return int(str(uid)[4:])

# Translates keys and objects of NSKeyedArchiver node into a dict
# node is a dict with NS.keys and NS.objects
# objList is the master '$objects' list
def nodeToDict( node, objList ):
  d = {}
  for i, k in enumerate(node['NS.keys']):
    d[objList[UIDtoInt(k)]] = objList[UIDtoInt(node['NS.objects'][i])]
  return d

# Walks the drummer info plist given in data
# returns a list of the selectedCharacterIdentifier for each drummer
def decodeDrummersPlist( data ):
  pl = ccl_bplist.load( data )
  rootID = UIDtoInt(pl['$top']['root'])
  root = nodeToDict(pl['$objects'][rootID], pl['$objects'])
  baseModel = nodeToDict(root['genInstDrummerBaseModel.state'], pl['$objects'])
  drummers = nodeToDict(baseModel['drummerModelTrackStates'], pl['$objects'])
  result = []
  for k, v in drummers.items():
    drummerInfo = nodeToDict(v, pl['$objects'])
    result.append(drummerInfo['selectedCharacterIdentifier'])
  return result

# Returns the drummers info plist as a byte string
def getDrummerChunk( pd ):
  OgnSAddr = pd.find(OgnSTag)
  plistAddr = pd.find(b"bplist00", OgnSAddr)
  qeSMAddr = pd.find(qeSMTag, plistAddr)
  return pd[plistAddr:qeSMAddr].rstrip("\x00")

def main():
  projectDataPath = sys.argv[1] + "/Alternatives/000/ProjectData"
  f = open(projectDataPath, "r+b")
  mm = mmap.mmap(f.fileno(), 0)
  drummersPlist = io.BytesIO(getDrummerChunk(mm))
  print("\n".join(decodeDrummersPlist(drummersPlist)))

if __name__ == "__main__":
  main()

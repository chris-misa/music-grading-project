import mmap
import sys

OCuA_TAG = "\x4f\x43\x75\x41\x01\x00\x0e\x00\x00\x00\x24\x00\x00\x00"

def main():
  with open(sys.argv[1],'r+b') as f:
    mm = mmap.mmap(f.fileno(),0)
    inst1Addr = mm.find(b'Inst 1')
    end = mm.rfind(OCuA_TAG, 0, inst1Addr)
    for i in range(0,4):
      start = mm.find(OCuA_TAG, end)
      end = mm.find(OCuA_TAG, start + 11)
      with open("out" + str(i), 'wb') as outfile:
        outfile.write(mm[start:end])

if __name__ == "__main__":
  main()

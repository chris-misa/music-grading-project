# Chapters Directory

This directory should have a module for each chapter
(ch1.py, ch2.py, . . .) as well as utility modules with
analysis functions needed in multiple chapters.

## Chapter script interface

Each chapter module must follow the naming convention established above and
implement a function with the following signature:

def test(filepath):
  """
    Open the garageband file at the given file path.
    Run this chapter's tests on this file.
    Return a string for the grader:
      "Pass" or "Fail: <specific point of failure>"
      

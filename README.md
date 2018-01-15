# Music Grading Project

This project reads and grades GarageBand files.

## Proposed Directory Structure

- root
  user interface scripts
  - tests
    GarageBand and MIDI file for testing (Toby)
  - api
    scripts for extracting information from raw .band files
  - midi
    scripts for making judgements on midi or note events

## Proposed Architecture

```text
user interface layer  <-> api layer
                  ^        ^
                  |       /
                  |      /
                  |     /
                  |    /
                  V   V
               midi layer
```

### user interface layer
Handles user input (files, rubric)
Uses api and midi layers to grade each file
Outputs results
*Adam*?

### midi layer
Receives midi files or note events from api layer (depending on what ends up working out)
Implements test functions for all midi-related criteria, possibly in consultation with
api layer for track or arrangement details.
*Andrew*

### api layer
Receives GarageBand files from user interface layer.
Returns dictionay of properties needed to implement non-midi-related tests.
Working branch: bandAPI
*Chris*



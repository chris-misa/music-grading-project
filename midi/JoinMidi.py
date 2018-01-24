import midi
import sys

if len(sys.argv) < 2:
    sys.exit("Not enough parameters")

pattern = midi.read_midifile(sys.argv[1])



def getFirstNote(track):
    for event in track:
        if isinstance(event, midi.NoteEvent):
            return event

def getAbsTime(track):
    abs_time = 0
    for event in track:
        if isinstance(event, midi.NoteEvent):
            abs_time += event.tick

    return abs_time


## This section is only needed if there are overlapping notes
# #TPM is ticks per measure
# def TrimNotes(track, TPM):
#     AbsTime = getAbsTime(track)
#     correctAbsTime = AbsTime - AbsTime % (2*TPM)
#     cur_abs_time = 0
#     newTrack = midi.Track()

#     for event in track:

#         if isinstance(event, midi.NoteEvent):
#             cur_abs_time += event.tick
#             if cur_abs_time <= correctAbsTime:
#                 newTrack.append(event)
            
            

#         else: 
#             newTrack.append(event)
                
#     return newTrack

# #preprocess to remove extra notes
# def ProcessPattern(pattern):
#     TPM = pattern.resolution * pattern[0][1].get_numerator()
#     processedTracks = midi.Pattern(resolution = 480)
#     for track in pattern:
#         ## find whether this track is a instrument track and find the instrument name
#         inst_name = None 
#         for event in track:
#             if isinstance(event, midi.InstrumentNameEvent):
#                 inst_name = event.text
#                 break
#         if inst_name:
#             processedTrack = TrimNotes(track, TPM)
#             processedTracks.append(processedTrack)
#         else:
#             processedTracks.append(track)
        

#     return processedTracks



def joinRegions(pattern):
    joined_pattern = midi.Pattern(resolution = 480)

    cur_abs_time = 0
    cur_inst_name = ""
    cur_track = None

    
    for track in pattern:

        ## find whether this track is a instrument track and find the instrument name
        inst_name = None 
        for event in track:
            if isinstance(event, midi.InstrumentNameEvent):
                inst_name = event.text
                break
        # if it's an instrument track, tally absolute time
        if inst_name:
            ## if new instrument, Add the previous cur_track to pattern and start the time over. 
            if inst_name != cur_inst_name:
                if cur_track:
                    cur_track.append(midi.EndOfTrackEvent())
                    joined_pattern.append(cur_track)
                
                cur_inst_name = inst_name
                cur_abs_time = getAbsTime(track)
                cur_track = track[0:-1]
                

            ## otherwise, subtract absolute time from the first tick and add note events to the ongoing track
            else:
                first_note = getFirstNote(track)
                first_note.tick -= cur_abs_time

                for event in track:
                    if isinstance(event, midi.NoteEvent):
                        cur_track.append(event)

                cur_abs_time += getAbsTime(track)

        ## if it's not an instrument track, add the current track in then add the track to the pattern
        else:
            if cur_track:
                    cur_track.append(midi.EndOfTrackEvent())
                    joined_pattern.append(cur_track)

            cur_track = None
            joined_pattern.append(track)

    # if there's still a track being added to, add it
    if cur_track:
        cur_track.append(midi.EndOfTrackEvent())
        joined_pattern.append(cur_track)


    return joined_pattern
                    
        


joinedPattern =  joinRegions(pattern)

midi.write_midifile("joined.mid", joinedPattern)

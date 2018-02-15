import sys
sys.path.append("../api")

import midiDump as md

def quantize_rhythm(seq, quantum = 120):

	for i in seq.keys():

		if "notes" in seq[i]:

			track = seq[i]["notes"]

			for note in track:

				note["duration"] = note["duration"] / quantum * quantum
				note["time"] = note["time"] / quantum * quantum

	return seq

def check_white_keys(seq):

	all_white = True

	for i in seq.keys():

		if "notes" in seq[i]:

			track = seq[i]["notes"]

			for note in track:
        
        p = note["pitch"] % 12

				if p == 1 or p == 3 or p == 6 or p == 8 or p == 10:
					all_white = False
					break

	return all_white


def in_range(seq):

	all_in_range = True

	melody = track = seq[1]["notes"]

	for note in melody:

		if note["pitch"] > 77 or note["pitch"] < 48:
			all_in_range = False
			break

	return all_in_range

def check_one_note(seq):

	one_note = True

	melody = seq[1]["notes"]

	for j in range(len(melody) - 1):

		current_end = melody[j]["time"] + melody[j]["duration"]
		next_start = melody[j+1]["time"]

		if next_start < current_end:

			one_note = False
			break
	return one_note



def main():
	# 1
	tracks = md.makeTracks("5.6 Right.band")
	quantized_tracks = quantize_rhythm(tracks)
	md.writeToMIDIFile(quantized_tracks, "quantized.mid")
	# 2
	print check_white_keys(tracks)
	# 3
	print in_range(tracks)
	# 4
	print check_one_note(tracks)

if __name__ == "__main__":
  main()


import sys
sys.path.append("../api")

import midiDump as md
import utilities as ut
from errors import TestError, TestCode
from copy import deepcopy
import bandFile as bf

def check_2_4_bar_regions(seq, tpqn = 480):

	melody = seq[1]["regions"]

	for region in melody:
		if "length" in region:
			length = region["length"]
			if not (length == (4*4*tpqn) or length == (2*4*tpqn)):

				return False
	return True

def check_verse_chorus(seq, verse_measures, tpqn = 480):

	melody = seq[1]["notes"]

	index = 0
	for note in melody:
		time = note["time"]
		if time >= verse_measures*4*tpqn:
			index = melody.index(note)
			break

	verse = melody[0:index]
	chorus = melody[index:]

	def are_equal(seg1, seg2):
		if len(seg1) == len(seg2):
			for i in range(len(seg1)):
				if seg1[i]["pitch"] != seg2[i]["pitch"]:
					return False
		return True
	return are_equal(verse, chorus)


def quantize_rhythm(seq, quantum = 120):

	seq_copy = deepcopy(seq)

	for i in seq_copy.keys():

		if "notes" in seq_copy[i]:

			track = seq_copy[i]["notes"]

			for note in track:

				note["duration"] = note["duration"] / quantum * quantum
				note["time"] = note["time"] / quantum * quantum

	return seq_copy

def is_quantized(seq, quantum = 120):

	quantized = True

	for i in seq.keys():

		track_is_quantized = True

		if "notes" in seq[i] and track_is_quantized:

			track = seq[i]["notes"]

			for note in track:

				if note["duration"] != note["duration"] / quantum * quantum or note["time"] != note["time"] / quantum * quantum:
					quantized = False
					track_is_quantized = False
					break			
					
	return quantized

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

	melody = seq[1]["notes"]

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


def check_for_motifs(seq):

	repetition = False

	melody_regions = seq[1]["regions"]

	length = len(melody_regions)

	for i in range(length):
		for j in range(i+1, length):

			if ut.are_equal(melody_regions[i], melody_regions[j]):

				repetition = True
				return repetition

def test(fp):

	tracks = md.makeTracks(fp)

	failedCodes = []

	if not check_2_4_bar_regions(tracks, tpqn = 960):
		failedCodes.append(TestCode(5,1,description = "regions are not 2 or 4 bars long"))

	if not check_for_motifs(tracks):
		failedCodes.append(TestCode(5,2,description = "no repetition or motifs"))

	### What is verse chorus structure at this point?
	verse_measures = bf.load(fp)['arrangement'][0][1]
	if check_verse_chorus(tracks, 8, tpqn = 960):
		failedCodes.append(TestCode(5,4,description = "verse and melody are the same"))

	if not is_quantized(tracks):
		failedCodes.append(TestCode(5,4,description = "notes are not quantized"))

	if not check_one_note(tracks):
		failedCodes.append(TestCode(5,5,description = "there are simultaneuous notes"))

	if not check_white_keys(tracks):
		failedCodes.append(TestCode(5,6,description = "notes are not all white"))

	if not in_range(tracks):
		failedCodes.append(TestCode(5,7,description = "notes are not all in range"))


	if failedCodes:
		raise TestError(failedCodes)
 	else:
 		return True


def main():
	"""
    Main for testing
	"""

	tracks = md.makeTracks("../tests/5.6 Right.band")
	quantized_tracks = quantize_rhythm(tracks)
	md.writeToMIDIFile(quantized_tracks, "quantized.mid")
	
	print check_white_keys(tracks)
	
	print in_range(tracks)
	
	print check_one_note(tracks)
	
	print check_for_motifs(tracks)

	print(test(sys.argv[1]))

	

if __name__ == "__main__":
  main()


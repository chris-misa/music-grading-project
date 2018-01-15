import midi
import sys


def consonantnotes(pattern):
	for track in pattern:
		for event in track:
			if isinstance(event, midi.NoteEvent):
				pitch = event.get_pitch() % 12
				if pitch == 1 or pitch == 3 or pitch == 6 or pitch == 8 or pitch == 10:
					print "failed test"
					break
		else:
			continue

		break



if len(sys.argv) < 2:
	sys.exit("Not enough parameters")

pattern = midi.read_midifile(sys.argv[1])

consonantnotes(pattern)
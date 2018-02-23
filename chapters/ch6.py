import sys
sys.path.append("../api")

import midiDump as md
import utilities as ut
from errors import TestError, TestCode
import bandFile as bf

# requirement 6.1
def check_form(info, tpqn = 480):

	markers = info["arrangement"]

	tpm = 4*tpqn

	if len(markers) != 9:
		return False
	else:
		if markers[0][0] != "Intro" or markers[0][1]/tpm != 4:
			return False
		elif markers[1][0] != "Verse 1" or markers[1][1]/tpm != 8:
			return False
		elif markers[2][0] != "Verse 2" or markers[2][1]/tpm != 8:
			return False
		elif markers[3][0] != "Chorus 1" or markers[3][1]/tpm != 8:
			return False
		elif markers[4][0] != "Verse 3" or markers[4][1]/tpm != 8:
			return False
		elif markers[5][0] != "Chorus 2" or markers[5][1]/tpm != 8:
			return False
		elif markers[6][0] != "Bridge" or markers[6][1]/tpm != 8:
			return False
		elif markers[7][0] != "Chorus 3" or markers[7][1]/tpm != 8:
			return False
		elif markers[8][0] != "Outro" or markers[8][1]/tpm != 8:
			return False

	return True

# requirement 6.2
def same_content(info, tpqn = 480):

	tracks = info["tracks"]

	for i in tracks.keys():
		same = True

		if 'notes' in tracks[i]:
			track = tracks[i]['notes']

			verse1 = ut.grab_section(track, 5, 8, tpqn)
			verse2 = ut.grab_section(track, 13, 8, tpqn)
			chorus1 = ut.grab_section(track, 21, 8, tpqn)
			verse3 = ut.grab_section(track, 29, 8, tpqn)
			chorus2 = ut.grab_section(track, 37, 8, tpqn)
			chorus3 = ut.grab_section(track, 53, 8, tpqn)

			if (not (ut.are_equal(verse1, verse2) and ut.are_equal(verse2, verse3)) and ut.are_equal(chorus1, chorus2) and ut.are_equal(chorus2, chorus3)):
				
				return False

	return True

def test(fp):
	info = bf.load(fp)

	failedCodes = []

	if not check_form(info,960):
		failedCodes.append(TestCode(6,1,description = "form of song is not same as rubric"))

	if not same_content(info, 960):
		failedCodes.append(TestCode(6,2,description = "verses and choruses are not all the same"))

	if failedCodes:
		raise TestError(failedCodes)
 	else:
 		return True

# tests
def main():
	print(test(sys.argv[1]))


if __name__ == "__main__":
	main()







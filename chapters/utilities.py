import sys
sys.path.append("../api")

import midiDump as md

'''
Functions to find which regions are the same
'''

def editDistDP(list1, list2, m, n):
    # Create a table to store results of subproblems
    dp = [[0 for x in range(n+1)] for x in range(m+1)]
 
    # Fill d[][] in bottom up manner
    for i in range(m+1):
        for j in range(n+1):
 
            # If first string is empty, only option is to
            # isnert all characters of second string
            if i == 0:
                dp[i][j] = j    # Min. operations = j
 
            # If second string is empty, only option is to
            # remove all characters of second string
            elif j == 0:
                dp[i][j] = i    # Min. operations = i
 
            # If last characters are same, ignore last char
            # and recur for remaining string
            elif list1[i-1] == list2[j-1]:
                dp[i][j] = dp[i-1][j-1]
 
            # If last character are different, consider all
            # possibilities and find minimum
            else:
                dp[i][j] = 1 + min(dp[i][j-1],        # Insert
                                   dp[i-1][j],        # Remove
                                   dp[i-1][j-1])    # Replace
 
    return dp[m][n]

def get_note_seq(region):

	seq = []

	for note in region["notes"]:

		seq.append(note["pitch"])

	return seq

def get_duration_seq(region):

    quantized = quantize_rhythm(region)

    seq = []

    for note in quantized["notes"]:
        seq.append(note["duration"])

    return seq


def quantize_rhythm(region, quantum = 120):

	seq = region["notes"]

	for note in seq:

		note["duration"] = note["duration"] / quantum
		note["time"] = note["time"] / quantum

	return region


def are_equal(region1, region2, min_distance_notes = 2, min_distance_dur = 5):

    note_seq1 = get_note_seq(region1)
    note_seq2 = get_note_seq(region2)

    if editDistDP(note_seq1, note_seq2, len(note_seq1), len(note_seq2)) < min_distance_notes:

        dur_seq1 = get_duration_seq(region1)
        dur_seq2 = get_duration_seq(region2)

        if editDistDP(dur_seq1, dur_seq2, len(dur_seq1), len(dur_seq2)) < min_distance_dur:

            return True

    return False




'''
Tests
'''

def main():
    tracks = md.makeTracks("../tests/5.6 Right.band")
    region1 = tracks[1]["regions"][0]
    region2 = tracks[1]["regions"][1]

    print are_equal(region1,region2)


if __name__ == "__main__":

    main()






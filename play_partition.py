from pydub import AudioSegment
from pydub.playback import play
from musicBoxMaker import *

partition = parsePartitionFile("listNotes.txt")#put your partition here

notes = AudioSegment.from_mp3("recording_notes.mp3")#put your recording here

#put the start time (in ms) of each note here
startTimes = [4984, 5538, 6071, 6647, 7249, 7736, 8288, 8910, 9485, 9984, 10705, 11322, 11953, 12615, 13210, 13825, 14553, 15237]


noteLength = 200 #length of each note (in ms)
song = AudioSegment.empty()
nbNotes = partition.shape[0]
for i in range(partition.shape[1]):#loop over the partition
    note = AudioSegment.silent(duration=noteLength)
    for j in range(nbNotes):#loop over the notes
        if partition[nbNotes-j-1,i]:
            note = note.overlay(notes[startTimes[j]:startTimes[j]+300])
    song += note
play(song) #play the partition
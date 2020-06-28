import mido
import sys
import time
import random
from PyQt5.QtCore import QObject, QRunnable, Qt, pyqtSignal, pyqtSlot
from synth import MidiSynth

NOT_IN_SCALE = -10000

# Just for testing/reading/displaying purposes
NOTES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']

def generate_complete_notes():
    white_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    complete_notes = []
    for note in white_notes:
        complete_notes.extend((note, note + '#', note + 'b'))
    return complete_notes

COMPLETE_NOTES = generate_complete_notes()

NOTE_JUMPS = [2, 2, 1, 2, 2, 2, 1]
REV_NOTE_JUMPS = NOTE_JUMPS[::-1]

# Relative to the fourth octave of the note (also zero indexed, contrary to music theory).
def note_number_in_scale_from_semitones(semis):
    if (semis == 0):
        return 0
    if (semis >= 0):
        i = 0
        count = 0
        while(True):
            for jump in NOTE_JUMPS:
                count += jump
                if (count == semis):
                    return i+1
                if (count > semis):
                    return NOT_IN_SCALE
                i += 1
    else:
        i = 0
        count = 0
        while(True):
            for jump in REV_NOTE_JUMPS:
                count -= jump
                if (count == semis):
                    return i-1
                if (count < semis):
                    return NOT_IN_SCALE
                i -= 1


def convert_msg_to_note_num(msg):
    msg = str(msg)
    index_of_note = msg.index("note=")
    note_num = msg[index_of_note + 5: index_of_note+7]

    # Check for triple digits.
    if (note_num >= "10"):
        if (msg[index_of_note + 7] != ' '):
            note_num += msg[index_of_note + 7]

    return int(note_num)

def convert_note_num_to_note(note_num):
    return NOTES[note_num % 12] + str(note_num // 12 - 1)

def line_number_from_note_treble(note, key='C'):
    if (key.find('C') != -1):
        return note_number_in_scale_from_semitones(note - 60) - 2
    if (key.find('D') != -1):
        return note_number_in_scale_from_semitones(note - 60) - 1
    if (key.find('E') != -1):
        return note_number_in_scale_from_semitones(note - 60)
    if (key.find('F') != -1):
        return note_number_in_scale_from_semitones(note - 60) + 1
    if (key.find('G') != -1):
        return note_number_in_scale_from_semitones(note - 60) + 2
    if (key.find('A') != -1):
        return note_number_in_scale_from_semitones(note - 60) + 3
    if (key.find('B') != -1):
        return note_number_in_scale_from_semitones(note - 60) + 4



class NoteSignal(QObject):
    note_recieved = pyqtSignal(object)
    note_generated = pyqtSignal(object)

class GenerateNoteWorker(QRunnable):
    curr_note = None
    prev_note = None
    
    def __init__(self, key, difficulty):
        super(GenerateNoteWorker, self).__init__()
        self.signal = NoteSignal()
        self.key = key
        self.difficulty = difficulty
    
    def resetNote(self):
        self.curr_note = None

    def setKey(self, key):
        self.key = key
    
    def setDifficulty(self, difficulty):
        self.difficulty = difficulty

    def generateNote(self):
        min_note = None
        max_note = None
        if (self.key.find('C') != -1):
            if (self.difficulty == "easy"):
                min_note = 64
                max_note = 77
            if (self.difficulty == "medium"):
                min_note = 55
                max_note = 86

        generated_note = None
        while(generated_note == None or generated_note == self.prev_note or note_number_in_scale_from_semitones(generated_note) == NOT_IN_SCALE):
            generated_note = random.randrange(min_note, max_note)
        self.prev_note = generated_note
        return generated_note
            

    @pyqtSlot()
    def run(self): 
        while(True):
            while(self.curr_note == None):
                time.sleep(.5)
                self.curr_note = self.generateNote()
                self.signal.note_generated.emit(
                    line_number_from_note_treble(self.curr_note, self.key))
            time.sleep(.1)

class MidiWorker(QRunnable):

    def __init__(self):
        super(MidiWorker, self).__init__()
        self.inport = mido.open_input('MPK Mini Mk II')
        self.signal = NoteSignal()
        self.key = 'C'
        self.firstTime = True
        self.synths = [MidiSynth(), MidiSynth(), MidiSynth(), MidiSynth(), MidiSynth(), MidiSynth(), MidiSynth(), MidiSynth()]
        

    def update_scale(self, key):
        self.key = key
    
    def playNoteOnASynth(self, note):
        for synth in self.synths:
            if (synth.curr_note == None):
                synth.playNote(note)
                return
        self.synths[0].playNote(note)
    
    def stopNoteOnASynth(self, note):
        for synth in self.synths:
            if (synth.curr_note == note):
                synth.stopPlay()


    @pyqtSlot()
    def run(self):
        while(True):
            for msg in self.inport.iter_pending():
                try: 
                    # This throws exception if not found.
                    _ = str(msg).index("note_on")
                    # This throws exception if a non standard midi note is played.
                    self.signal.note_recieved.emit(
                        line_number_from_note_treble(convert_msg_to_note_num(msg), self.key))
                    self.playNoteOnASynth(convert_msg_to_note_num(msg))
                except:
                    pass
                    
                try: 
                    _ = str(msg).index("note_off")
                    self.stopNoteOnASynth(convert_msg_to_note_num(msg))
                except:
                    pass

            time.sleep(.05)



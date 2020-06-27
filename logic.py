import mido
import sys
import time
from PyQt5.QtWidgets import  QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QStackedLayout
from PyQt5.QtGui import QPalette, QColor, QIcon, QPixmap
from PyQt5.QtCore import QObject, QThreadPool, QRunnable, Qt, pyqtSignal, pyqtSlot

NOT_IN_SCALE = -10000

NOTES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']

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

def line_number_from_note(note, key='C'):
    if (key == 'C'):
        return note_number_in_scale_from_semitones(note - 60) - 2
    if (key == 'D'):
        return note_number_in_scale_from_semitones(note - 60) - 1
    if (key == 'E'):
        return note_number_in_scale_from_semitones(note - 60)
    if (key == 'F'):
        return note_number_in_scale_from_semitones(note - 60) + 1
    if (key == 'G'):
        return note_number_in_scale_from_semitones(note - 60) + 2
    if (key == 'A'):
        return note_number_in_scale_from_semitones(note - 60) + 3
    if (key == 'B'):
        return note_number_in_scale_from_semitones(note - 60) + 4

class NoteSignal(QObject):
    note_recieved = pyqtSignal(object)

class MidiWorker(QRunnable):

    def __init__(self):
        super(MidiWorker, self).__init__()
        self.inport = mido.open_input('MPK Mini Mk II')
        self.signal = NoteSignal()
        self.key = 'C'

    def update_scale(self, key):
        self.key = key
            

    @pyqtSlot()
    def run(self):
        while(True):
            for msg in self.inport.iter_pending():
                try: 
                    # This throws exception if not found.
                    _ = str(msg).index("note_on")
                    # This throws exception if a non standard midi note is played.
                    self.signal.note_recieved.emit(
                        line_number_from_note(convert_msg_to_note_num(msg), self.key))
                except:
                    pass
            time.sleep(.1)



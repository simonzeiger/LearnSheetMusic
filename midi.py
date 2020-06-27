import mido
import sys
import time
from PyQt5.QtWidgets import  QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QStackedLayout
from PyQt5.QtGui import QPalette, QColor, QIcon, QPixmap
from PyQt5.QtCore import QObject, QThreadPool, QRunnable, Qt, pyqtSignal, pyqtSlot

NOTES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']


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

class NoteSignal(QObject):
    note_recieved = pyqtSignal(object)

class MidiWorker(QRunnable):

    def __init__(self):
        super(MidiWorker, self).__init__()
        self.inport = mido.open_input('MPK Mini Mk II')
        self.signal = NoteSignal()


    @pyqtSlot()
    def run(self):
        while(True):
            for msg in self.inport.iter_pending():
                try: 
                    # This throws exception if not found.
                    _ = str(msg).index("note_on")
                    # This throws exception if a non standard midi note is played.
                    self.signal.note_recieved.emit((convert_msg_to_note_num(msg)))
                except:
                    pass
            time.sleep(.1)



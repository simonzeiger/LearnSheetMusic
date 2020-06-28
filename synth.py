import sounddevice as sd
import numpy as np
import time
from PyQt5.QtCore import QTimer, QRunnable, pyqtSlot

class MidiSynth(QRunnable):
    
    def __init__(self, sample_rate = 44100): 
        super(MidiSynth, self).__init__()
        
        # sampling rate, Hz, must be integer
        self.fs = sample_rate
        self.freq = 0
        self.max_volume = .25
        self.volume = .25
        self.play_stopped = True
        self.start_idx = 0
        self.curr_note = None
        self.fade_count = 0
        self.max_volume_reached = None
    
    @pyqtSlot()
    def run(self): 
        while(True):
            with sd.OutputStream(channels=1, callback=self.callback, samplerate=self.fs):
                while(not self.play_stopped):
                    time.sleep(.05)

        
    def callback(self, outdata, frames, time, status):
        # if (self.play_stopped):
        #     return
        
        if (self.fade_out):
            if (self.fade_count == 50):
                if (self.volume < self.max_volume):
                    self.max_volume_reached = self.volume
            if (self.max_volume_reached != None):
                self.volume = self.max_volume_reached * (self.fade_count) / 50
            else:
                self.volume = self.max_volume * (self.fade_count) / 50
            self.fade_count -= 2

            if (self.volume < .001):
                self.curr_note = None
                self.volume = 0
                self.max_volume_reached = None
                self.fade_out = False
                self.play_stopped = True
                return
        
        if (self.fade_in):
            self.volume = self.max_volume * (self.fade_count) / 50
            self.fade_count += 2
            if (self.volume >= self.max_volume):
                self.fade_in = False
                self.volume = self.max_volume

        # Prevent death
        if (self.volume > 1):
            self.volume = 0
            self.stopPlay()
            return

        print(self.volume)
        t = (self.start_idx + np.arange(frames)) / self.fs
        t = t.reshape(-1, 1)

        samples = np.sin(2 * np.pi * self.freq * t)
        if (self.freq < 1000):
            samples += (.0675)*np.sin(2 * np.pi * self.freq * t * 4)
        if (self.freq < 2000):
            samples += (.125)*np.sin(2 * np.pi * self.freq * t * 3)
        if (self.freq < 3000):
            samples += (.25)*np.sin(2 * np.pi * self.freq * t * 2)
        
        outdata[:] = self.volume * samples
        self.start_idx += frames

    
    def playNote(self, note, volume=.25):
        self.fade_count = 0
        self.fade_out = False
        self.fade_in = True
        self.max_volume_reached = None
        self.max_volume = volume
        self.curr_note = note
        self.play_stopped = False
        self.freq = (440.0/32) * (2**((note - 9) / 12))
       

    def stopPlay(self):
        self.fade_in = False
        self.fade_count = 50
        self.fade_out = True
           
      






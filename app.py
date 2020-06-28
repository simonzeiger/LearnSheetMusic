import sys
from PyQt5.QtWidgets import  QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QStackedLayout
from PyQt5.QtGui import QPalette, QColor, QIcon, QPixmap, QColor
from PyQt5.QtCore import QObject, QThreadPool, QRunnable, Qt, pyqtSignal, pyqtSlot, QTimer
from logic import MidiWorker, GenerateNoteWorker

WIDTH = 720
HEIGHT = 360

def dark_theme(qApp):
    qApp.setStyle("Fusion")

    dark_palette = QPalette()

    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    qApp.setPalette(dark_palette)

    qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")


class QuarterNote(QLabel):
    is_curr_pix_normal = True

    def __init__(self, parent):
        self.ledger_lines = self.initLedgerLines(parent)  
        self.hideLedgerLines()
        
        super(QuarterNote, self).__init__(parent)
        self.pix = QPixmap('./quarter_note.png').scaledToHeight(214)
        self.red_pix = QPixmap('./quarter_note_red.png').scaledToHeight(214)
        self.green_pix = QPixmap('./quarter_note_green.png').scaledToHeight(214)

        self.changeColor(QColor("black"))
       
       
        self.upside_pix = QPixmap('./quarter_note_upside.png').scaledToHeight(214)
        self.upside_red_pix = QPixmap('./quarter_note_upside_red.png').scaledToHeight(214)
        self.upside_green_pix = QPixmap('./quarter_note_upside_green.png').scaledToHeight(214)


    
    
    def changeColor(self, color="black"):
        if(self.is_curr_pix_normal):
            if (color == "red"):
                self.setPixmap(self.red_pix)
            elif (color == "green"):
                self.setPixmap(self.green_pix)
            else:
                self.setPixmap(self.pix)
        else:   
            if (color == "red"):
                self.setPixmap(self.upside_red_pix)
            elif (color == "green"):
                self.setPixmap(self.upside_green_pix)
            else:
                self.setPixmap(self.upside_pix)

      

    def hideLedgerLines(self):
        for ledger in self.ledger_lines:
            ledger.hide()
    
    def showLedgerLines(self, line_num):
        if (line_num > 30 or line_num < -30):
            return
        if (line_num < -1):
            self.ledger_lines[3].show()
            if (line_num < -3):
                self.ledger_lines[2].show()
                if (line_num < -5):
                    self.ledger_lines[1].show()
                    if (line_num < -7):
                        self.ledger_lines[0].show()

        if (line_num > 9):
            self.ledger_lines[4].show()
            if (line_num > 11):
                self.ledger_lines[5].show()
                if (line_num > 13):
                    self.ledger_lines[6].show()
                    if (line_num > 15):
                        self.ledger_lines[7].show()

    def initLedgerLines(self, parent):
        ledger_lines = []

        for i in range(8):
            ledger_label = QLabel(parent)
            if (i < 4):
                ledger_label.move(228, 538 - 40*i)
            else:
                ledger_label.move(232, 122 - 40*(i-4))

            ledger_label.setPixmap(QPixmap('./ledger_line.png'))
            ledger_lines.append(ledger_label)
        
        return ledger_lines

    def setPix(self, is_normal = True):
        if (is_normal):
            self.setPixmap(self.pix)
            self.is_curr_pix_normal = True
        else:
            self.setPixmap(self.upside_pix)
            self.is_curr_pix_normal = False

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        layout = QVBoxLayout()
    
        self.treble_clef_label = QLabel()
        treble_clef_pix = QPixmap('./treble_clef.jpg')
        treble_clef_pix = treble_clef_pix.scaledToHeight(640)
        self.treble_clef_label.setPixmap(treble_clef_pix)
       
        layout.addWidget(self.treble_clef_label)
        
        self.quarter_note_label = QuarterNote(self.treble_clef_label)
        self.quarter_note_label.move(170, -1000)

        layout.setContentsMargins(200, 11, 200, 11)
        self.treble_clef_label.setScaledContents(True)
        self.setLayout(layout)
        
        self.target_line_number = -1000

        self.threadpool = QThreadPool()

        self.midi_worker = MidiWorker()
        self.midi_worker.signal.note_recieved.connect(self.checkIfCorrect)

        self.note_generator = GenerateNoteWorker('C', "medium")
        self.note_generator.signal.note_generated.connect(self.setTargetLineNumber)
        
        self.threadpool.start(self.midi_worker)
        self.threadpool.start(self.note_generator)

        for synth in self.midi_worker.synths:
            self.threadpool.start(synth)
    
    def checkIfCorrect(self, line_number):
        print("target", self.target_line_number, "acutal", line_number)

        if (line_number == self.target_line_number):
            self.quarter_note_label.changeColor("green")
            self.note_generator.resetNote()
        else:
            self.quarter_note_label.changeColor("red")
            timer = QTimer()
            timer.singleShot(500, self.quarter_note_label.changeColor)
      

            
            
    def setTargetLineNumber(self, line_number):
        self.quarter_note_label.changeColor("black")
        self.target_line_number = line_number
        self.createNoteAtLineNumber(line_number)

    def createNoteAtLineNumber(self, line_number):
        BOTTOM_OF_STAFF = 224
        BOTTOM_OF_STAFF_LEDGER = 230
        BOTTOM_OF_STAFF_UPSIDE = 378
        BOTTOM_OF_STAFF_UPSIDE_LEDGER = 376
        LINE_WIDTH = 27
        LEDGER_LINE_WIDTH = 20

        if (self.quarter_note_label.is_curr_pix_normal):
            if (line_number >= 4):
                self.quarter_note_label.setPix(is_normal = False)
                y_pos = BOTTOM_OF_STAFF_UPSIDE - line_number*LINE_WIDTH
            else:
                y_pos = BOTTOM_OF_STAFF - line_number*LINE_WIDTH
        else:
            if (line_number < 4):
                self.quarter_note_label.setPix(is_normal = True)
                y_pos = BOTTOM_OF_STAFF - line_number*LINE_WIDTH
            else:
                y_pos = BOTTOM_OF_STAFF_UPSIDE - line_number*LINE_WIDTH
        
        self.quarter_note_label.hideLedgerLines()
        self.quarter_note_label.showLedgerLines(line_number)
        if (line_number > 8):
            y_pos = BOTTOM_OF_STAFF_UPSIDE_LEDGER - (8*LINE_WIDTH + (line_number - 8)*LEDGER_LINE_WIDTH)
        elif (line_number < 0):
            y_pos = BOTTOM_OF_STAFF_LEDGER - line_number*LEDGER_LINE_WIDTH
      
        self.quarter_note_label.move(170, y_pos)

if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    dark_theme(qApp)
    window = MainWindow()
    window.resize(WIDTH, HEIGHT)
    window.show()
    sys.exit(qApp.exec_())
"""
 # @author nebuchadnezzar
 # @email michele.ferro1998@libero.it
 # @create date 03-11-2021 12:51:37
 # @modify date 04-01-2022 23:29:45
 # @desc video interpolation project (subject: Multimedia)
"""
import os
import numpy as np
import cv2

from PyQt5 import QtCore, QtGui, QtWidgets as qtw
from PyQt5 import QtMultimedia as qtm
from PyQt5.QtMultimediaWidgets import QVideoWidget

# --- GUI CLASS ---

class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        layout = qtw.QGridLayout()
        title = "Video interpolator"
        icon = QtGui.QIcon('icon.png')

        layout.addWidget(self.createInputOutputGroup(),0,0,1,3)
        layout.addWidget(self.createInputInfoGroup(),1,0)
        layout.addWidget(self.createInterpolationGroup(),1,1,1,2)

        self.pbar = qtw.QProgressBar()
        self.btn = qtw.QPushButton("RUN")
        self.helpbtn = qtw.QPushButton("HELP")

        self.btn.setDisabled(True)

        self.btn.clicked.connect(self.doInterpolation)
        self.helpbtn.clicked.connect(self.callHelp)
        
        layout.addWidget(self.pbar,5,0,1,3)
        layout.addWidget(self.helpbtn,6,1,1,1)
        layout.addWidget(self.btn,6,2)

        self.setWindowTitle(title)
        self.setFixedSize(500,300)
        self.setWindowIcon(icon)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setLayout(layout)
        self.show()

    # UI CREATION FUNCTIONS

    # creates a group with a label and a button: 
    # the label describes the filepath chosen using the button
    def createInputOutputGroup(self):
        groupBox = qtw.QGroupBox("Input/Output")

        btn1 = qtw.QPushButton("&Choose...")
        btn1.clicked.connect(self.getfile)

        self.label1 = qtw.QLineEdit(readOnly=True)

        self.btn2 = qtw.QPushButton("&Save...")
        self.btn2.clicked.connect(self.saveFile)

        self.label2 = qtw.QLineEdit(readOnly=True)

        grid = qtw.QGridLayout()
        grid.addWidget(self.label1,0,0)
        grid.addWidget(btn1,0,1)
        grid.addWidget(self.label2,1,0)
        grid.addWidget(self.btn2,1,1)
        groupBox.setLayout(grid)

        return groupBox

    # describes the input video file giving the following infos:
    # - width
    # - height
    # - framerate
    # - size in MB
    def createInputInfoGroup(self):
        groupBox = qtw.QGroupBox("Input info")
        width_label = qtw.QLabel("&Width")
        height_label = qtw.QLabel("&Height")
        framerate_label = qtw.QLabel("&Framerate")
        size_label = qtw.QLabel("&Size")

        self.width_out = qtw.QLineEdit(readOnly=True, text="pixel")
        self.height_out = qtw.QLineEdit(readOnly=True, text="pixel")
        self.framerate_out = qtw.QLineEdit(readOnly=True, text="fps")
        self.size_out = qtw.QLineEdit(readOnly=True, text="MB")

        width_label.setBuddy(self.width_out)
        height_label.setBuddy(self.height_out)
        framerate_label.setBuddy(self.framerate_out)
        size_label.setBuddy(self.size_out)

        grid = qtw.QGridLayout()
        grid.addWidget(width_label,0,0)
        grid.addWidget(height_label,1,0)
        grid.addWidget(framerate_label,2,0)
        grid.addWidget(size_label,3,0)  

        grid.addWidget(self.width_out,0,1)
        grid.addWidget(self.height_out,1,1)
        grid.addWidget(self.framerate_out,2,1)
        grid.addWidget(self.size_out,3,1)   
        groupBox.setLayout(grid)
        
        return groupBox

    # creates a group with an fps selector and two radio buttons, 
    # to choose the interpolation mode
    def createInterpolationGroup(self):
        groupBox = qtw.QGroupBox("Interpolation")
        label = qtw.QLabel("FPS:")
        self.fps_spinbox = qtw.QSpinBox(value=60, minimum=1, maximum=300)
        self.dup_radio = qtw.QRadioButton(text="dup [FAST - LOW QUALITY]")
        self.blend_radio = qtw.QRadioButton(text="blend [SLOWER - GOOD QUALITY]")

        self.dup_radio.setChecked(True)

        grid = qtw.QGridLayout()
        grid.addWidget(label,0,0)
        grid.addWidget(self.fps_spinbox,0,1,1,2)
        grid.addWidget(self.dup_radio,1,0,1,5)
        grid.addWidget(self.blend_radio,2,0,1,5)    

        self.disableInput()  
        
        groupBox.setLayout(grid)
        
        return groupBox

    # SERVICE AND GUI UPDATE FUNCTIONS
    # calls help window
    def callHelp(self):
        self.help = HelpWindow()
        self.help.show()
    
    # disables the GUI when there is not an input file
    def disableInput(self):
        self.fps_spinbox.setDisabled(True)
        self.blend_radio.setDisabled(True)
        self.dup_radio.setDisabled(True)
        self.btn2.setDisabled(True)

    # enables the GUI when there is an input file
    def enableInput(self):
        self.fps_spinbox.setDisabled(False)
        self.blend_radio.setDisabled(False)
        self.dup_radio.setDisabled(False)
        self.btn2.setDisabled(False)

    # updates the progress bar during the interpolation
    def updateProgressBar(self,value):
        self.pbar.setValue(value)
    
    # calls the file selector to choose an input file
    def getfile(self):
        fname, _ = qtw.QFileDialog.getOpenFileName(self, 'Open file', '.', "Video files (*.mp4)")

        self.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))                                  # sets cursor in wait state when loading the input file

        if fname:
            self.frames_in, self.size, self.fps_in = read_video(fname)
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))                             # restores cursor state
            hd_size = os.path.getsize(fname) / 1000000

            self.label1.setText(fname)
            self.width_out.setText(str(self.size[0]) + ' pixel')
            self.height_out.setText(str(self.size[1]) + ' pixel')
            self.framerate_out.setText(str(self.fps_in) + ' fps')
            self.size_out.setText(str(hd_size) + ' MB')
            self.enableInput()

    # calls the file selector to save the output file
    def saveFile(self):
        self.fdir, _ = qtw.QFileDialog.getSaveFileName(self, 'Save file', '.', 'Video files (*.mp4)')
        
        if self.fdir:
            self.label2.setText(self.fdir)
            self.btn.setDisabled(False)                         # enables RUN button only when there is a save file

    # EXECUTION
    def doInterpolation(self):
        l_frames_in = len(self.frames_in)                       # number of total frames in input video
        fps_out = self.fps_spinbox.value()

        if fps_out > self.fps_in:
            multiplier = round(fps_out/self.fps_in)
            l_frames_out = l_frames_in * multiplier             # number of total frames in output video

            if self.dup_radio.isChecked(): self.frames_out = dup(self.frames_in, l_frames_out)
            elif self.blend_radio.isChecked(): self.frames_out = blend(self.frames_in, l_frames_out)
        else:
            divisor = round(self.fps_in/fps_out)
            l_frames_out = round(l_frames_in/divisor)

            self.frames_out = gen_reduced_out(self.frames_in, l_frames_out)

        output_video = generate_video(self.fdir, self.fps_spinbox.value(), self.size)

        for f in self.frames_out:
            output_video.write(f)

        output_video.release()

class HelpWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        layout = qtw.QVBoxLayout()
        self.setWindowTitle("Help")
        self.setFixedSize(400,300)
        icon = QtGui.QIcon('icon.png')
        
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        help_text = 'This Python program simulates <b>ffmpeg</b>\'s minterpolate command on a given video file.<br>\
                    After choosing an input video file and the output destination folder, if the desired new framerate is higher than the input\'s one, you can choose between two interpolation modes:<br>\
                    - <b>dup</b>: all the \"missing frames\" in the output video are equal to their predecessor (so, the frame <i>i</i> is a duplicate of the frame <i>i-1</i>) [<b>FAST</b>];<br>\
                    - <b>blend</b>: all the \"missing frames\" in the output video are blended calculating the mean between their predecessor and their successor (so, the frame <i>i</i> is extimated by an average between the frame <i>i-1</i> and the frame <i>i+1</i>) <b>[SLOW]</b>.\
                    If, instead, the chosen new framerate is lower than the input\'s one, the selection of the mode will be ignored and the needless intermediate frames will be discarded, so that the new video will result in a lower framerate.'
        
        auth_text = '@<b>nebuchadneZZar01</b> (Michele Ferro) ~ V1.0 [2022]'

        label1 = qtw.QLabel(help_text)
        label2 = qtw.QLabel(auth_text)
        label1.setWordWrap(True)
        label1.setAlignment(QtCore.Qt.AlignJustify)

        btn = qtw.QPushButton("OK")
        btn.clicked.connect(lambda: self.close())
        
        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(btn)
        self.setLayout(layout)


# ---- CALCULATION FUNCTIONS ----

# normalization in [0,100] for progressbar
def normalize(value, min, max):
    return int(((value-min)/(max-min))*100)

def gen_out(in_a, new_length):
    old_length = len(in_a)
    step = round(new_length/old_length)
    
    # create new empty array (it will contain the frames)
    out_a = np.array([None]*new_length)                                              

    # inserting each frame of the input video with a step 
    for i in range(old_length):
        j = i * step
        if j < new_length:
            out_a[j] = in_a[i]

    return out_a, old_length, step

# dup mode: the frame i is equal to frame i-1 (his predecessor)
def dup(in_a, new_length):
    out_a, old_length, step = gen_out(in_a, new_length)

    for i in range(new_length):
        MainWindow.updateProgressBar(mw, normalize(i,0,new_length-1))
        if out_a[i] is not None: pass
        else: out_a[i] = out_a[i-1]

    return out_a

# blend mode: the frame i is given by the average between frame i-1 (its predecessor) and frame i+1 (its successor)
def blend(in_a, new_length):    
    out_a, old_length, step = gen_out(in_a, new_length)

    # first case: fill the "empty frame" with the average between his successor and his predecessor
    if round(new_length/old_length) == 2:
        fake_new_length = old_length*2
        for i in range(fake_new_length):
            MainWindow.updateProgressBar(mw, normalize(i,0,fake_new_length-1))
            if out_a[i] is not None: pass
            elif i+1 < fake_new_length: out_a[i] = np.mean(np.array([out_a[i-1],out_a[i+1]], dtype='object'), axis=0).astype('uint8')
            else: 
                zero_shape = out_a[i-1].shape 
                out_a[i] = np.mean(np.array([out_a[i-1],np.zeros(zero_shape)], dtype='object'), axis=0).astype('uint8')
        # fill possible odd frames making average with black
        if new_length%old_length != 0:
            tmp = out_a[fake_new_length-1:new_length+1]
            for i in range(len(tmp)):
                if i == 0: pass
                else:
                    zero_shape = tmp[i-1].shape 
                    tmp[i] = np.mean(np.array([tmp[i-1],np.zeros(zero_shape)], dtype='object'), axis=0).astype('uint8')
    # second case: we have more than one empty frame, so when we have to calculate the average between the frame i and every frame in the step
    else: 
        for i in range(new_length):
            if i == 0: pass
            # dividing the list in chunks
            else:
                j = i * step
                if j < new_length:
                    #print(j)
                    tmp = out_a[j-step:j+1]
                    # for every chunk, calculate the average
                    for z in range(len(tmp)):
                        if tmp[z] is None:
                            #print("index: ", z-1, j)
                            tmp[z] = np.mean(np.array([tmp[z-1],tmp[-1]], dtype='object'), axis=0).astype('uint8')
                    #print(tmp)
            MainWindow.updateProgressBar(mw, normalize(i,0,new_length-1))
        tmp = out_a[new_length-step:new_length]
        # print(tmp)
        # remaining odd frames: average with black
        for i in range(len(tmp)):
            if i == 0: pass
            else:
                #print(i)
                zero_shape = tmp[i-1].shape
                tmp[i] = np.mean(np.array([tmp[i-1],np.zeros(zero_shape)], dtype='object'), axis=0).astype('uint8')
        #print(out_a[new_length-step:new_length])

    return out_a

# to reduce framerate
def gen_reduced_out(in_a, new_length):
    old_length = len(in_a)
    step = round(old_length/new_length)                                           
    
    out_a = []

    i = 0
    while i < old_length:
        out_a.append(in_a[i])
        MainWindow.updateProgressBar(mw, normalize(i,0,old_length-1))
        i = i + step

    out_a = np.array(out_a)
    return out_a


# ---- VIDEO FUNCTIONS ----

def input_video(filepath):
    in_vid = cv2.VideoCapture(filepath)
    width = int(in_vid.get(3))                                                      # le info sulle dimensioni wxh stanno rispettivamente alle posizioni 3 e 4 dell'header
    height = int(in_vid.get(4))
    fps_in = int(in_vid.get(5))
    frame_in_count = int(in_vid.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_in = frame_in_count/fps_in
    size = (width, height)

    return in_vid, size, fps_in

def read_video(filepath):
    in_vid, size, fps_in = input_video(filepath)
    ret, frame = in_vid.read()

    frames_in = []

    while (in_vid.isOpened()):
        prev_frame = frame[:]
        ret, frame = in_vid.read()
        if ret:
            if (frame is not None):
                frames_in.append(frame)
        else: break
    
    in_vid.release()
    return frames_in, size, fps_in

def generate_video(filepath, fps_output, size):
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')                                                # DIVX is the best encoder until now (mpg4 gave too much large output files)
    output_video = cv2.VideoWriter(filepath, fourcc, fps_output, size, isColor = True)

    return output_video


# ---- MAIN EXECUTION ----
app = qtw.QApplication([])
mw = MainWindow()

app.exec()
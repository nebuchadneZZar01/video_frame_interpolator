"""
 # @author nebuchadnezzar
 # @email michele.ferro1998@libero.it
 # @create date 03-11-2021 12:51:37
 # @modify date 23-01-2022 11:40:55
 # @desc video interpolation project (subject: Multimedia)
"""
import os
import platform                                     # for GUI size
from statistics import mode
from matplotlib.pyplot import draw
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

        layout.addWidget(self.createInputOutputGroup(),0,0,1,3)
        layout.addWidget(self.createInputInfoGroup(),1,0)
        layout.addWidget(self.createInterpolationGroup(),1,1,1,2)

        self.pbar = qtw.QProgressBar()
        self.btn = qtw.QPushButton("Run")
        self.helpbtn = qtw.QPushButton("Help")
        self.cmprbtn = qtw.QPushButton("Compare")

        self.btn.setDisabled(True)
        self.cmprbtn.setDisabled(True)

        self.btn.clicked.connect(self.doInterpolation)
        self.helpbtn.clicked.connect(self.callHelp)
        self.cmprbtn.clicked.connect(self.callCompare)
        
        layout.addWidget(self.pbar,5,0,1,3)
        layout.addWidget(self.cmprbtn,6,0,1,1)
        layout.addWidget(self.helpbtn,6,1,1,1)
        layout.addWidget(self.btn,6,2)

        self.setWindowTitle(title)
        if platform.system() == 'Windows': self.setFixedSize(500,320)
        else: self.setFixedSize(600,375)
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
        self.mci_gf_radio = qtw.QRadioButton(text="mci (Farneback) [SLOWEST - BEST QUALITY]")
        self.mci_lk_radio = qtw.QRadioButton(text="mci (Lucas-Kanade) [SLOWEST - BEST QUALITY]")

        self.dup_radio.setChecked(True)

        grid = qtw.QGridLayout()
        grid.addWidget(label,0,0)
        grid.addWidget(self.fps_spinbox,0,1,1,2)
        grid.addWidget(self.dup_radio,1,0,1,5)
        grid.addWidget(self.blend_radio,2,0,1,5)
        grid.addWidget(self.mci_gf_radio,3,0,1,5)
        grid.addWidget(self.mci_lk_radio,4,0,1,5)    

        self.disableInput()  
        
        groupBox.setLayout(grid)
        
        return groupBox

    # SERVICE AND GUI UPDATE FUNCTIONS
    # calls help window
    def callHelp(self):
        self.help = HelpWindow()
        self.help.show()

    # calls compare window
    def callCompare(self):
        self.compare = CompareWindow()
        self.compare.show()
    
    # disables the GUI when there is not an input file
    def disableInput(self):
        self.fps_spinbox.setDisabled(True)
        self.blend_radio.setDisabled(True)
        self.dup_radio.setDisabled(True)
        self.mci_gf_radio.setDisabled(True)
        self.mci_lk_radio.setDisabled(True)
        self.btn2.setDisabled(True)

    # enables the GUI when there is an input file
    def enableInput(self):
        self.fps_spinbox.setDisabled(False)
        self.blend_radio.setDisabled(False)
        self.dup_radio.setDisabled(False)
        self.mci_gf_radio.setDisabled(False)
        self.mci_lk_radio.setDisabled(False)
        self.btn2.setDisabled(False)

    # updates the progress bar during the interpolation
    def updateProgressBar(self,value):
        self.pbar.setValue(value)
    
    # calls the file selector to choose an input file
    def getfile(self):
        self.fname, _ = qtw.QFileDialog.getOpenFileName(self, 'Open file', '.', "Video files (*.mp4)")

        self.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))                                  # sets cursor in wait state when loading the input file

        if self.fname:
            self.frames_in, self.size, self.fps_in = read_video(self.fname)
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))                             # restores cursor state
            hd_size = os.path.getsize(self.fname) / 1000000

            self.label1.setText(self.fname)
            self.width_out.setText(str(self.size[0]) + ' pixel')
            self.height_out.setText(str(self.size[1]) + ' pixel')
            self.framerate_out.setText(str(self.fps_in) + ' fps')
            self.size_out.setText(str(hd_size) + ' MB')
            self.enableInput()
        if not(self.fname):
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor)) 

    # calls the file selector to save the output file
    def saveFile(self):
        self.fdir, _ = qtw.QFileDialog.getSaveFileName(self, 'Save file', '.', 'Video files (*.mp4)')
        
        if self.fdir:
            self.label2.setText(self.fdir)
            self.btn.setDisabled(False)                         # enables RUN button only when there is a save file

    # returns input filepath (used in comparison window)
    def getFname(self):
        return self.fname

    # returns input filepath (used in comparison window)
    def getFdir(self):
        return self.fdir

    # EXECUTION
    def doInterpolation(self):
        self.btn.setDisabled(True)
        self.label1.deselect()                                  # to prevent text selection bug in input filepath label
        l_frames_in = len(self.frames_in)                       # number of total frames in input video
        fps_out = self.fps_spinbox.value()

        if fps_out > self.fps_in:
            multiplier = round(fps_out/self.fps_in)
            l_frames_out = l_frames_in * multiplier             # number of total frames in output video

            if self.dup_radio.isChecked(): self.frames_out = dup(self.frames_in, l_frames_out)
            elif self.blend_radio.isChecked(): self.frames_out = blend(self.frames_in, l_frames_out)
            elif self.mci_gf_radio.isChecked(): self.frames_out = mci(self.frames_in, l_frames_out, "GF")
            elif self.mci_lk_radio.isChecked(): self.frames_out = mci(self.frames_in, l_frames_out, "LK")
        else:
            divisor = round(self.fps_in/fps_out)
            l_frames_out = round(l_frames_in/divisor)

            self.frames_out = gen_reduced_out(self.frames_in, l_frames_out)

        output_video = generate_video(self.fdir, self.fps_spinbox.value(), self.size)

        for f in self.frames_out:
            output_video.write(f)
        
        del(self.frames_out)                                                                        # to prevent memory leak of output array

        if self.pbar.value() == 100: 
            qtw.QMessageBox.information(self, "Message", "Interpolation completed!")                # shows an informative maessagebox when the interpolation is completed
            self.cmprbtn.setDisabled(False)                                                         # enables compare button, which calls the comparison window between input and output file
            self.btn.setDisabled(False)

        output_video.release()

# HELP POP-UP CLASS
class HelpWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        layout = qtw.QVBoxLayout()
        self.setWindowTitle("Help")
        if platform.system() == 'Windows': self.setFixedSize(450,300)
        else: self.setFixedSize(550,400)
        
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        help_text = 'This Python program simulates <b>ffmpeg</b>\'s minterpolate command on a given video file.<br>\
                    After choosing an input video file and the output destination folder, if the desired new framerate is higher than the input\'s one, you can choose between two interpolation modes:<br>\
                    - <b>dup</b>: all the \"missing frames\" in the output video are equal to their predecessor (so, the frame <i>i</i> is a duplicate of the frame <i>i-1</i>) [<b>FAST</b>];<br>\
                    - <b>blend</b>: all the \"missing frames\" in the output video are blended calculating the mean between their predecessor and their successor (so, the frame <i>i</i> is extimated by an average between the frame <i>i-1</i> and the frame <i>i+1</i>) <b>[SLOW]</b>;<br>\
                    - <b>mci</b>: all the \"missing frames\" in the output video are extimated using a <b>m</b>otion <b>c</b>ompensated <i>i</i>nterpolation (so, the motion vectors from anchor frame <i>i-1</i> to target frame <i>i+1</i> are calculated to extimate the missing frame <i>i</i>). As for now, to extimate the Optical Flow, can be used the Gunnar-Farneback dense method or the Lucas-Kanade sparse method [<b>SLOWEST</b>]<br>\
                    If, instead, the chosen new framerate is lower than the input\'s one, the selection of the mode will be ignored and the needless intermediate frames will be discarded, so that the new video will result in a lower framerate.'
        
        auth_text = '@<b>nebuchadneZZar01</b> (Michele Ferro) ~ V1.1 [2022]'

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

# COMPARE INPUT AND OUTPUT CLASS
# to make the media player work, you have to install codecs in both Windows and GNU/Linux
class CompareWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        layout = qtw.QGridLayout()
        self.setWindowTitle("Compare input/output")
        self.setFixedSize(1000,500)

        label1 = qtw.QLabel("Input video:")
        label2 = qtw.QLabel("Output video:")
        self.mediaPlayer_input = qtm.QMediaPlayer(None, qtm.QMediaPlayer.VideoSurface)
        self.mediaPlayer_output = qtm.QMediaPlayer(None, qtm.QMediaPlayer.VideoSurface)

        label1.setFixedHeight(25)
        label2.setFixedHeight(25)
        
        videoWidget_input = QVideoWidget()
        videoWidget_output = QVideoWidget()

        replay_btn = qtw.QPushButton("REPLAY VIDEOS")
        replay_btn.clicked.connect(self.replayVideos)

        layout.addWidget(label1,0,0)
        layout.addWidget(label2,0,1)
        layout.addWidget(videoWidget_input,1,0)
        layout.addWidget(videoWidget_output,1,1)
        layout.addWidget(replay_btn,2,0,1,2)

        self.setLayout(layout)

        self.mediaPlayer_input.setVideoOutput(videoWidget_input)
        self.mediaPlayer_output.setVideoOutput(videoWidget_output)

        self.openVideos()
        self.playVideos()

    def openVideos(self):
        f_in = mw.getFname()
        f_out = mw.getFdir()

        if f_in and f_out:
            self.mediaPlayer_input.setMedia(qtm.QMediaContent(QtCore.QUrl.fromLocalFile(f_in)))
            self.mediaPlayer_output.setMedia(qtm.QMediaContent(QtCore.QUrl.fromLocalFile(f_out)))

    def playVideos(self):
        if self.mediaPlayer_input.state() == qtm.QMediaPlayer.PlayingState and self.mediaPlayer_output.state() == qtm.QMediaPlayer.PlayingState:
            self.mediaPlayer_input.pause()
            self.mediaPlayer_output.pause()
        else:
            self.mediaPlayer_input.play()
            self.mediaPlayer_output.play()

    def stopVideos(self):
        self.mediaPlayer_input.stop()
        self.mediaPlayer_output.stop()

    def replayVideos(self):
        self.stopVideos()
        self.playVideos()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.stopVideos()


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

# motion compensation via dense optical flow (Gunnar-Farneback method)
def motion_compensation_Farneback(anchor_frame, target_frame, frame_num):
    prev = cv2.cvtColor(anchor_frame,cv2.COLOR_BGR2GRAY)                            # have to convert in gray in order to have
    next = cv2.cvtColor(target_frame,cv2.COLOR_BGR2GRAY)                            # same channel to calculate motion vectors
    
    flow = cv2.calcOpticalFlowFarneback(prev, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    #ov_visualization(anchor_frame, flow, frame_num)

    h, w = flow.shape[:2]
    flow = -flow
    flow[:,:,0] += np.arange(w)
    flow[:,:,1] += np.arange(h)[:,np.newaxis]

    return flow

def motion_compensation_Lucas_Kanade(anchor_frame, target_frame, frame_num):
    grid_y, grid_x = np.mgrid[0:anchor_frame.shape[0]:1, 0:anchor_frame.shape[1]:1]
    p0 = np.stack((grid_x.flatten(),grid_y.flatten()),axis=1).astype(np.float32)

    p1, status, err = cv2.calcOpticalFlowPyrLK(anchor_frame, target_frame, p0, None)

    flow = np.reshape(p1 - p0, (anchor_frame.shape[0], anchor_frame.shape[1], 2))

    #ov_visualization(anchor_frame, flow, frame_num)

    h, w = flow.shape[:2]
    flow = -flow
    flow[:,:,0] += np.arange(w)
    flow[:,:,1] += np.arange(h)[:,np.newaxis]

    return flow

def motion_compensation(anchor_frame, target_frame, frame_num, mode):
    if mode == "GF": flow = motion_compensation_Farneback(anchor_frame, target_frame, frame_num)
    elif mode == "LK": flow = motion_compensation_Lucas_Kanade(anchor_frame, target_frame, frame_num)

    return flow

def draw_hsv(anchor_frame, flow):
    hsv = np.zeros_like(anchor_frame)
    hsv[...,1] = 255
    
    mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])

    hsv[...,0] = ang*180/np.pi/2
    hsv[...,2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return bgr

def ov_visualization(anchor_frame, flow, frame_num):
    fname = 'img\\' + "HSV" + '\ov_' + str(frame_num) + '.jpg'
    vis = draw_hsv(anchor_frame,flow)
    
    print(fname)
    cv2.imwrite(fname, vis)

# mci mode: the frame i is given by the motion compensation between frame i-1 (its predecessor) and frame i+1 (its successor)
def mci(in_a, new_length, mode):
    out_a, old_length, step = gen_out(in_a, new_length)

    # first case: fill the "empty frame" with the motion compensation between his successor and his predecessor
    if round(new_length/old_length) == 2:
        fake_new_length = old_length*2
        for i in range(fake_new_length):
            MainWindow.updateProgressBar(mw, normalize(i,0,fake_new_length-1))
            if out_a[i] is not None: pass
            elif i+1 < fake_new_length:
                flow = motion_compensation(out_a[i-1], out_a[i+1], i, mode)
                out_a[i] = cv2.remap(out_a[i-1], flow, None, cv2.INTER_LINEAR)
            else:
                flow = motion_compensation(out_a[i-1], np.zeros_like(out_a[i-1]), i, mode)
                out_a[i] = cv2.remap(out_a[i-1], flow, None, cv2.INTER_LINEAR)
    else:
        for i in range(new_length):
            if i == 0: pass
            # dividing the list in chunks
            else:
                j = i * step
                if j < new_length:
                    tmp = out_a[j-step:j+1]
                    # for every chunk, calculate the motion compensation
                    for z in range(len(tmp)):
                        if tmp[z] is None:
                            flow = motion_compensation(tmp[z-1], tmp[-1], i, mode)
                            tmp[z] = cv2.remap(tmp[z-1], flow, None, cv2.INTER_LINEAR)
            MainWindow.updateProgressBar(mw, normalize(i,0,new_length-1))
        tmp = out_a[new_length-step:new_length]
        # remaining odd frames: motion compensation with black
        for i in range(len(tmp)):
            if i == 0: pass
            else:
                flow = motion_compensation(tmp[i-1], np.zeros_like(tmp[i-1]), i, mode)
                tmp[i] = cv2.remap(tmp[i-1], flow, None, cv2.INTER_LINEAR)                  
    
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
    MainWindow.updateProgressBar(mw, 100)

    out_a = np.array(out_a)
    return out_a


# ---- VIDEO FUNCTIONS ----

def input_video(filepath):
    in_vid = cv2.VideoCapture(filepath)
    width = int(in_vid.get(3))                                                      # le info sulle dimensioni wxh stanno rispettivamente alle posizioni 3 e 4 dell'header
    height = int(in_vid.get(4))
    fps_in = int(round(in_vid.get(5)))
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
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')                                                # mp4v is the best encoder until now (mpg4 gave too much large output files)
    output_video = cv2.VideoWriter(filepath, fourcc, fps_output, size, isColor = True)

    return output_video


# ---- MAIN EXECUTION ----
app = qtw.QApplication([])
mw = MainWindow()

app.exec()
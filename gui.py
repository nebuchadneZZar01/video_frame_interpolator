"""
 # @author nebuchadnezzar
 # @email michele.ferro1998@libero.it
 # @create date 27-12-2021 17:36:22
 # @modify date 27-12-2021 20:01:17
"""

from PyQt5 import QtCore, QtWidgets as qtw

class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        layout = qtw.QGridLayout()
        title = "Video interpolator"

        self.btn1 = qtw.QPushButton("IN")
        self.btn1.clicked.connect(self.getfile)

        self.label1 = qtw.QLineEdit()

        self.btn2 = qtw.QPushButton("OUT")
        self.btn2.clicked.connect(self.saveFile)

        self.btn3 = qtw.QPushButton("OK")

        self.label2 = qtw.QLineEdit()

        fps_spinbox = qtw.QSpinBox(self, value=30, minimum=1)

        width_label = qtw.QLabel("&Width", self)
        height_label = qtw.QLabel("&Height", self)
        framerate_label = qtw.QLabel("&Framerate", self)
        size_label = qtw.QLabel("&Size", self)

        width_out = qtw.QLineEdit(self)
        height_out = qtw.QLineEdit(self)
        framerate_out = qtw.QLineEdit(self)
        size_out = qtw.QLineEdit(self)

        width_label.setBuddy(width_out)
        height_label.setBuddy(height_out)
        framerate_label.setBuddy(framerate_out)
        size_label.setBuddy(size_out)

        dup_radio = qtw.QRadioButton(self, text="dup")
        blend_radio = qtw.QRadioButton(self, text="blend")

        #InputOutputGroup
        layout.addWidget(self.label1,0,0)
        layout.addWidget(self.btn1,0,1)
        layout.addWidget(self.label2,1,0)
        layout.addWidget(self.btn2,1,1)

        #InfoGroup
        layout.addWidget(width_label,2,0)
        layout.addWidget(height_label,3,0)
        layout.addWidget(framerate_label,4,0)
        layout.addWidget(size_label,5,0)  

        layout.addWidget(width_out,2,1)
        layout.addWidget(height_out,3,1)
        layout.addWidget(framerate_out,4,1)
        layout.addWidget(size_out,5,1)   
        
        #InterpolationGroup
        layout.addWidget(fps_spinbox,2,3)
        layout.addWidget(dup_radio,3,3)
        layout.addWidget(blend_radio,4,3)      

        layout.addWidget(self.btn3,5,3)

        self.setWindowTitle(title)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setLayout(layout)
        self.show()
    
    def getfile(self):
        fname = qtw.QFileDialog.getOpenFileName(self, 'Open file', '.', "Video files (*.mp4)")
        # self.le.setPixmap(qtw.QPixmap(fname))

    def saveFile(self):
        fdir = qtw.QFileDialog.getSaveFileName(self, 'Save file', '.', 'Video files (*.mp4)')

app = qtw.QApplication([])
mw = MainWindow()

app.exec()
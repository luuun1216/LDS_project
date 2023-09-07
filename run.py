import os
import cv2
import time
from PyQt5 import QtGui, QtWidgets, QtCore, QtMultimedia, QtMultimediaWidgets
from PyQt5.QtWidgets import QFileDialog
from natsort import natsorted
from datetime import datetime
import subprocess
from multiprocessing import Process, Queue
import generate_numbers 
import threading
import time
import queue

# 0829_TODO_list 
# 1. Add two button for "save pic" and "save video"
#   - for save pic
#       - after click the button, the sys will show a sub_windows, this sub_window will 
#         have a button call "save", and let user to name the pic
#   - for save video
#       - after click the button, the sys will show a sub_windows, this sub_window will 
#         have a button call "save", and let user to name the video
#       - And the sys will save current frame to next 50 frame(defult)
#       - 50 frame can let user to set , but in the config 
# 2. Add two arrow
#   - these two arrow can let user to add or sub three frame (like youtube)
# 3. We need to do screenshot when the event list add the new event, like the auto save for each video.


# 0905_TODO_list
# 1. auto save function need to add new funciton : when the event list been activate, sys need to save the pic ,for example, when we need save
# the no.50 frame , we also need to save 55 and 45 
# 2. text size adjust
# 3. Add the batch proceess for system. For example, we can load 5 video at the same time, (we can load all the video in the folder)
# 4. Add new function for watch video which Has been completed (load video and txt , and we can see the whole result of this video)



# specify your image folder
image_folder = '.'
button_interval = 50

# get a list of the image file names
image_files = sorted(os.listdir(image_folder))
currentDateAndTime = datetime.now()

if not os.path.exists('pic_temp'):
    os.makedirs('pic_temp')

class Ui_MainWindow(object):
    def create_timestamp(self, num, Mainwindow):
        self.timestamp_button = QtWidgets.QPushButton(self.topFiller)
        self.timestamp_button.setGeometry(QtCore.QRect(60, 15+num*40, 100, 30))
        self.timestamp_button.setObjectName('button')
        self.timestamp_button.setText(str(num*button_interval))
        # print(num)
        
        self.timestamp_button.clicked.connect(lambda: Mainwindow.click_timestamp_button(num))
        self.timestamp_button.show()

    def add_timestamp(self, num, Mainwindow, eventframe_height):
        self.create_timestamp(num, Mainwindow)
        if(15+num*40 > eventframe_height):
            eventframe_height = eventframe_height + 500
            self.topFiller.setMinimumSize(200, eventframe_height)
        print("add timastamp", num)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1211, 877)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_videoframe = QtWidgets.QLabel(self.centralwidget)
        self.label_videoframe.setGeometry(QtCore.QRect(40, 60, 800, 450))
        self.label_videoframe.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.label_videoframe.setObjectName("label_videoframe")

         # add a button to select video
        self.open_button = QtWidgets.QPushButton("Open video", self.centralwidget)
        self.open_button.setGeometry(QtCore.QRect(20, 550, 113, 32))  # set button size and location
        self.open_button.clicked.connect(MainWindow.open_file)  # connect button to open_file function

        self.slider_videoframe = QtWidgets.QSlider(self.centralwidget)
        self.slider_videoframe.setGeometry(QtCore.QRect(150, 560, 531, 22))
        self.slider_videoframe.setOrientation(QtCore.Qt.Horizontal)
        self.slider_videoframe.setObjectName("slider_videoframe")

        # Add Start Button
        self.start_button = QtWidgets.QPushButton("Start", self.centralwidget)
        self.start_button.setGeometry(QtCore.QRect(140, 600, 113, 32))
        self.start_button.clicked.connect(MainWindow.start_video)

        # Add Pause Button
        self.pause_button = QtWidgets.QPushButton("Pause", self.centralwidget)
        self.pause_button.setGeometry(QtCore.QRect(260, 600, 113, 32))
        self.pause_button.clicked.connect(MainWindow.pause_video)

        # Add Stop Button
        self.stop_button = QtWidgets.QPushButton("Stop", self.centralwidget)
        self.stop_button.setGeometry(QtCore.QRect(380, 600, 113, 32))
        self.stop_button.clicked.connect(MainWindow.stop_video)

        # Assuming this is part of your Ui_MainWindow setupUi function:
        self.button_rewind = QtWidgets.QPushButton(self.centralwidget)
        self.button_rewind.setGeometry(QtCore.QRect(140, 650, 30, 30))  # adjust the coordinates and size as needed
        self.button_rewind.setText("<<")  # using << for rewind
        self.button_rewind.setObjectName("button_rewind")
        self.button_rewind.clicked.connect(self.rewind_video)

        self.button_fast_forward = QtWidgets.QPushButton(self.centralwidget)
        self.button_fast_forward.setGeometry(QtCore.QRect(190, 650, 30, 30))  # adjust the coordinates and size as needed
        self.button_fast_forward.setText(">>")  # using >> for fast forward
        self.button_fast_forward.setObjectName("button_fast_forward")
        self.button_fast_forward.clicked.connect(self.fast_forward_video)

        # Assuming this is part of your Ui_MainWindow setupUi function:
        self.button_save = QtWidgets.QPushButton(self.centralwidget)
        self.button_save.setGeometry(QtCore.QRect(600, 700, 80, 30))  # adjust the coordinates and size as needed
        self.button_save.setText("Save pic")
        self.button_save.setObjectName("button_save")
        # Connect the signals to slots (functions)
        self.button_save.clicked.connect(self.save_current_frame)

        self.save_video_btn = QtWidgets.QPushButton("Save Video", self.centralwidget)
        self.save_video_btn.setGeometry(QtCore.QRect(700, 700, 80, 30))  # set button size and location
        self.save_video_btn.clicked.connect(self.save_video_segment)

        self.label_framecnt = QtWidgets.QLabel(self.centralwidget)
        self.label_framecnt.setGeometry(QtCore.QRect(700, 560, 171, 21))
        self.label_framecnt.setObjectName("label_framecnt")
        
        self.label_filepath = QtWidgets.QLabel(self.centralwidget)
        self.label_filepath.setGeometry(QtCore.QRect(40, 790, 841, 41))
        self.label_filepath.setObjectName("label_filepath")

        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(900, 60, 250, 450))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.topFiller = QtWidgets.QWidget()
        self.topFiller.setMinimumSize(200, 450)
        self.vbox = QtWidgets.QVBoxLayout()
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self.topFiller)
        self.vbox.addWidget(self.scroll)
        self.frame.setLayout(self.vbox)

        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(430, 260, 181, 51))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.hide()
        
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_videoframe.setText(_translate("MainWindow", "video_player"))
        self.open_button.setText(_translate("MainWindow", "Openfile"))
        self.label_framecnt.setText(_translate("MainWindow", "current_frame/total_frame"))
        self.label_filepath.setText(_translate("MainWindow", "file path:"))

class newWindow(QtWidgets.QWidget):
    # def __init__(self, num):
    #     super().__init__()
    #     self.num = num
    #     self.currentFrameIndex = 0
    #     self.frames = []
        
    #     self.setWindowTitle('New Window')
        
    #     self.initUI()
    #     self.loadFrame(num)
    def __init__(self, start_frame, end_frame, frames=[]):
        super().__init__()
        self.frames_qimage = [QtGui.QImage(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888) for frame in frames]
        self.frames = frames
        self.currentFrameIndex = 0
        self.setWindowTitle('New Window')
        self.initUI()

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)
        
        # QLabel for displaying frames
        self.frameLabel = QtWidgets.QLabel(self)
        self.layout.addWidget(self.frameLabel)
        
        # Button to save frames as video
        self.saveButton = QtWidgets.QPushButton("Save Video", self)
        self.saveButton.clicked.connect(self.save_frames_as_video)
        self.layout.addWidget(self.saveButton)
        
        # Start displaying frames as GIF
        self.startGIF()

    def startGIF(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateGIF)
        self.timer.start(100)  # 500ms per frame
    def updateGIF(self):
        if self.frames_qimage:
            pixmap = QtGui.QPixmap.fromImage(self.frames_qimage[self.currentFrameIndex])
            self.frameLabel.setPixmap(pixmap)
            self.currentFrameIndex = (self.currentFrameIndex + 1) % len(self.frames_qimage)
    def save_frames_as_video(self):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Video", "", "Video Files (*.mp4);;All Files (*)", options=options)
        if fileName:
            if not fileName.endswith('.mp4'):
                fileName += '.mp4'
            
            # Define the codec and create VideoWriter object. We use 'mp4v' for mp4 files.
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(fileName, fourcc, 20.0, (self.frames[0].shape[1], self.frames[0].shape[0]))
            
            if not out.isOpened():
                print("Error: Video writer couldn't be opened. Check the path or codec.")
                return

            for frame in self.frames:
                out.write(frame)

            out.release()
            print(f"Video saved at {fileName}")

    def Show(self):
        self.show()

     
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, newWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.idx = 0
        self.video_path = ""  # path to the video file
        self.cap = None  # cv2.VideoCapture object
        self.timer_id = None  # timer_id to None initially
        self.current_frame_no = 0
        self.current_frame = None
        self.video_total_frame_count = 0
        self.frame_count = 0
        self.slider_videoframe.valueChanged.connect(self.slider_changed)
    def timerEvent(self, event):
        if event.timerId() != self.timer_id or self.cap is None:
            return

        ret, frame = self.cap.read()
        f = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if ret:
            self.current_frame_no += 1
            self.current_frame = frame
            self.label_framecnt.setText(f"frame number: {self.current_frame_no}/{self.video_total_frame_count}")  # update the label
            self.show_frame(frame)
            self.idx += 1
            # print(self.idx)
            eventframe_height = self.topFiller.height()
            if(self.frame_count%button_interval == 0):
                self.add_timestamp(int(self.frame_count/button_interval), self, eventframe_height)
                
                # Save frame after adding the timestamp
                file_path = os.path.join('pic_temp', f'frame_{self.frame_count}.png')
                
                cv2.imwrite(file_path, self.current_frame)

            self.frame_count += 1
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # h, w, c = frame.shape
            # qimg = QtGui.QImage(frame.data, w, h, c*w, QtGui.QImage.Format_RGB888)
            # pixmap = QtGui.QPixmap.fromImage(qimg)

            # # Scale QPixmap to fit the QLabel size
            # self.label_videoframe.setPixmap(pixmap.scaled(self.label_videoframe.width(),
            #                                               self.label_videoframe.height(),
            #                                               QtCore.Qt.KeepAspectRatio))
            self.slider_videoframe.setValue(self.current_frame_no)
        else:
            self.killTimer(self.timer_id)  # if no more frames, stop the timer
            self.cap.release()
            self.cap = None
            # print(f)
            self.stop_video()

    # function to open file
    def open_file(self):
        
        self.video_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Videos (*.mp4 *.avi *.flv *.mkv)")
        self.progressBar.show() 
        
        ########## 0820 ##########
        max_value = 100
        self.progressBar.setMaximum(max_value)
        self.progressBar.setValue(0)
        result_queue = queue.Queue()
        current_iteration = 1
        total_iterations = 1
        while current_iteration <= total_iterations:
            end = current_iteration * 10
            thread = threading.Thread(target=generate_numbers.print_numbers, args=(end - 9, end, result_queue))
            thread.start()
            thread.join()
            while not result_queue.empty():
                number = result_queue.get()
                # print(f"Received: {number}")
            self.progressBar.setValue(number)
            current_iteration += 1
        ########## 0820 ##########
        self.progressBar.hide()

        if self.video_path:
            # Display the chosen file path in the label
            self.label_filepath.setText(self.video_path)
            if self.cap:
                self.cap.release()

            self.cap = cv2.VideoCapture(self.video_path)
            self.video_total_frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))  # get total frames
            self.slider_videoframe.setMaximum(self.video_total_frame_count - 1)
            if self.timer_id is not None:
                self.killTimer(self.timer_id)
            self.timer_id = self.startTimer(1000//30)  # start a new timer and keep its ID

    def click_timestamp_button(self, num):
        # print("click timestamp button", num)
        # self.nw = newWindow(num)       # 連接新視窗
        # self.nw.show() 
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, num)
            ret, frame = self.cap.read()
            if ret:
                self.current_frame_no = num*button_interval
                self.show_frame(frame)
                self.label_framecnt.setText(f"frame number: {num*button_interval}/{self.video_total_frame_count}")
                self.slider_videoframe.setValue(num*button_interval)
    def jump_to_frame(self, frame_no):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = self.cap.read()
            if ret:
                self.current_frame_no = frame_no
                self.show_frame(frame)
                self.label_framecnt.setText(f"frame number: {frame_no}/{self.video_total_frame_count}")
                self.slider_videoframe.setValue(frame_no)

    def start_video(self):
        if not self.cap:
            return
        if self.timer_id is None:
            self.timer_id = self.startTimer(1000//30)

    def pause_video(self):
        if self.timer_id:
            self.killTimer(self.timer_id)
            self.timer_id = None

    def stop_video(self):
        if self.timer_id:
            self.killTimer(self.timer_id)
            self.timer_id = None
        if self.cap:
            self.cap.release()
            self.cap = None
        self.label_videoframe.clear()
        self.current_frame_no = 0
        self.label_framecnt.setText(f"frame number: {self.current_frame_no}/{self.video_total_frame_count}")

    def slider_changed(self):
        if self.cap:
            frame_no = self.slider_videoframe.value()
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)  # Move to the selected frame
            ret, frame = self.cap.read()
            if ret:
                self.show_frame(frame)
                self.label_framecnt.setText(f"frame number: {frame_no}/{self.video_total_frame_count}")


        
    def show_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, c = frame.shape
        qimg = QtGui.QImage(frame.data, w, h, c*w, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qimg)
        
        # Scale QPixmap to fit the QLabel size
        self.label_videoframe.setPixmap(pixmap.scaled(self.label_videoframe.width(),
                                                        self.label_videoframe.height(),
                                                        QtCore.Qt.KeepAspectRatio))
    def rewind_video(self):
        if self.cap:
            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            desired_frame = max(0, current_frame - 3)
            print(desired_frame)
            self.jump_to_frame(desired_frame)
    def fast_forward_video(self):
        if self.cap:
            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            desired_frame = min(self.video_total_frame_count, current_frame + 3)
            print(desired_frame)
            self.jump_to_frame(desired_frame)
    def save_current_frame(self):
        if self.current_frame is None:
            # If there's no frame currently displayed, exit the function
            return
            
        # Open a save dialog to select where to save the image
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"Save Image", "", "JPEG (*.jpeg);;PNG (*.png);;All Files (*)", options=options)
        
        if fileName:
            # Add appropriate file extension if not provided
            if '.' not in fileName:
                fileName += '.png'  # default to PNG, you can change this

            # Save the frame
            status = cv2.imwrite(fileName, self.current_frame,)

            if not status:
                # If there was an error saving the image, you can notify the user
                print("Error saving image!")
    def save_video_segment(self):
        # Calculate the frames to save
        start_frame = self.current_frame_no
        end_frame = min(self.current_frame_no + 50, self.video_total_frame_count)

        # Ensure the video file is open
        if not self.cap:
            self.cap = cv2.VideoCapture(self.video_path)

        # Go to the start frame
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        # Create a list to store frames
        frames_to_save = []

        # Read and store the frames
        for i in range(start_frame, end_frame):
            ret, frame = self.cap.read()
            if ret:
                frames_to_save.append(frame)

        # Launch a new window to display the video frames as GIF
        self.sub_window = newWindow(start_frame, end_frame, frames_to_save)
        self.sub_window.show()




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
import sys

import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout, QGridLayout, \
    QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from pygame import mixer
from pyqt5_plugins.examplebutton import QtWidgets
from pyqt5_plugins.examplebuttonplugin import QtGui
import tensorflow as tf
from keras.models import load_model

class FirstMainWin(QMainWindow):
    def __init__(self, parent=None):
        super(FirstMainWin, self).__init__(parent)
        # 设置主窗口的标题

        self.setWindowTitle("Driving alarm")
        self.setObjectName("MainWindow")
        self.setStyleSheet("#MainWindow{background-color: #6865CB}")
        self.resize(1820, 1080)

        self.centralwidget = QWidget(self)
        self.grid = QGridLayout(self.centralwidget)
        self.logo = QLabel(self)
        self.logo.setFixedSize(330, 100)
        jpg = QtGui.QPixmap('images/title').scaled(self.logo.width(), self.logo.height())
        self.logo.setPixmap(jpg)
        self.grid.addWidget(self.logo,0,0)

        self.label = QLabel(self)
        self.label.setFixedSize(800, 800)
        jpg = QtGui.QPixmap('images/photo.png').scaled(self.label.width(), self.label.height())
        self.label.setPixmap(jpg)
        self.grid.addWidget(self.label,1,0)

        # 创建按钮
        self.vbox = QVBoxLayout(self.centralwidget)
        startBtn = QPushButton(self)
        startBtn.setFixedSize(350, 80)
        startBtn.setObjectName("start")
        startBtn.setText("GET START")
        startBtn.setStyleSheet(
            "#start{background-color: #333D92;color:#ffffff;font-size:30px;;font-family:Times New Roman}")
        startBtn.clicked.connect(self.getstart)
        self.vbox.addWidget(startBtn)

        # 按钮2
        aboutBtn = QPushButton(self)
        aboutBtn.setObjectName("about")
        aboutBtn.setFixedSize(350, 80)
        aboutBtn.setText("ABOUT US")
        aboutBtn.setStyleSheet(
            "#about{background-color: #333D92;color:#ffffff;font-size:30px;;font-family:Times New Roman}")
        aboutBtn.clicked.connect(self.getAboutus)
        self.vbox.addWidget(aboutBtn)
        self.grid.addLayout(self.vbox,1,1)
        self.setCentralWidget(self.centralwidget)

    def getstart(self):
        self.close()
        self.s = SecondUi()
        self.s.show()
    def getAboutus(self):
        self.close()
        self.t = ThirdUi()
        self.t.show()


class SecondUi(QMainWindow):  # 建立第二个窗口的类
    def __init__(self):
        super(SecondUi, self).__init__()
        self.score = 0
        self.alarmOn = False
        self.timer_camera = QtCore.QTimer()  # 定义定时器，用于控制显示视频的帧率
        self.cap = cv2.VideoCapture()  # 视频流
        self.CAM_NUM = 0  # 为0时表示视频流来自笔记本内置摄像头
        self.timer_camera.timeout.connect(self.show_camera)  # 若定时器结束，则调用show_camera()
        flag = self.cap.open(self.CAM_NUM)  # 参数是0，表示打开笔记本的内置摄像头，参数是视频文件路径则打开视频
        if flag == False:  # flag表示open()成不成功
            msg = QtWidgets.QMessageBox.warning(self, 'warning', "Check your computer camera", buttons=QtWidgets.QMessageBox.Ok)
        else:
            self.timer_camera.start(50)  #

        self.model = tf.keras.models.load_model('./model/weights.07-0.39.hdf5')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        mixer.init()
        self.sound = mixer.Sound(r'./alarm.wav')
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Driving alarm")
        self.setObjectName("MainWindow")
        self.setStyleSheet("#MainWindow{background-color: #6865CB}")
        # 设置窗口的尺寸
        self.resize(1820, 1080)

        self.centralwidget = QWidget(self)
        self.grid = QGridLayout(self.centralwidget)
        # 添加Logo到window
        self.logo = QPushButton(self)
        self.logo.setObjectName("logo")
        self.logo.setFixedSize(330,100)
        self.logo.setStyleSheet(
            "#logo{border-image: url(images/title.png);background-color: #6865CB;}")
        self.logo.clicked.connect(self.back)
        self.grid.addWidget(self.logo,0,0)

        #video
        self.label_show_camera = QtWidgets.QLabel(self)  # 定义显示视频的Label
        self.label_show_camera.setFixedSize(1000, 800)  # 给显示视频的Label设置大小为641x481
        self.grid.addWidget(self.label_show_camera,1,0)

        #status
        self.status = QLabel(self)
        self.status.setFixedSize(500, 600)
        jpg = QtGui.QPixmap('images/danger').scaled(self.status.width(), self.status.height())
        self.status.setPixmap(jpg)
        self.status.hide();
        #self.status.move(1200, 250)
        self.grid.addWidget(self.status,1,1)
        self.setCentralWidget(self.centralwidget)


    def show_camera(self):
        flag, show = self.cap.read()  # 从视频流中读取
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
        self.identify(show)
        show = cv2.resize(show, (1200, 800))
        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                 QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
        self.label_show_camera.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImage
    def close_cap(self):
        self.timer_camera.stop()  # 关闭定时器
        self.cap.release()  # 释放视频流
    def back(self):
        self.close_cap()
        self.close()
        self.firstMainWindow = FirstMainWin()
        self.firstMainWindow.show()
    def identify(self,frame):
        #sound = mixer.Sound(r'./alarm.wav')
        #face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        #eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        #model = tf.keras.models.load_model('./model/weights.07-0.39.hdf5')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3)
        #eyes = self.eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3)
        #cv2.rectangle(frame, (0, height - 50), (200, height), (0, 0, 0), thickness=cv2.FILLED)
        for (x, y, w, h) in faces:
            #cv2.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h), color=(0, 255, 0), thickness=3)
            close = 0;
            eyes = self.eye_cascade.detectMultiScale(gray[y:y+h,x:x+w], scaleFactor=1.2, minNeighbors=5)
            for (ex, ey, ew, eh) in eyes:
                close = 0;
                eye= frame[ey+y:ey+eh+y,ex+x:ex+ew+x]
                eye= cv2.resize(eye,(80,80))
                eye= eye/255
                eye= eye.reshape(80,80,3)
                eye= np.expand_dims(eye,axis=0)
               # preprocessing is done now model prediction
                prediction = self.model.predict(eye)
                #print(prediction)
                if prediction[0][0] > 0.10:
                    cv2.rectangle(frame, pt1=(ex+x, ey+y), pt2=(ex + ew+x, ey + eh+y), color=(255, 0, 0), thickness=3)
                    close += 1;
                    self.score = self.score + 1

                    # if eyes are open
                elif prediction[0][1] > 0.90:
                    cv2.rectangle(frame, pt1=(ex+x, ey+y), pt2=(ex + ew+x, ey + eh+y), color=(0, 255, 0), thickness=3)
                    self.score = self.score - 1
                    if (self.score < 0):
                        self.score = 0
            if close > 0:
                cv2.putText(frame, 'closed', (50, 50), fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale=1,
                            color=(255, 0, 0),
                            thickness=1, lineType=cv2.LINE_AA)

            else:
                cv2.putText(frame, 'open ', (50, 50), fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale=1,
                            color=(0, 255, 0),
                            thickness=1, lineType=cv2.LINE_AA)

            if (self.score > 15):
                try:
                    cv2.putText(frame, 'Score' + str(self.score), (50, 100), fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                fontScale=1, color=(255, 0, 0),
                                thickness=1, lineType=cv2.LINE_AA)
                    # print("alarm")
                    self.status.show();
                    if(self.alarmOn == False):
                        self.sound.play()
                        self.alarmOn = True;
                except:
                    pass
            else:
                cv2.putText(frame, 'Score' + str(self.score), (50, 100), fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL,
                            fontScale=1, color=(0, 255, 0),
                            thickness=1, lineType=cv2.LINE_AA)
                self.status.hide();
                self.sound.stop()
                self.alarmOn = False;
                pass

class ThirdUi(QMainWindow):  #
    def __init__(self,parent='None'):
        super(ThirdUi, self).__init__()
        self.init_ui()
    def init_ui(self):
        self.setWindowTitle("Driving alarm")
        self.setObjectName("MainWindow")
        self.setStyleSheet("#MainWindow{background-color: #6865CB}")
        # 设置窗口的尺寸
        self.resize(1820, 1080)

        self.centralwidget = QWidget(self)
        self.grid = QGridLayout(self.centralwidget)

        # 添加Logo到window
        self.logo = QPushButton(self)
        self.logo.setObjectName("logo")
        self.logo.setFixedSize(330,100)
        self.logo.setStyleSheet(
            "#logo{border-image: url(images/title.png);background-color: #6865CB;}")
        self.logo.clicked.connect(self.back)

        #self.logo.move(50, 35)
        self.grid.addWidget(self.logo,0,0,Qt.AlignLeft)
        #about us Title
        memberTitle = QLabel(self)
        memberTitle.setObjectName("memberTitle")
        memberTitle.setText("Team Member")
        memberTitle.setStyleSheet("#memberTitle{color:#ffffff;font-size:40px;font-weight:800;font-family:Arial;letter-spacing:3px;}")
        memberTitle.setAlignment(Qt.AlignCenter)
        #memberTitle.move(740, 200)
        self.grid.addWidget(memberTitle,1,0,Qt.AlignCenter)
        self.hbox = QHBoxLayout(self.centralwidget)
        self.vbox1 = QVBoxLayout(self.centralwidget)
        #Member 1
        self.member1 = QLabel(self)
        self.member1.setFixedSize(350, 350)
        jpg = QtGui.QPixmap('images/male').scaled(self.member1.width(), self.member1.height())
        self.member1.setPixmap(jpg)
        self.member1.setAlignment(Qt.AlignCenter)
        self.vbox1.addWidget(self.member1)
        #self.member1.move(300, 300)
        name1 = QLabel(self)
        name1.setObjectName("name")
        name1.setText("ZACK BAILEY")
        name1.setStyleSheet("#name{color:#ffffff;font-size:30px;;font-family:Times New Roman;letter-spacing:3px;}")
        name1.setAlignment(Qt.AlignCenter)

        #name1.move(400,670)
        self.vbox1.addWidget(name1)

        #Member 2
        self.vbox2 = QVBoxLayout(self.centralwidget)
        self.member2 = QLabel(self)
        self.member2.setFixedSize(350, 350)
        jpg = QtGui.QPixmap('images/female').scaled(self.member2.width(), self.member2.height())
        self.member2.setPixmap(jpg)
        self.member2.setAlignment(Qt.AlignCenter)
        #self.member2.move(750, 300)
        self.vbox2.addWidget(self.member2)
        name2 = QLabel(self)
        name2.setObjectName("name")
        name2.setText("JIEYING DONG")
        name2.setStyleSheet("#name{color:#ffffff;font-size:30px;;font-family:Times New Roman;letter-spacing:3px;}")
        name2.setAlignment(Qt.AlignCenter)
        #name2.move(800,670)
        self.vbox2.addWidget(name2);

        # Member 2
        self.vbox3 = QVBoxLayout(self.centralwidget)
        self.member3 = QLabel(self)
        self.member3.setFixedSize(350, 350)
        jpg = QtGui.QPixmap('images/male').scaled(self.member3.width(), self.member3.height())
        self.member3.setPixmap(jpg)
        self.member3.setAlignment(Qt.AlignCenter)
        #self.member3.move(1200, 300)
        self.vbox3.addWidget(self.member3)

        name3 = QLabel(self)
        name3.setObjectName("name")
        name3.setText("ZHICHENG LIN")
        name3.setStyleSheet("#name{color:#ffffff;font-size:30px;;font-family:Times New Roman;letter-spacing:3px;}")
        name3.setAlignment(Qt.AlignCenter)
        #name3.move(1270, 670)
        self.vbox3.addWidget(name3);
        self.hbox.addLayout(self.vbox1)
        self.hbox.addLayout(self.vbox2)
        self.hbox.addLayout(self.vbox3)

        self.grid.addLayout(self.hbox,2,0,Qt.AlignCenter)
        #Descript-text 1
        desc1 = QLabel(self)
        desc1.setObjectName("desc")
        desc1.setText("Program: Driver Drowsiness Detection")
        desc1.setStyleSheet("#desc{color:#ffffff;font-size:30px;font-weight:800;font-family:Arial;letter-spacing:3px;}")
        #desc1.move(570, 800)
        desc1.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(desc1,3,0,Qt.AlignCenter)

        #Descript-text 1
        desc2 = QLabel(self)
        desc2.setObjectName("desc")
        desc2.setText("Coordinator: Nabin Sharma")
        desc2.setStyleSheet("#desc{color:#ffffff;font-size:30px;font-weight:800;font-family:Arial;letter-spacing:3px;}")
        #desc2.move(670, 900)
        desc2.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(desc2,4,0,Qt.AlignCenter)
        self.setCentralWidget(self.centralwidget)
    def back(self):
        self.close()
        self.firstMainWindow = FirstMainWin()
        self.firstMainWindow.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon('E:/PycharmProjects/doutula/pyqt5_/controls/images/t10.ico'))
    app.setWindowIcon(QIcon('./images/test.png'))
    main = FirstMainWin()
    main.show()
    sys.exit(app.exec_())
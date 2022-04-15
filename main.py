import os
import sys
import re
import shutil
from PyQt5.Qt import QUrl
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2 as cv
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from gui import *

# 设置全局变量用于存储line edit控件的输入
FPS = '25'
MAX_SEQ_LEN = 'None'
DEVICE = 'True'
# 获取当前路径
CWD = os.getcwd()


# 自定义qt线程类
class MyThread(QThread):
    finish_signal = pyqtSignal(str)

    def __int__(self):
        super(MyThread, self).__init__()

    def run(self):
        global FPS, MAX_SEQ_LEN, DEVICE
        # 推理需要的参数
        self.command = 'python inference_realbasicvsr.py configs/realbasicvsr_x4.py checkpoints/RealBasicVSR_x4.pth temp results/sr_imgs '
        if FPS == '':
            self.command = self.command
        else:
            self.command = self.command + '--fps ' + FPS + ' '
        if MAX_SEQ_LEN == '':
            self.command = self.command
        else:
            self.command = self.command + '--max_seq_len ' + MAX_SEQ_LEN + ' '
        if DEVICE == 'True':
            self.command = self.command
        else:
            self.command = self.command + '--device ' + DEVICE
        # 先CD到当前路径再执行command
        os.system('cd ' + CWD)
        os.system(self.command)
        self.finish_signal.emit('finish')


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        # 存储视频文件的变量
        self.lr_file = None
        self.sr_file = None
        # 设置按键控件
        self.select_btn.clicked.connect(self.select_file)
        self.confirm_btn.clicked.connect(self.sr_process)
        # 设置视频播放控件
        self.lr_video_player = QMediaPlayer()
        self.lr_video_player.setVideoOutput(self.lr_video_widget)
        self.sr_video_player = QMediaPlayer()
        self.sr_video_player.setVideoOutput(self.sr_video_widget)
        self.lr_video_widget.mousePressEvent = self.lr_video_widget_mousePressEvent
        self.sr_video_widget.mousePressEvent = self.sr_video_widget_mousePressEvent
        # 设置line edit控件
        self.fps_lineEdit.setPlaceholderText('FPS：[浮点型][默认25.0]')
        self.fps_lineEdit_validator = QtGui.QDoubleValidator()
        self.max_seq_len_lineEdit.setPlaceholderText('MAX SEQUENCE LENGTH：[整型][默认None]')
        self.max_seq_len_lineEdit_validator = QtGui.QIntValidator()
        self.fps_lineEdit.setValidator(self.fps_lineEdit_validator)
        self.max_seq_len_lineEdit.setValidator(self.max_seq_len_lineEdit_validator)
        self.info_label.setText('BasicVSR++ demo with gui v0.1')
        # 设置进度条控件
        self.progressBar.setValue(0)
        # 实例化一个线程，共超分时候使用
        self.workthread = MyThread()
        # 绑定处理完成时接收到信号对应执行的函数
        self.workthread.finish_signal.connect(self.imgs2video)
        # 获取str类型的lr视频路径所用的正则表达式
        self.pattern = re.compile("'(.*)'")

    def sr_process(self):
        global FPS, MAX_SEQ_LEN, DEVICE
        if self.lr_file is None:
            QMessageBox.critical(self, '错误', '未选择视频文件', QMessageBox.Ok)
            return
        else:
            # 获取str类型的文件路径
            video_path = self.pattern.findall(str(self.lr_file))[0][8:]
            self.video2imgs(video_path)  # 视频转图片
            # 获取line edit参数
            FPS = self.fps_lineEdit.text()
            MAX_SEQ_LEN = self.max_seq_len_lineEdit.text()
            if self.gpu_radioButton.isChecked():
                DEVICE = 'True'
            elif self.cpu_radioButton.isChecked():
                DEVICE = 'False'
            # setRange(0, 0)会显示一个繁忙的指示符而不会显示百分比
            self.progressBar.setRange(0, 0)
            self.info_label.setText('inference and convert to video ...')
            # 把推理放进另一个线程防止主界面卡顿
            self.workthread.start()
            # 调试用
            # self.imgs2video()#单独测试的时候需要把该方法的msg参数去掉

    # 这个感觉也可以放到新的线程里
    def imgs2video(self, msg):
        global FPS
        # 为了获取视频原宽高计算超分的视频宽高
        video_path = self.pattern.findall(str(self.lr_file))[0][8:]
        capture = cv.VideoCapture(video_path)
        frame_height = capture.get(cv.CAP_PROP_FRAME_HEIGHT)
        frame_width = capture.get(cv.CAP_PROP_FRAME_WIDTH)
        # 输入的图片集
        imgs_path = os.path.join(CWD, 'results/sr_imgs/')
        sr_video_path = os.path.join(CWD, 'results/')
        filelist = os.listdir(imgs_path)
        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        if FPS == '':
            fps = 25.0
        else:
            fps = float(FPS)
        video_writer = cv.VideoWriter(sr_video_path + 'sr.mp4', fourcc,
                                      fps, (int(frame_width * 4), int(frame_height * 4)))
        self.progressBar.setRange(0, len(filelist) - 1)
        self.progressBar.setValue(0)
        frame_idx = 0
        self.info_label.setText('imgs to video ...')
        for i in range(len(filelist)):
            img_path = os.path.join(imgs_path, str(i) + '.png')
            img = cv.imread(img_path)
            video_writer.write(img)
            self.progressBar.setValue(frame_idx)
            frame_idx += 1
        self.info_label.setText('imgs to video done!')
        video_writer.release()

        # 也许可以考虑合成视频后删除temp文件夹
        # shutil.rmtree(path)

        # 播放视频
        self.sr_file = QUrl.fromLocalFile(sr_video_path + 'sr.mp4')
        self.play_video('sr_video')

    def video2imgs(self, video_path):
        # 临时文件存在代码目录下的temp文件夹
        imgs_path = os.path.join(CWD, 'temp/')
        try:
            # 如果不存在temp文件则新建
            if not os.path.exists(imgs_path):
                os.makedirs(imgs_path)
                self.info_label.setText('create temp dir!')
            cap = cv.VideoCapture(video_path)  # 读取视频文件
            frame_idx = 0
            frames_num = int(cap.get(7))  # 获取视频总帧数
            self.progressBar.setRange(0, frames_num)
            self.info_label.setText('video to imgs ...')
            while True:
                ret, frame = cap.read()
                self.progressBar.setValue(frame_idx)
                if ret:
                    cv.imwrite(imgs_path + str(frame_idx) + '.png', frame)
                    frame_idx = frame_idx + 1
                else:
                    break
            self.info_label.setText('video to imgs done!')
            cap.release()
        except:
            self.info_label.setText('can not create temp dir!')
            return

    def lr_video_widget_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.play_or_pause('lr_video_player')

    def sr_video_widget_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.play_or_pause('sr_video_player')

    def play_or_pause(self, flag='lr_video_player'):
        if flag == 'lr_video_player':
            if self.lr_video_player.state() == 1:
                self.lr_video_player.pause()
            else:
                self.lr_video_player.play()
        elif flag == 'sr_video_player':
            if self.sr_video_player.state() == 1:
                self.sr_video_player.pause()
            else:
                self.sr_video_player.play()

    def play_video(self, flag='lr_video'):
        if flag == 'lr_video':
            self.lr_video_player.setMedia(QMediaContent(self.lr_file))
            self.lr_video_player.play()
        elif flag == 'sr_video':
            self.sr_video_player.setMedia(QMediaContent(self.sr_file))
            self.sr_video_player.play()

    # 选择文件的逻辑
    def select_file(self):
        try:
            self.lr_file = QFileDialog.getOpenFileUrl()[0]
            self.play_video(flag='lr_video')
        except:
            return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())

'''
播放其他格式的视频文件参考这篇的解决方法
https://blog.csdn.net/qq_42191914/article/details/104261414
'''

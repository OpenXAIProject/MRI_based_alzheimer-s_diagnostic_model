# -*- coding: utf-8 -*-

import sys

import PyQt5
import matplotlib.pyplot as plt
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Simlar_Explanations import Similar_Document
from qtpy import QtGui

from Rule_based_report import Report

sys.path.append("/usr/home/jungjunkim/pdfminer")

path = '/home/jungjunkim/PycharmProjects/xai_project_app/GUI/xai.ui'
Top = 5

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class GUI_main(QDialog):
    def __init__(self):
        QDialog.__init__(self,None)
        uic.loadUi(path,self)
        self.Similar_Explanations = Similar_Document(Top)
        self.image = QtGui.QImage()
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480

        # self.pushButton.clicked.connect(함수)

        ### Event Handler
        self.MR_load_btn.clicked.connect(self.show_prediction)

        self.topics =[]
        self.contents = []
        self.pairs = []


    def itemActivated_event(item):
            print(item.text())

    def Report(self):
        report_s = Report(brain_volume=140.0, brain_mean=120.0, hippocampus_volume=30.0, hippocampus_mean=50.0,prediction_rate=67,lang = 'eng')
        self.Report_text.setText(report_s.RuleBased())
        self.Report_text.setFont(QtGui.QFont('SansSerif', 13))

    def Explanation(self):
        topics =[]
        contents = []
        self.topics, self.contents = self.Similar_Explanations.Analyze()

        listview = self.Topiclist
        model = QStandardItemModel()

        for topic in self.topics:
            model.appendRow(QStandardItem(topic))

        listview.setModel(model)
        listview.setFont(QtGui.QFont('SansSerif', 13))
        listview.show()


        self.Content_editText.setText(self.contents[0])
        self.Content_editText.setFont(QtGui.QFont('SansSerif', 13))
        # self.Content_editText.setEnabled(False)


    def showContent(self,index):
        item = self.Topiclist.selectedIndexes()[0]
        topic = item.model().itemFromIndex(index).text()

        print(topic)

        idx = self.topics.index(topic)
        setence = self.contents[idx]

        self.Content_editText.setText(setence)
        self.Content_editText.setFont(QtGui.QFont('SansSerif', 13))

    def show_prediction(self,prob=0.55):

        type = ('NC', 'AD')
        y_pred = (prob, 1-prob)
        fig, ax = plt.subplots(1, 1, figsize=(7, 5))  # 1x1 figure matrix 생성, 가로(7인치)x세로(5인치) 크기지정
        ax.set_xlim([0.0, 0.99])
        ax.xaxis.set_tick_params(labelsize=10)
        ax.set_xlabel('Prediction Accuracy', fontsize=14)

        h = plt.barh(type, y_pred, color=['salmon', 'skyblue'])

        plt.legend(h, type)
        for p in ax.patches:
            percentage = '{:.2f}%'.format(100 * p.get_width() / 100)
            x = p.get_x() + p.get_width() + 0.02
            y = p.get_y() + p.get_height() / 2
            ax.annotate(percentage, (x, y), fontsize=15)

        plt.savefig('predict.png', format='png', dpi=300)


        self.fig = plt.Figure()
        ax = fig.add_subplot(111)
        ax.bar()


    def open_image_fd(self):

        dialog_text = "Open Image"
        default_folder = "/home/jungjunkim/xai_team_project/example_images/"

        fname = PyQt5.QtWidgets.QFileDialog.getOpenFileName(self, dialog_text,
                                                      default_folder)


        if fname:
            image = QtGui.QImage(fname[0])
        else:
            image = None


        self.image_label = QLabel(self)
        pixmap = QPixmap(image)
        self.image_label.setPixmap(pixmap)

        self.image_label.resize(200,180)
        self.image_label.move(220,15)

        self.image_label.show()

        # return image



app = QApplication(sys.argv)
gui = GUI_main()
gui.show()
app.exec_()




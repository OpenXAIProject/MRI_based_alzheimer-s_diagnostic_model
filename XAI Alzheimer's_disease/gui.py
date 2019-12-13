# -*- coding: utf-8 -*-

import PyQt5

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from Rule_based_report import Report
from Simlar_Explanations import Similar_Document
from qtpy import QtGui

import os
import sys
sys.path.append("/usr/home/jungjunkim/pdfminer")

path = './XAI_Project.ui'
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
        self.Load_MR_Image.clicked.connect(self.open_image_fd)

        self.Diagnosis_Btn.clicked.connect(self.Report)
        self.Diagnosis_Btn.clicked.connect(self.Explanation)
        self.Topiclist.doubleClicked.connect(self.showContent)
        # self.Topiclist.itemActivated.connect(self.itemActivated_event)


        #########
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




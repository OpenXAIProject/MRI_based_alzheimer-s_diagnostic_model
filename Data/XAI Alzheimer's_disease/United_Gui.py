# -*- coding: utf-8 -*-

import math
import re
import sys
import time

import PyQt5
import numpy as np
from GLWidget import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication
from Simlar_Explanations import Similar_Document
from Volume_controller import *
from qtpy import QtGui

# from PySide import QtGui, QtCore
from Rule_based_report import Report

path = './xai.ui'

Top = 4

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Thread(QDialog):
    def __init__(self):
        QDialog.__init__(self, None)
        uic.loadUi(path, self)

    def update_btn(self):
        pixmap = QPixmap('./red1.png')
        self.onoff.setPixmap(pixmap)


class GUI_main(QDialog):

    def __init__(self):
        QDialog.__init__(self, None)
        uic.loadUi(path,self)
        '''
        ## volume_controller _ 01 ##
        '''
        self.volume_cntr = Volume_controller(model_path='../Diagnosis_Network/model/Grad_cam_10')

        self.Similar_Explanations = Similar_Document(Top)
        self.image = QtGui.QImage()
        self.file_name = ""
        ### Event Handler
        self.Load_MR_Image.clicked.connect(self.open_image_fd)

        # Analyze_btn even

        #self.MR_Analyze_btn.clicked.connect(self.Visual_Explanation)
        #self.MR_Analyze_btn.clicked.connect(self.Report)
        #self.MR_Analyze_btn.clicked.connect(self.Explanation)
        #self.MR_Analyze_btn.clicked.connect(self.show_prediction)
        #self.MR_Analyze_btn.clicked.connect(self.show_details)

        self.MR_Analyze_btn.clicked.connect(self.Diagnosis_disease)

        # Slider event
        self.Axial_slider.sliderMoved['int'].connect(self.Axial_slider_change)
        self.Coronal_slider.sliderMoved['int'].connect(self.Coronal_slider_change)
        self.Sagittal_slider.sliderMoved['int'].connect(self.Sagittal_slider_change)

        self.Topiclist.doubleClicked.connect(self.showContent)



        # i think we need more implement here

        # openGL
        self.openGLWidget = GLWidget(self.groupBox_2)
        self.openGLWidget.setGeometry(QtCore.QRect(20, 50, 370, 370))
        self.openGLWidget.setObjectName("openGLWidget")

        # QtWidget label
        #self.opengl_title = QtWidgets.QLabel(self.groupBox_2)
        #self.opengl_title.setGeometry(QtCore.QRect(0, 30, 81, 21))
        self.opengl_title.raise_()

        self.paper_to_journal = {
            "High b-value diffusion imaging of dementia_3A application to vascular dementia and Alzheimer disease" : "neurological sciences (2007)",
            "Novel MRI techniques in the assessment of dementia" : "nuclear medicine and molecular imaging(2008)",
            "Oxidative modification and down-regulation of Pin1 in Alzheimer's disease hippocampus_3A a redox proteomics analysis" : "Neurobiology of aging (2006)",
            "Ways toward an early diagnosis in Alzheimer's disease_3A the Alzheimer's Disease Neuroimaging Initiative (ADNI)" : "Alzheimer's & Dementia (2005)",
            "Novel MRI techniques in the assessment of dementia":"neurological sciences (2007)",
            "Amyloid precursor protein processing and A42 deposition in atransgenic mouse model of Alzheimer disease":"National Academy of Sciences(1997)",
            "Oxidative modification and down - regulation of Pin1 in Alzheimer's disease hippocampus_3A a redox proteomics analysis" :"Neurobiology of aging(2006)",
            "New insights into brain BDNF function in normal aging and Alzheimer disease" : "Brain research reviews (2008)",
            "The developmental role of serotonin_3A news from mouse molecular genetics":"Nature Reviews Neuroscience (2003)",
            "Chronic divalproex sodium use and brain atrophy in Alzheimer disease":"Neurology (2011)",
            'Amyloid precursor protein processing and A42 deposition in a transgenic mouse model of Alzheimer disease':"National Academy of Sciences (1997)",
            'Oxidative modification and down-regulation of Pin1 in Alzheimer_s disease hippocampus_3A a redox proteomics analysis' : 'Neurobiology (2006)'
            }

        self.paper_to_author = {
            "High b-value diffusion imaging of dementia_3A application to vascular dementia and Alzheimer disease" : "Mayzel-Oreg, Orna, et al.",
            "Novel MRI techniques in the assessment of dementia" : "Teipel, Stefan J., et al.",
            "Oxidative modification and down-regulation of Pin1 in Alzheimer's disease hippocampus_3A a redox proteomics analysis" : "Sultana, Rukhsana, et al.",
            "Ways toward an early diagnosis in Alzheimer's disease_3A the Alzheimer's Disease Neuroimaging Initiative (ADNI)" : "Mueller, Susanne G., et al.",
            "Novel MRI techniques in the assessment of dementia":"Teipel, Stefan J., et al.",
            "Amyloid precursor protein processing and A42 deposition in atransgenic mouse model of Alzheimer disease":"Johnson - Wood, K., et al.",
            "Oxidative modification and down - regulation of Pin1 in Alzheimer's disease hippocampus_3A a redox proteomics analysis" :"Sultana, Rukhsana, et al.",
            "New insights into brain BDNF function in normal aging and Alzheimer disease" : "Tapia-Arancibia, Lucia, et al.",
            "The developmental role of serotonin_3A news from mouse molecular genetics":"Gaspar, Patricia, Olivier Cases, and Luc Maroteaux.",
            "Chronic divalproex sodium use and brain atrophy in Alzheimer disease":"Fleisher, A.S., et al.",
            'Amyloid precursor protein processing and A42 deposition in a transgenic mouse model of Alzheimer disease':"Johnson-Wood, K., et al.",
            'Oxidative modification and down-regulation of Pin1 in Alzheimer_s disease hippocampus_3A a redox proteomics analysis': 'Sultana, Rukhsana, et al.'
            }


        '''
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setItalic(True)
        self.opengl_title.setFont(font)
        #self.opengl_title.setAutoFillBackground(False)
        self.opengl_title.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "color: rgb(255, 255, 255);")

        #self.opengl_title.
        '''

        self.flag=0
        if self.flag == 1:
            print("test")

        self.topics =[]
        self.contents = []
        self.pairs = []

        self.ad_hippocampus = 0
        self.nc_hippocampus = 0
        self.ad_ventricle = 0
        self.nc_ventricle = 0
        self.ad_amygdala = 0
        self.nc_amygdala = 0
        self.ad_thalamus = 0
        self.nc_thalamus = 0
        self.ad_putamen = 0
        self.nc_putamen = 0
        self.ad_wholebrain = 0
        self.nc_wholebrain = 0

    def Refresh(self):
        cur_value = self.Axial_slider.value()
        axial_image = self.volume_cntr.get_axial_image(cur_value)
        # h, w, c = np.shape(axial_image)
        self.openGLWidget.move_axial(volume_info=axial_image, index=cur_value)

        cur_value = self.Coronal_slider.value()
        coronal_image = self.volume_cntr.get_coronal_image(cur_value)
        # h, w, c = np.shape(coronal_image)
        self.openGLWidget.move_coronal(volume_info=coronal_image, index=cur_value)

        cur_value = self.Sagittal_slider.value()
        sagittal_image = self.volume_cntr.get_sagittal_image(cur_value)
        # h, w, c = np.shape(coronal_image)
        self.openGLWidget.move_sagittal(volume_info=sagittal_image, index=cur_value)

    def Axial_slider_change(self):
        cur_value = self.Axial_slider.value()
        axial_size = self.volume_cntr.get_axial_size()
        #axial_index = self.volume_cntr.get_axial_index()
        axial_indexer_text = '{0:03}:{1:03}'.format(cur_value, axial_size)
        self.Axial_indexer.setText(axial_indexer_text)
        axial_image = self.volume_cntr.get_axial_image(cur_value)
        h, w, c = np.shape(axial_image)
        qimage = QImage(axial_image, w, h, 3 * w, QImage.Format_RGB888)
        self.Axial_viewer.setPixmap(QPixmap(qimage))
        self.openGLWidget.move_axial(volume_info=axial_image, index=cur_value)

    def Coronal_slider_change(self):
        cur_value = self.Coronal_slider.value()
        coronal_size = self.volume_cntr.get_coronal_size()
        #coronal_index = self.volume_cntr.get_coronal_index()
        coronal_indexer_text = '{0:03}:{1:03}'.format(cur_value, coronal_size)
        self.Coronal_indexer.setText(coronal_indexer_text)
        coronal_image = self.volume_cntr.get_coronal_image(abs(coronal_size - cur_value - 1))
        h, w, c = np.shape(coronal_image)
        qimage = QImage(coronal_image, w, h, 3 * w, QImage.Format_RGB888)
        self.Coronal_viewer.setPixmap(QPixmap(qimage))
        self.openGLWidget.move_coronal(volume_info=coronal_image,index=abs(coronal_size - cur_value - 1))


    def Sagittal_slider_change(self):
        cur_value = self.Sagittal_slider.value()
        sagittal_size = self.volume_cntr.get_sagittal_size()
        #sagittal_index = self.volume_cntr.get_axial_index()
        sagittal_indexer_text = '{0:03}:{1:03}'.format(cur_value, sagittal_size)
        self.Sagittal_indexer.setText(sagittal_indexer_text)
        sagittal_image = self.volume_cntr.get_sagittal_image(cur_value)
        h, w, c = np.shape(sagittal_image)
        sagittal_image_reshape = np.reshape(sagittal_image, (w, h, c))
        qimage = QImage(sagittal_image_reshape, w, h, 3 * w, QImage.Format_RGB888)
        self.Sagittal_viewer.setPixmap(QPixmap(qimage))
        self.openGLWidget.move_sagittal(volume_info=sagittal_image, index=cur_value)

    def on_red(self):
        pixmap = QPixmap('./red1.png')
        self.onoff.setPixmap(pixmap)

    def itemActivated_event(item):
            print(item.text())

    # mri 영상 분석하기 click event
    ###################################################################################################
    #                                                                                                 #
    #                                            Diagnosis                                            #
    #                                                                                                 #
    ###################################################################################################
    def Set_contextBox(self, editText, content):
        html_head = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n" \
                    "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n" \
                    "p, li { white-space: pre-wrap; }\n" \
                    "</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n" \
                    "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">"

        html_tail = "</body></html>"
        sentence = html_head
        sentence += content
        sentence += html_tail

        _translate = QtCore.QCoreApplication.translate

        editText.setHtml(_translate("MainWindow", sentence))
        editText.setFont(QtGui.QFont('SansSerif', 13))
        editText.setAlignment(Qt.AlignCenter)  # 가운데 정렬
        editText.setAlignment(Qt.AlignVCenter)  # 가운데 정렬

    def Diagnosis_disease(self):

        if self.volume_cntr.Isvolume():
            QApplication.setOverrideCursor(Qt.WaitCursor)
            pixmap = QPixmap('./red1.png')
            self.onoff.setPixmap(pixmap)

            # i don't know what is the menaing of this line
            # check later 2019/8/26 [mon]
            #sec = 3.0
            #time.sleep(sec)

            # Diagnosis
            '''
            ## volume_controller _ 02 ##
            '''
            Dtected_damaged_area = self.volume_cntr.get_diagnosis(Threshold=0.9)
            print(Dtected_damaged_area)

            # Refresh_opengl
            self.Refresh()

            # View heatmap image
            axial_image = self.volume_cntr.get_axial_image(self.volume_cntr.axial_index)
            h, w, c = np.shape(axial_image)
            qimage = QImage(axial_image, w, h, 3 * w, QImage.Format_RGB888)
            self.Axial_viewer.setPixmap(QPixmap(qimage))

            coronal_image = self.volume_cntr.get_coronal_image(self.volume_cntr.coronal_index)
            h, w, c = np.shape(coronal_image)
            qimage = QImage(coronal_image, w, h, 3 * w, QImage.Format_RGB888)
            self.Coronal_viewer.setPixmap(QPixmap(qimage))

            sagittal_image = self.volume_cntr.get_sagittal_image(self.volume_cntr.sagittal_index)
            h, w, c = np.shape(sagittal_image)
            sagittal_image = np.reshape(sagittal_image, (w, h, c))
            qimage = QImage(sagittal_image, w, h, 3 * w, QImage.Format_RGB888)
            self.Sagittal_viewer.setPixmap(QPixmap(qimage))


            #self.openGLWidget.load()

            # Show diagnosis
            # Prediction
            predicted_value = self.volume_cntr.get_prediction()
            print(predicted_value)
            val = math.trunc(predicted_value[0][0] * 100)

            val2 = 100 - val #predicted_value[0][1] * 100
            print(val, val2)

    #------------------------------------------------------------------------------------------------------------------#
            ## Show Reports
            ## Patient's
            volume_map = self.volume_cntr.get_volume_map()

            hippocampus_vol = volume_map[27][2] + volume_map[13][2]
            ventricle_volume = volume_map[10][2] + volume_map[11][2] + volume_map[20][2] + volume_map[3][2]
            amygdal_volume = volume_map[14][2] + volume_map[28][2]
            thalamus_volume = volume_map[6][2] + volume_map[23][2]
            putamen_volume = volume_map[8][2] + volume_map[25][2]

            sum = 0.0
            for dat in volume_map:
                sum += dat[2]
            whole_brain = sum - volume_map[0][2]
    #------------------------------------------------------------------------------------------------------------------#
            result_ad_nc = 'AD' if val > val2 else 'NC'

            self.flag = 1
            # User's volume
            report_s = Report(self.volume_cntr.get_volume_map(),
                              detected_damaged_area=Dtected_damaged_area,
                              result=result_ad_nc,
                              prob =[val, val2])

            text = report_s.RuleBased()
            _translate = QtCore.QCoreApplication.translate
            self.Report_text.setHtml(_translate("MainWindow", text))
            self.Report_text.setFont(QtGui.QFont('SansSerif', 15))

    # ----------------------------------------- List Box appending  ----------------------------------------- #

            self.topics, self.contents = self.Similar_Explanations.Analyze(self.file_name)

            listview = self.Topiclist
            model = QStandardItemModel()

            for idx, topic in enumerate(self.topics):
                temp = ""

                cnt = 0
                for w in topic:
                    if cnt == 31:
                        temp += '\n    '
                        temp += w
                        cnt = 0
                    else:
                        temp += w
                        cnt += 1

                #temp = QTextEdit(topic)
                #model.appendRow(temp)

                model.appendRow(QStandardItem(str(idx + 1) + " : " + temp + '\n'))
                #model.appendRow(QStandardItem(''))

            listview.setModel(model)
            listview.setFont(QtGui.QFont('SansSerif', 11))
            listview.show()
    # ------------------------------------------------------------------------------------------------------- #

            # html_head = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n" \
            #             "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n" \
            #             "p, li { white-space: pre-wrap; }\n" \
            #             "</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n" \
            #             "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">" \
            #
            # html_tail = "</body></html>"
            #
            # sentence = html_head
            # sentence += "<b>제목</b><br>"
            # sentence += self.topics[0].replace('\n', '') + "<br>"
            # sentence += "<b>내용</b><br>"
            # sentence += self.contents[0].replace('\n', '')
            # sentence += "<br>"
            # sentence += "<b>저자</b><br>"
            # sentence += self.paper_to_author[self.topics[0].replace('\n', '')] + "<br>"  # "Mayzel-Oreg, Orna, et al.<br>"
            # sentence += "<b>출판지 (년도)</b><br>"
            # sentence += self.paper_to_journal[self.topics[0].replace('\n', '')]  # "neurological sciences (2007)"
            # sentence += html_tail
            #
            #
            # _translate = QtCore.QCoreApplication.translate
            #
            # self.Content_editText.setHtml(_translate("MainWindow", sentence))
            # self.Content_editText.setFont(QtGui.QFont('SansSerif', 13))
            # self.Content_editText.setAlignment(Qt.AlignCenter)  # 가운데 정렬
            # self.Content_editText.setAlignment(Qt.AlignVCenter)  # 가운데 정렬
            #self.Set_contextBox(self.Qtext_title,self.topics[0].replace('\n', ''))
            self.Set_contextBox(self.Qtext_author, self.paper_to_author[self.topics[0].replace('\n', '')])
            self.Set_contextBox(self.Qtext_publish, self.paper_to_journal[self.topics[0].replace('\n', '')])
            self.Set_contextBox(self.Qtext_content, self.contents[0].replace('\n', ''))


            #self.Content_editText.setText(self.contents[0])
            #self.Content_editText.setFont(QtGui.QFont('SansSerif', 17))
    # ------------------------------------------------------------------------------------------------------ #


            ## Show detail

            # self.get_details(10, 20, 30, 20, 40, 50, 40, 35, 20, 25, 18, 60)
            self.get_details(6016, 7422, 62133, 41202, 2758, 2224, 13265, 12890, 8449, 7878, 1005607, 1049783)
            # self.ad_details.setFont(QtGui.QFont('SansSerif', 10.5))
            # self.nc_details.setFont(QtGui.QFont('SansSerif', 10.5))
            # self.nc_details.setAlignment(Qt.AlignCenter)  # 가운데 정렬
            # self.ad_details.setAlignment(Qt.AlignCenter)  # 가운데 정렬


    #-------------------------------------------------------------#
            # Normal person set Text
            self.hippo_normal.setText(format(7422, ','))
            self.vent_normal.setText(format(41202, ','))
            self.amyg_normal.setText(format(2224, ','))
            self.thala_normal.setText(format(12890, ','))
            self.puta_normal.setText(format(7878, ','))
            self.wb_normal.setText(format(1049783, ','))

            # Patient person set Text
            self.hippo_patient.setText(format(hippocampus_vol, ','))
            self.vent_patient.setText(format(ventricle_volume, ','))
            self.amyg_patient.setText(format(amygdal_volume, ','))
            self.thala_patient.setText(format(thalamus_volume, ','))
            self.puta_patient.setText(format(putamen_volume, ','))
            self.wb_patient.setText(format(int(whole_brain), ','))
    #-------------------------------------------------------------#
            #
            #
            # self.hippo_ad.setText(str(self.ad_hippocampus))
            # self.hippo_nc.setText(str(self.nc_hippocampus))
            #
            # self.vent_ad.setText(str(self.ad_ventricle))
            # self.vent_nc.setText(str(self.nc_ventricle))
            #
            # self.amyg_ad.setText(str(self.ad_amygdala))
            # self.amyg_nc.setText(str(self.nc_amygdala))
            #
            # self.thala_ad.setText(str(self.ad_thalamus))
            # self.thala_nc.setText(str(self.nc_thalamus))
            #
            # self.puta_ad.setText(str(self.ad_putamen))
            # self.puta_nc.setText(str(self.nc_putamen))
            #
            # self.wb_ad.setText(str(self.ad_wholebrain))
            # self.wb_nc.setText(str(self.nc_wholebrain))



            # self.ad_details.setAlignment(Qt.AlignCenter)  # 가운데 정렬
            # self.nc_details.setAlignment(Qt.AlignCenter)  # 가운데 정렬
            self.adlabel.setText(str(val) + "%")
            self.nclabel.setText(str(val2) + "%")
            self.adbar.setValue(val)
            self.ncbar.setValue(val2)
            QApplication.restoreOverrideCursor()
            # pixmap = QPixmap('../GUI/null1.png')
            # self.onoff.setPixmap(pixmap)



    def Visual_Explanation(self):
        if self.volume_cntr.Isvolume():
            # Heatmap + damaged area
            volume_map = self.volume_cntr.get_diagnosis()

            axial_image = self.volume_cntr.get_axial_image(self.volume_cntr.axial_index)
            h, w, c = np.shape(axial_image)
            qimage = QImage(axial_image, w, h, 3 * w, QImage.Format_RGB888)
            self.Axial_viewer.setPixmap(QPixmap(qimage))

            coronal_image = self.volume_cntr.get_coronal_image(self.volume_cntr.coronal_index)
            h, w, c = np.shape(coronal_image)
            qimage = QImage(coronal_image, w, h, 3 * w, QImage.Format_RGB888)
            self.Coronal_viewer.setPixmap(QPixmap(qimage))

            sagittal_image = self.volume_cntr.get_sagittal_image(self.volume_cntr.sagittal_index)
            h, w, c = np.shape(sagittal_image)
            sagittal_image = np.reshape(sagittal_image, (w, h, c))
            qimage = QImage(sagittal_image, w, h, 3 * w, QImage.Format_RGB888)
            self.Sagittal_viewer.setPixmap(QPixmap(qimage))

    def show_prediction(self):
        val = 62.3
        val2 = 100.0-val
        print(val,val2)
        self.adlabel.setText(str(val) + "%")
        self.nclabel.setText(str(val2) + "%")
        self.adbar.setValue(val)
        self.ncbar.setValue(val2)

    def Report(self):
        self.flag = 1
        report_s = Report(100.0,50.0,10.0,25.0,
                          50.0,60.0,70.0,80.0,
                          90.0,10.0,20.0,31.0,result = 'NC', lang = 'kor')
        self.Report_text.setText(report_s.RuleBased())
        self.Report_text.setFont(QtGui.QFont('SansSerif', 11))

    def Explanation(self):

        self.topics, self.contents = self.Similar_Explanations.Analyze(self.file_name)

        listview = self.Topiclist
        model = QStandardItemModel()

        for topic in self.topics:
            model.appendRow(QStandardItem(topic))

        listview.setModel(model)
        listview.setFont(QtGui.QFont('SansSerif', 13.5))
        listview.show()

        self.Content_editText.setText(self.contents[0])
        # self.Content_editText.setFont(QtGui.QFont('SansSerif', 10))
        # self.Content_editText.setEnabled(False)


# ---------------------------------------------  Contents box double click  --------------------------------------------- #

    def showContent(self,index):

        item = self.Topiclist.selectedIndexes()[0]
        get_item = item.model().itemFromIndex(index).text()
        int_index = get_item.split(' ')[0]

        topic = self.topics[int(int_index)-1]
        contents = self.contents[int(int_index)-1]

        shortword = re.compile(r'\W*\b\w{1,2}\b')
        shortword.sub('', topic)

        print(topic)

        #idx = self.topics.index(topic)
        #print(idx)

        # html_head = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"\
        # "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"\
        # "p, li { white-space: pre-wrap; }\n"\
        # "</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"\
        # "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">" \
        #
        # html_tail = "</body></html>"
        #
        # sentence = html_head
        # sentence += "<b>제목</b><br>"
        # #sentence += self.topics[idx].replace('\n','') + "<br><br>"
        # sentence += topic + "<br>"
        # sentence += "<b>내용</b><br>"
        # print(sentence)
        # #sentence += self.contents[index].replace('\n','')
        # sentence += contents
        # sentence += "<br>"
        # sentence += "<b>저자</b><br>"
        # sentence += self.paper_to_author[topic] + "<br>"#"Mayzel-Oreg, Orna, et al.<br>"
        # sentence += "<b>출판지 (년도)</b><br>"
        # sentence += self.paper_to_journal[topic]#"neurological sciences (2007)"
        # sentence += html_tail
        #
        # _translate = QtCore.QCoreApplication.translate
        #
        # self.Content_editText.setHtml(_translate("MainWindow", sentence))
        # self.Content_editText.setFont(QtGui.QFont('SansSerif', 13))
        # self.Content_editText.setAlignment(Qt.AlignCenter) # 가운데 정렬
        # self.Content_editText.setAlignment(Qt.AlignVCenter)  # 가운데 정렬

        idx = self.topics.index(topic)
        #self.Set_contextBox(self.Qtext_title, self.topics[idx].replace('\n', ''))
        self.Set_contextBox(self.Qtext_author, self.paper_to_author[self.topics[idx].replace('\n', '')])
        self.Set_contextBox(self.Qtext_publish, self.paper_to_journal[self.topics[idx].replace('\n', '')])
        self.Set_contextBox(self.Qtext_content, self.contents[idx].replace('\n', ''))

    def show_details(self):

        self.get_details(6016,7422,62133,41202,2758,2224,13265,12890,8449,7878,1005607,1049783)
        self.ad_details.setFont(QtGui.QFont('SansSerif', 11))
        self.nc_details.setFont(QtGui.QFont('SansSerif', 11))

        self.ad_details.setText(str(self.ad_hippocampus)+'\n   '+str(self.ad_ventricle)+'\n   '+str(self.ad_amygdala)+'\n   '+str(self.ad_thalamus)+'\n   '+str(self.ad_putamen)+'\n   '+str(self.ad_wholebrain))
        self.nc_details.setText(str(self.nc_hippocampus) + '\n   ' + str(self.nc_ventricle) + '\n   ' + str(self.nc_amygdala) + '\n   ' + str(self.nc_thalamus) + '\n   ' + str(self.nc_putamen) + '\n   ' + str(self.nc_wholebrain))

        self.ad_details.setAlignment(Qt.AlignCenter)  # 가운데 정렬
        self.nc_details.setAlignment(Qt.AlignCenter)  # 가운데 정렬


    # what is this?
    def get_details(self, ad_hippo,nc_hippo,ad_vent,nc_vent,ad_amyg,nc_amyg,ad_thala,nc_thala,ad_puta,nc_puta,ad_wb,nc_wb):

        self.ad_hippocampus = ad_hippo
        self.nc_hippocampus = nc_hippo
        self.ad_ventricle = ad_vent
        self.nc_ventricle = nc_vent
        self.ad_amygdala = ad_amyg
        self.nc_amygdala = nc_amyg
        self.ad_thalamus = ad_thala
        self.nc_thalamus = nc_thala
        self.ad_putamen = ad_puta
        self.nc_putamen = nc_puta
        self.ad_wholebrain = ad_wb
        self.nc_wholebrain = nc_wb


    def open_image_fd(self):

            dialog_text = "Open Image"
            default_folder = "../Data/brainmask/"
            file_info = PyQt5.QtWidgets.QFileDialog.getOpenFileName(self, dialog_text,
                                                          default_folder)
            patient_list = [["ADNI_109_S_1157_AD.mgz", "1157", "H.W Kim", "79", "2011.04.07"],
                            ["ADNI_099_S_1144_AD.mgz", "1144", "H.S Kim", "81", "2012.05.28"],
                            ["ADNI_099_S_0372_AD.mgz", "0372", "S.H Kang", "82", "2011.03.28"],
                            ["ADNI_114_S_0374_AD.mgz", "0374", "W.S Lee", "81", "2012.05.28"],
                            ["ADNI_099_S_0470_AD.mgz", "0470", "Y.H Lee", "69", "2011.03.18"],
                            ["ADNI_068_S_0127_CN.mgz", "0127", "W.S Chang", "80", "2012.02.18"],
                            ["ADNI_094_S_0711_CN.mgz", "0711", "H.G Kim", "77", "2012.02.13"],
                            ["ADNI_067_S_0257_CN.mgz", "0257", "W.H Young", "71", "2012.02.17"],
                            ["ADNI_073_S_0386_CN.mgz", "0386", "W.H Young", "69", "2012.03.11"],
                            ["ADNI_073_S_0311_CN.mgz", "0311", "S.F Kim", "81", "2012.05.12"],
                            ["ADNI_032_S_0400_AD.mgz", "0400", "F.V Young", "82", "2011.06.14"],
                            ["ADNI_002_S_0938_AD.mgz", "0938", "E.B Lee", "88", "2013.01.15"],
                            ["ADNI_137_S_0796_AD.mgz", "0796", "A.E Young", "90", "2011.03.12"],
                            ["ADNI_021_S_1109_AD.mgz", "1109", "B.A Kim", "91", "2012.07.14"],
                            ["ADNI_036_S_0577_AD.mgz", "0577", "J.G Sang", "70", "2011.08.12"],
                            ["ADNI_021_S_0159_CN.mgz", "0159", "J.H Lee", "80", "2013.09.06"],
                            ["ADNI_052_S_1250_CN.mgz", "1250", "K.E Kim", "81", "2012.01.13"],
                            ["ADNI_005_S_0553_CN.mgz", "0553", "K.Q Bob", "83", "2014.05.14"],
                            ["ADNI_033_S_0923_CN.mgz", "0923", "Q.V Young", "84", "2011.07.19"],
                            ["ADNI_033_S_0516_CN.mgz", "0516", "A.M Young", "91", "2011.08.12"],
                            ]
            QApplication.setOverrideCursor(Qt.WaitCursor)
            file_name, _ = file_info
            file_name_t = file_name.split('/')[-1]
            self.file_name = file_name_t

            for patient in patient_list:
                test = patient[0]
                if patient[0] == file_name_t:
                    self.info_id.setText(patient[1])
                    self.info_name.setText(patient[2])
                    self.info_age.setText(patient[3])
                    self.info_date.setText(patient[4])


            # Load axial image

            self.volume_cntr.Load_volume(file_name)

            self.openGLWidget.Volume_change(self.volume_cntr.get_axis_volumes())

            # Load Image
            axial_size = self.volume_cntr.get_axial_size()
            axial_index = self.volume_cntr.get_axial_index()
            axial_indexer_text = '{0:03}:{1:03}'.format(axial_index, axial_size)
            self.Axial_indexer.setText(axial_indexer_text)
            self.Axial_slider.setMinimum(0)
            self.Axial_slider.setMaximum(axial_size-1)
            self.Axial_slider.setValue(axial_index)
            axial_image = self.volume_cntr.get_axial_image(axial_index)
            h,w,c = np.shape(axial_image)
            qimage = QImage(axial_image, w, h, 3*w, QImage.Format_RGB888)
            self.Axial_viewer.setPixmap(QPixmap(qimage))

            # Load coronal_image

            coronal_size = self.volume_cntr.get_coronal_size()
            coronal_index = self.volume_cntr.get_coronal_index()
            coronal_indexer_text ='{0:03}:{1:03}'.format(coronal_index, coronal_size)
            self.Coronal_indexer.setText(coronal_indexer_text)
            self.Coronal_slider.setMinimum(0)
            self.Coronal_slider.setMaximum(coronal_size-1)
            self.Coronal_slider.setValue(coronal_index)
            coronal_image = self.volume_cntr.get_coronal_image(coronal_index)
            h,w,c = np.shape(coronal_image)
            qimage = QImage(coronal_image, w, h, 3*w, QImage.Format_RGB888)
            self.Coronal_viewer.setPixmap(QPixmap(qimage))


            # Load sagittal_image

            sagittal_size = self.volume_cntr.get_sagittal_size()
            sagittal_index = self.volume_cntr.get_sagittal_index()
            sagittal_indexer_text = '{0:03}:{1:03}'.format(sagittal_index, sagittal_size)
            self.Sagittal_indexer.setText(sagittal_indexer_text)
            self.Sagittal_slider.setMinimum(0)
            self.Sagittal_slider.setMaximum(sagittal_size-1)
            self.Sagittal_slider.setValue(sagittal_index)
            sagittal_image = self.volume_cntr.get_sagittal_image(sagittal_index)
            h,w,c = np.shape(sagittal_image)
            sagittal_image = np.reshape(sagittal_image, (w, h, c))
            qimage = QImage(sagittal_image, w, h, 3*w, QImage.Format_RGB888)
            #h, w, c = np.shape(coronal_image)
            #qimage = QImage(coronal_image, w, h, 3 * w, QImage.Format_RGB888)
            self.Sagittal_viewer.setPixmap(QPixmap(qimage))

            '''
            self.image_label = QLabel(self)
            pixmap = QPixmap(image)
            self.image_label.setPixmap(pixmap)
            self.image_label.resize(200,180)

            self.image_label.show()
            '''

            QApplication.restoreOverrideCursor()



if __name__ == '__main__':
    #libpaths = QtWidgets.QApplication.libraryPaths()
    #libpaths.append("./platforms/")
    #QtWidgets.QApplication.setLibraryPaths(libpaths)
    # modify environment variables to find qgis and qt plugins during qgis.core import
    #os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'~qgis directory\apps\Qt5\plugins'
    #os.environ['PATH'] += r';~qgis directory\apps\qgis\bin;~qgis directory\apps\Qt5\bin'

    app = QApplication(sys.argv)
    gui = GUI_main()
    gui.show()
    app.exec_()





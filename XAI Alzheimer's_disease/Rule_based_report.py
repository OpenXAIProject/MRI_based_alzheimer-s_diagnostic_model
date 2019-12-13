# -*- coding: utf-8 -*-

class Report():
    def __init__(self, volume_map, detected_damaged_area, result, prob):
        self.prob = prob
        self.result = result
        self.volume_map = volume_map

        self.label_to_vol_dict = {}
        for i, dat in enumerate(volume_map):
            index, name, vol = dat
            self.label_to_vol_dict[int(index)] = (i, vol)

        sum = 0.0
        for dat in volume_map:
            sum += dat[2]
        whole_brain = sum - volume_map[0][2]

        self.detected_damaged_area = detected_damaged_area

        self.hippocampus_volume = volume_map[27][2] + volume_map[13][2]
        self.ventricle_volume = volume_map[10][2] + volume_map[11][2] + volume_map[20][2] + volume_map[3][2]
        self.amygdala_volume = volume_map[14][2] + volume_map[28][2]
        self.thalamus_volume = volume_map[6][2] + volume_map[23][2]
        self.putamen_volume = volume_map[8][2] + volume_map[25][2]
        self.brain_volume = whole_brain

        if self.result == 'NC': # AD
            self.hippocampus_mean = 6016
            self.ventricle_mean = 62133
            self.amygdala_mean = 2758
            self.thalamus_mean = 13265
            self.putamen_mean = 8449
            self.brain_mean = 1005607
        else:
            self.hippocampus_mean = 7422
            self.ventricle_mean = 41202
            self.amygdala_mean = 2224
            self.thalamus_mean = 12890
            self.putamen_mean = 7878
            self.brain_mean = 1049783

    def Add_color(self, color="#ff0000;", text=" "):
        return "<span style =\" color:" + color + "\">" + text + "</span>"

    def RuleBased(self):

        html_head = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"\
        "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"\
        "p, li { white-space: pre-wrap; }\n"\
        "</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"\
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">" \

        html_tail = "</body></html>"

        '''
            이 환자의 MRI 분석결과, 각 영역별 뇌의 부피는 아래와 같다.
        '''

        #s = "이 환자는 " + self.Add_color(text=str(self.prob[0]) + '%') + "의 확률로" + self.Add_color(text=" AD") +"로 판단됩니다.<br>" \
        #    if self.result == 'AD' else "이 환자는 " + self.Add_color(text=str(self.prob[1]) + '%') + "의 확률로" + self.Add_color(text = " NC") +"로 판단됩니다.<br>"
        #print(s)

        s0 = "해당 환자는 <b>" + self.Add_color(text=str(self.prob[0]) + '%') + "</b>의 확률로 <b>" + self.Add_color(text='알츠하이머 ') + "</b>로 판단되며 그 근거가 되는 영역은 아래와 같다.<br>" \
            if self.result == 'AD' \
            else "해당 환자는 <b>" + self.Add_color(text=str(self.prob[1]) + '%') + "</b>의 확률로 <b>" + self.Add_color(text='정상인 ') + "</b>으로 판단되며 그 근거가 되는 영역은 아래와 같다.<br>"

        for dat in self.detected_damaged_area:
            # Zero equal label_index
            label_index = dat[0]
            region_name = dat[1]
            if label_index != 0:
                index, vol = self.label_to_vol_dict[label_index]
                volume_rate = vol / self.volume_map[index][2]

                if volume_rate > 0.8:
                    s0 = s0 + region_name + ", "
        s0 = s0[:-2]
        s0 = s0 + '<br>'

        '''
        s1 = "이 환자의 MRI 분석결과, 각 영역별 뇌의 부피는 아래와 같다.<br>"

        s2 = 'Hippocampus: ' + str(self.hippocampus_volume) + ', '
        s3 = 'Ventricle: ' + str(self.ventricle_volume) + ', '
        s4 = 'Amygdala: ' + str(self.amygdala_volume) + '<br>'
        s5 = 'Thalamus: ' + str(self.thalamus_volume) + ', '
        s6 = 'Putamen: ' + str(self.putamen_volume) + ', '
        s7 = 'Whole brain: ' + str(self.brain_volume) + '<br>'
        '''

        ment = '정상군과 비교해, 이 환자는 다음과 같은 차이를 보인다.<br>' if self.result == 'AD' else '비정상군과 비교해 이 환자는 다음과 같은 차이를 보인다.<br>'

        hippo = '증가' if self.hippocampus_volume - self.hippocampus_mean > 0 else '감소'
        vent =  '증가' if self.ventricle_volume - self.ventricle_mean > 0 else '감소'
        amy = '증가' if self.amygdala_volume - self.amygdala_mean > 0 else '감소'
        thala = '증가' if self.thalamus_volume - self.thalamus_mean > 0 else '감소'
        puta = '증가' if self.putamen_volume - self.putamen_mean > 0 else '감소'
        wholeb = '증가' if self.brain_volume - self.brain_mean > 0 else '감소'

        s8 = 'Hippocampus ' + "{:.0f}".format((abs(self.hippocampus_mean - self.hippocampus_volume) / self.hippocampus_mean) * 100) + '% ' + hippo + ' '
        # s8 = 'Hippocampus ' + str((abs(self.hippocampus_mean-self.hippocampus_volume) / self.hippocampus_mean ) * 100) + '% ' + hippo + ' '
        # s9 = 'Ventricle ' + str((abs(self.ventricle_mean - self.ventricle_volume) / self.ventricle_mean) * 100) + '% ' + vent + ' '
        s9 = 'Ventricle ' + "{:.0f}".format((abs(self.ventricle_mean - self.ventricle_volume) / self.ventricle_mean) * 100 )+ '% ' + vent + ' '
        s10 = 'Amygdala ' + "{:.0f}".format((abs(self.amygdala_mean - self.amygdala_volume) / self.amygdala_mean) * 100) + '% ' + amy + '<br>'
        s11 = 'Thalamus ' + "{:.0f}".format((abs(self.thalamus_mean - self.thalamus_volume) / self.thalamus_mean) * 100) + '% ' + thala + ' '
        s12 = 'Putamen ' + "{:.0f}".format((abs(self.putamen_mean - self.putamen_volume) / self.putamen_mean) * 100) + '% ' + puta + ' '
        s13 = 'Whole brain ' + "{:.0f}".format((abs(self.brain_mean - self.brain_volume) / self.brain_mean) * 100) + '% ' + wholeb + ' '

        #report = html_head + s + s0 + s1 + s2 + s3 + s4 + s5 + s6 + s7 + ment + s8 + s9 + s10 + s11 + s12 + s13 + html_tail
        report = html_head + s0 + ment + s8 + s9 + s10 + s11 + s12 + s13 + html_tail

        _hippo = 'increase' if self.hippocampus_volume - self.hippocampus_mean > 0 else 'decrease'
        _vent = 'increase' if self.ventricle_volume - self.ventricle_mean > 0 else 'decrease'
        _amy = 'increase' if self.amygdala_volume - self.amygdala_mean > 0 else 'decrease'
        _thala = 'increase' if self.thalamus_volume - self.thalamus_mean > 0 else 'decrease'
        _puta = 'increase' if self.putamen_volume - self.putamen_mean > 0 else 'decrease'
        _wholeb = 'increase' if self.brain_volume - self.brain_mean > 0 else 'decrease'

        e1 = "As a result of MRI analysis of this patient, the brain volume of each region is as follows."

        e2 = 'Hippocampus: ' + str(self.hippocampus_volume) + ', '
        e3 = 'Ventricle: ' + str(self.ventricle_volume) + ', '
        e4 = 'Amygdala: ' + str(self.amygdala_volume) + ', '
        e5 = 'Thalamus: ' + str(self.thalamus_volume) + ', '
        e6 = 'Putamen: ' + str(self.putamen_volume) + ', '
        e7 = 'Whole brain: ' + str(self.brain_volume) + '. '

        ment = 'as compared to NC, This patient has the following differences' if self.result == 'AD' else 'as compared to AD, This patient has the following differences'

        e8 = 'Ventricle ' + "{:.0f}".format((abs(self.ventricle_mean - self.ventricle_volume) / self.ventricle_mean) * 100) + '% ' + _vent + ' '
        e9 = 'Amygdala ' + "{:.0f}".format((abs(self.amygdala_mean - self.amygdala_volume) / self.amygdala_mean) * 100) + '% ' + _amy + ' '
        e10 = 'Thalamus ' + "{:.0f}".format((abs(self.thalamus_mean - self.thalamus_volume) / self.thalamus_mean) * 100) + '% ' + _thala + ' '
        e11 = 'Putamen ' + "{:.0f}".format((abs(self.putamen_mean - self.putamen_volume) / self.putamen_mean) * 100) + '% ' + _puta + ' '
        e12 = 'Whole brain ' + "{:.0f}".format((abs(self.brain_mean - self.brain_volume) / self.brain_mean) * 100) + '% ' + _wholeb + ' '

        eng_report = e1 + e2 + e3 + e4 + e5 + e6 + e7 + ment + e8 + e9 + e10 + e11 + e12
        Save_path = open("./" + 'Report_english' + ".txt", "w")
        Save_path.write(eng_report)
        print("report saved")




        return report



# -*- coding: utf-8 -*-
#from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktTrainer
#from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
#from pdfminer.converter import TextConverter
#from pdfminer.layout import LAParams

#from io import BytesIO
#import string as str
from os.path import isfile, join
#from nltk.tokenize import word_tokenize
#from nltk.tokenize import TreebankWordTokenizer
#from nltk.tokenize import RegexpTokenizer
#import gensim
#from gensim.models.doc2vec import Doc2Vec, TaggedDocument
#from gensim.test.utils import common_texts
#from gensim.test.utils import get_tmpfile
import numpy as np
from os import listdir
import re, math
from collections import Counter

class Similar_Document():
    def __init__(self,top_list):
        #self.Database_path = '../xai_team_project/preprocessed/'
        self.report_1 = "This patient has a 40.0% atrophy of the temporal lobe, especially the hippocampus,compared to normal, and the whole brain volume has increased by 16.67 and is 67% as compared to be Alzheimer's."
        self.report_2 = "Significant reductions and atrophy in medically significant right caudate, right lateral ventricle, and right hippocampus in Alzheimer disease are seen"
        self.report_3 = "This patient has been unchanged in hippocampus area compared to normal subjects, and the whole brain volume is also around the average."
        self.report_4 = "As a result of MRI analysis of this patient, the brain volume of each region is as follows Hippocampus: 88.0, Ventricle: 10.0, Amygdala: 50.0 Thalamus: 70.0, Putamen: 90.0, Whole brain: 20.0  Compared to the abnormal group, this patient had the following differences Hippocampus 100.0% increase Ventricle 60% reduction Amygdala 17% reduction Thalamus 12% reduction Putamen 800% increase Whole brain 35% reduction"
        self.report_5 = "As a result of MRI analysis of this patient, the brain volume of each region is as follows Hippocampus: 50.0, Ventricle: 10.0, Amygdala: 50.0 Thalamus: 70.0, Putamen: 90.0, Whole brain: 20.0  Compared to the abnormal group, this patient had the following differences Hippocampus 100.0% reduction Ventricle 10% increase Amygdala 17% increase Thalamus 12% reduction Putamen 800% increase Whole brain 35% reduction"
        self.report = ''
        self.sims_list = []
        self.topic_list = []
        self.sent_list = []
        #self.file_lists = [f for f in listdir(self.Database_path) if isfile(join(self.Database_path, f))]
        self.TOP = top_list
        self.WORD = re.compile(r'\w+')


        self.file_to_index = {
            "ADNI_002_S_0938_AD.mgz" : 0,
            "ADNI_099_S_0372_AD.mgz" : 1,
            "ADNI_109_S_1157_AD.mgz" : 2,
            "ADNI_067_S_0257_CN.mgz" : 3,
            "ADNI_068_S_0127_CN.mgz" : 4,
            "ADNI_073_S_0311_CN.mgz" : 5,
            }

        self.index_to_topics={
            0:['New insights into brain BDNF function in normal aging and Alzheimer disease',
                'Amyloid precursor protein processing and A42 deposition in a transgenic mouse model of Alzheimer disease',
                'The developmental role of serotonin_3A news from mouse molecular genetics',
                'Chronic divalproex sodium use and brain atrophy in Alzheimer disease'],
            1:['High b-value diffusion imaging of dementia_3A application to vascular dementia and Alzheimer disease', 'Novel MRI techniques in the assessment of dementia', 'Amyloid precursor protein processing and A42 deposition in a transgenic mouse model of Alzheimer disease', 'Oxidative modification and down-regulation of Pin1 in Alzheimer_s disease hippocampus_3A a redox proteomics analysis'],
            2:['High b-value diffusion imaging of dementia_3A application to vascular dementia and Alzheimer disease', 'Novel MRI techniques in the assessment of dementia', 'Amyloid precursor protein processing and A42 deposition in a transgenic mouse model of Alzheimer disease'],
            3:['High b-value diffusion imaging of dementia_3A application to vascular dementia and Alzheimer disease', 'Novel MRI techniques in the assessment of dementia', 'Amyloid precursor protein processing and A42 deposition in a transgenic mouse model of Alzheimer disease'],
            4:['Amyloid precursor protein processing and A42 deposition in a transgenic mouse model of Alzheimer disease', 'High b-value diffusion imaging of dementia_3A application to vascular dementia and Alzheimer disease', 'Novel MRI techniques in the assessment of dementia'],
            5:['Amyloid precursor protein processing and A42 deposition in a transgenic mouse model of Alzheimer disease', 'High b-value diffusion imaging of dementia_3A application to vascular dementia and Alzheimer disease', 'Novel MRI techniques in the assessment of dementia'],
        }

        self.index_to_contents ={
            0:['Correlations between neuronal loss decrease of memory and decrease expression of brain derived neurotrophic factor in the gerbil hippocampus during normal aging\n', 'Both the sequence of events of this process as well as the brain region specificity of AD pathology have been extraordinarily difficult to unravel because brain tissue cannot typically be analyzed until after the death of these patients\n', 'So even though the effects of an excess or a decrease of HT are not as striking as was initially expected and cannot be detected by simple inspection of the brain they definitely exist\n', 'Valproate has been shown to decrease brain levels of myoinositol MI a known brain osmolyte and upregulate glycine on magnetic resonance spec troscopy even in the absence of clear hyperammone mia This may support a theory of global or localized osmotic shifts associated with the brain vol ume changes demonstrated in the present study\n'],
            1:['This is a result of the increase in the mean displacement of the GM and the infiltration of CSF and brain atrophy\n', 'This modification is supposed to increase the validity of the results by reducing the influence of non brain tissue\n', 'Both the sequence of events of this process as well as the brain region specificity of AD pathology have been extraordinarily difficult to unravel because brain tissue cannot typically be analyzed until after the death of these patients\n', 'Therefore the oxidation of Pin in severely affected region of the brain may increase the vulnerability of the hip pocampus leading to the progression of disease\n'],
            2:['This is a result of the increase in the mean displacement of the GM and the infiltration of CSF and brain atrophy\n', 'This modification is supposed to increase the validity of the results by reducing the influence of non brain tissue\n', 'Both the sequence of events of this process as well as the brain region specificity of AD pathology have been extraordinarily difficult to unravel because brain tissue cannot typically be analyzed until after the death of these patients\n'],
            3:['This is a result of the increase in the mean displacement of the GM and the infiltration of CSF and brain atrophy\n', 'This modification is supposed to increase the validity of the results by reducing the influence of non brain tissue\n', 'Both the sequence of events of this process as well as the brain region specificity of AD pathology have been extraordinarily difficult to unravel because brain tissue cannot typically be analyzed until after the death of these patients\n'],
            4:['Both the sequence of events of this process as well as the brain region specificity of AD pathology have been extraordinarily difficult to unravel because brain tissue cannot typically be analyzed until after the death of these patients\n', 'This is a result of the increase in the mean displacement of the GM and the infiltration of CSF and brain atrophy\n', 'This modification is supposed to increase the validity of the results by reducing the influence of non brain tissue\n'],
            5:['Both the sequence of events of this process as well as the brain region specificity of AD pathology have been extraordinarily difficult to unravel because brain tissue cannot typically be analyzed until after the death of these patients\n', 'This is a result of the increase in the mean displacement of the GM and the infiltration of CSF and brain atrophy\n', 'This modification is supposed to increase the validity of the results by reducing the influence of non brain tissue\n'],
        }


    def get_cosine(self,vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
        sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    def text_to_vector(self,text):
        words = self.WORD.findall(text)
        return Counter(words)

    def Analyze(self, file_name=""):
        # 시발 이게 머시여
        f = open("./Report_english.txt", "r")
        filename = file_name

        index = self.file_to_index[filename]

        topics = self.index_to_topics[index]
        contents = self.index_to_contents[index]
        return topics, contents
        '''
        all = f.readlines()
        for l in all:
            self.report = l

        print("Analyzing...")

        topics = []
        contents = []
        for n, each_file in enumerate(self.file_lists):

            f = open(self.Database_path + each_file, "r")
            lines = f.readlines()

            document = []
            for l in lines:
                document.append(l)
            f.close()

            max_similar = -99999
            max_sentence = ""

            for s, sentence in enumerate(document):

                shortword = re.compile(r'\W*\b\w{1,2}\b')

                shortword.sub('', self.report)
                shortword.sub('', sentence)

                target = self.text_to_vector(self.report)
                source = self.text_to_vector(sentence)
                similar = self.get_cosine(target, source)

                if similar >= max_similar:
                    max_similar = similar
                    max_sentence = sentence

            self.sims_list.append(max_similar)
            self.topic_list.append(each_file.replace('.txt', ''))
            self.sent_list.append(max_sentence)

        sims_list = np.array(self.sims_list)

        index = sims_list.argsort()[-self.TOP:][::-1]

        for idx in index:
            self.topic_list[idx] = self.topic_list[idx].replace('%3A',':')
            self.topic_list[idx] = self.topic_list[idx].replace('¥â', '')

            cnt = 0
            for w in topic:
                if cnt == 35:
                    temp += '\n'
                    temp += w
                    cnt = 0
                else:
                    temp += w
                    cnt += 1
        '''

         #   topics.append(self.topic_list[idx])
         #   contents.append(self.sent_list[idx])

        #topics = topics.replace('%3A', ':')
        #self.topic_list = self.topic_list[index].replace('%3A', ':')
        #print("topics")
        #print(topics)
        #print("contents")
        #print(contents)
        #return topics, contents




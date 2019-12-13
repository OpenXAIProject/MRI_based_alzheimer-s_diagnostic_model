# -*- coding: utf-8 -*-
#from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktTrainer
#from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
#from pdfminer.converter import TextConverter
#from pdfminer.layout import LAParams
#from pdfminer.pdfpage import PDFPage
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
from os import listdir

# 텍스트를 읽어와서 Document2Vector를 만드는 과정

Database_path = '/home/jungjunkim/xai_team_project/preprocessed/'
file_lists = [f for f in listdir(Database_path) if isfile(join(Database_path, f))]

for each_file in file_lists:

    f = open(Database_path + each_file, "r")
    lines = f.readlines()

    document = []
    for l in lines:
        document.append(l)
    f.close()

    documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(document)]
    model = Doc2Vec(documents, vector_size=7, window=4, min_count=3, workers=6)
    fname = '/home/jungjunkim/xai_team_project/doc2vec_models/'+ each_file.replace('.txt','')
    model.save(fname)







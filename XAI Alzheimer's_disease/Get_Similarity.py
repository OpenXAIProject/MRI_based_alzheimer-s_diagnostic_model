# -*- coding: utf-8 -*-

from os.path import isfile, join
import numpy as np
from os import listdir
import re, math
from collections import Counter
WORD = re.compile(r'\w+')

TOP = 5

def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)

Database_path = '../xai_team_project/preprocessed/'

file_lists = [f for f in listdir(Database_path) if isfile(join(Database_path, f))]

example_1 = "This patient has a 40 atrophy of the temporal lobe, especially the hippocampus," \
         " compared to normal, and the whole brain volume has increased by 16 and is 67 as compared to be Alzheimer's."
example_2 = "Significant reductions and atrophy in medically significant right caudate, right lateral ventricle, and right hippocampus in Alzheimer disease are seen"
example_3 = "This patient has been unchanged in hippocampus area compared to normal subjects, and the whole brain volume is also around the average"
example_4 = "Alzheimer patient has been shrank in hippocampus area compared to normal subject. and the whole brain volume is also small evidence pathology linked to Alzheimer disease AD"
report = example_4
print("report: ",report)

sims_list = []
topic_list = []
sent_list = []

for n, each_file in enumerate(file_lists):

    f = open(Database_path + each_file, "r")
    lines = f.readlines()

    document = []
    for l in lines:
        document.append(l)
    f.close()

    # fname = Model_path + each_file.replace('.txt', '')
    # model = Doc2Vec.load(fname)

    topic_ = each_file.replace('.txt','')

    max_similar = -99999
    max_sentence = ""

    for s, sentence in enumerate(document):

        shortword = re.compile(r'\W*\b\w{1,2}\b')
        shortword.sub('', report)
        shortword.sub('', sentence)

        target = text_to_vector(report)
        source = text_to_vector(sentence)
        similar = get_cosine(target,source)

        if similar >= max_similar:
            max_similar = similar
            max_sentence = sentence

    sims_list.append(max_similar)
    topic_list.append(each_file.replace('.txt',''))
    sent_list.append(max_sentence)

sims_list = np.array(sims_list)

index = sims_list.argsort()[-TOP:][::-1]

print(index)
print(sims_list[index])

for idx in index:
    print("similarity: ",sims_list[idx])
    print("topic: ", topic_list[idx].replace('%3A',':'))
    print("content: ", sent_list[idx])


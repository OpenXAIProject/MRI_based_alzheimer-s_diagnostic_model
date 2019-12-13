# -*- coding: utf-8 -*-
#import numpy as np

#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure
import matplotlib.pyplot as plt

type = ('AD', 'NC')

y_pred = (0.78,0.22)
fig, ax = plt.subplots(1,1,figsize=(7,5)) # 1x1 figure matrix 생성, 가로(7인치)x세로(5인치) 크기지정
ax.set_xlim([0.0,0.99])
ax.xaxis.set_tick_params(labelsize=10)
ax.set_xlabel('Prediction Accuracy', fontsize=14)

h = plt.barh(type, y_pred,color=['salmon','skyblue'])

plt.legend(h,type)
plt.savefig('predict.png', format='png', dpi=300)
for p in ax.patches:
    percentage = '{:.2f}%'.format(100*p.get_width()/100)
    x = p.get_x() + p.get_width()+0.02
    y = p.get_y() + p.get_height()/2
    ax.annotate(percentage, (x,y), fontsize=15)

plt.show()


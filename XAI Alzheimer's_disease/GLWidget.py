from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import matplotlib.image as mping

#import nibabel as nib
import numpy as np

import sys
#import math

from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)

import OpenGL.GL as gl
from OpenGL.GLU import *
from PyQt5.QtCore import QPointF, QRect, QRectF, Qt, QTimer
from PyQt5.QtGui import (QBrush, QColor, QFont, QLinearGradient, QPainter,
                         QPen, QSurfaceFormat)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLabel, QOpenGLWidget,
                             QWidget)

from utility import *



class GLWidget(QOpenGLWidget):

    clicked = pyqtSignal()

    PROGRAM_VERTEX_ATTRIBUTE, PROGRAM_TEXCOORD_ATTRIBUTE = range(2)

    vsrc = """
attribute highp vec4 vertex;
attribute mediump vec4 texCoord;
varying mediump vec4 texc;
uniform mediump mat4 matrix;
void main(void)
{
    gl_Position = matrix * vertex;
    texc = texCoord;
}
"""

    fsrc = """
uniform sampler2D texture;
varying mediump vec4 texc;
void main(void)
{
    gl_FragColor = texture2D(texture, texc.st);
}
"""

    coords = (
        (( +1, -1, 0 ), ( -1, -1, 0 ), ( -1, +1, 0 ), ( +1, +1, 0 )),
        (( +1, 0, -1 ), ( -1, 0, -1 ), ( -1, 0, +1 ), ( +1, 0, +1 )),
        (( 0, -1, +1 ), ( 0, -1, -1 ), ( 0, +1, -1 ), ( 0, +1, +1 )),
        (( 0, -1, -1 ), ( 0, -1, +1 ), ( 0, +1, +1 ), ( 0, +1, -1 )),
        (( +1, 0, +1 ), ( -1, 0, +1 ), ( -1, 0, -1 ), ( +1, 0, -1 )),
        (( -1, -1, 0 ), ( +1, -1, 0 ), ( +1, +1, 0 ), ( -1, +1, 0 ))
    )

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        print("Constructure")
        self.clearColor = QColor(Qt.black)
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.program = 0

        self.lastPos = QPoint()

        self.textures = []
        self.texCoords = []
        self.vertices = []
        self.Isvol = False

        self.rate_x = 0.32 #self.s1/sum
        self.rate_y = 0.32 #self.s3/sum
        self.rate_z = 0.35 #self.s2/sum

        self.move_x = 0.0
        self.move_y = 0.0
        self.move_z = 0.0

        default_pix = 100
        _black = np.zeros((default_pix, default_pix, 3), dtype=np.uint8)

        # images

        ax_image = _black
        self.ax_image = ax_image.astype(np.uint8).copy()
        self.ax_image_flip = np.flipud(self.ax_image).copy()

        co_image = _black
        self.co_image = co_image.astype(np.uint8).copy()
        self.co_image_flip = np.fliplr(self.co_image).copy()

        sa_image = _black
        self.sa_image = sa_image.astype(np.uint8).copy()
        self.sa_image_flip = np.fliplr(self.sa_image).copy()

        # QImage

        self.axial_01 = QImage(self.ax_image, default_pix, default_pix, 3 * default_pix, QImage.Format_RGB888)
        self.axial_02 = QImage(self.ax_image_flip, default_pix, default_pix, 3 * default_pix, QImage.Format_RGB888)

        self.coronal_01 = QImage(self.co_image, default_pix, default_pix, 3 * default_pix, QImage.Format_RGB888)
        self.coronal_02 = QImage(self.co_image_flip, default_pix, default_pix, 3 * default_pix, QImage.Format_RGB888)

        self.sagittal_01 = QImage(self.sa_image, default_pix, default_pix, 3 * default_pix, QImage.Format_RGB888)
        self.sagittal_02 = QImage(self.sa_image_flip, default_pix, default_pix, 3 * default_pix, QImage.Format_RGB888)

    def axis_change(self):
        self.rate_x = 0.0
        self.rate_y = 0.0
        self.rate_z = 0.0
        self.makeObject()
        self.update()

    def Volume_change(self,volume_info=[]):
        print("Volume_change")
        ax_image, co_image, sa_image, ax_sz, co_sz, sa_sz = volume_info
        ax_image = ax_image.astype(np.uint8)
        co_image = co_image.astype(np.uint8)
        sa_image = sa_image.astype(np.uint8)

        # Size
        self.ax_sz = ax_sz
        self.co_sz = co_sz
        self.sa_sz = sa_sz

        # images

        #ax_image = self.brainmask_rgb[int(self.s3/2),:,:,:]
        ax_image = Draw_rect(ax_image, color=[0, 255, 0])
        self.ax_image = np.flipud(ax_image.astype(np.uint8)).copy()
        self.ax_image_flip = np.flipud(self.ax_image).copy()

        #co_image = self.brainmask_rgb[:, int(self.s2 / 2), :, :]
        co_image = Draw_rect(co_image, color=[255, 0, 0])
        self.co_image = co_image.astype(np.uint8).copy()
        self.co_image_flip = np.fliplr(self.co_image).copy()

        #sa_image = self.brainmask_rgb[:, :, int(self.s1/2), :]
        sa_image = Draw_rect(sa_image, color=[0, 0, 255])
        self.sa_image = sa_image.astype(np.uint8).copy()
        self.sa_image_flip = np.fliplr(self.sa_image).copy()

        # QImage
        # ax_sz, co_sz, sa_sz
        self.axial_01 = QImage(self.ax_image, sa_sz, co_sz, 3 * sa_sz, QImage.Format_RGB888)
        self.axial_02 = QImage(self.ax_image_flip, sa_sz, co_sz, 3 * sa_sz, QImage.Format_RGB888)

        self.coronal_01 = QImage(self.co_image, sa_sz, ax_sz, 3 * sa_sz, QImage.Format_RGB888)
        self.coronal_02 = QImage(self.co_image_flip, sa_sz, ax_sz, 3 * sa_sz, QImage.Format_RGB888)

        self.sagittal_01 = QImage(self.sa_image, co_sz, ax_sz, 3 * co_sz, QImage.Format_RGB888)
        self.sagittal_02 = QImage(self.sa_image_flip, co_sz, ax_sz, 3 * co_sz, QImage.Format_RGB888)

        # ax_sz, co_sz, sa_sz
        sum = ax_sz + co_sz + sa_sz
        # rate
        self.rate_x = co_sz/sum
        self.rate_y = ax_sz/sum
        self.rate_z = sa_sz/sum

        self.makeObject()

        self.update()


    def rotateBy(self, xAngle, yAngle, zAngle):
        self.xRot += xAngle
        self.yRot += yAngle
        self.zRot += zAngle
        self.update()

    def setClearColor(self, color):
        self.clearColor = color
        self.update()

    def load(self):
        # image change


        self.axial_01 = QImage(self.ax_image, self.s3, self.s2, 3 * self.s3, QImage.Format_RGB888)
        self.axial_02 = QImage(self.ax_image_flip, self.s3, self.s2, 3 * self.s3, QImage.Format_RGB888)

        self.coronal_01 = QImage(self.ax_image, self.s3, self.s2, 3 * self.s3, QImage.Format_RGB888)#QImage(self.co_image, self.s3, self.s1, 3 * self.s3, QImage.Format_RGB888)
        self.coronal_02 = QImage(self.ax_image_flip, self.s3, self.s2, 3 * self.s3, QImage.Format_RGB888)#QImage(self.co_image_flip, self.s3, self.s1, 3 * self.s3, QImage.Format_RGB888)

        self.sagittal_01 = QImage(self.ax_image_flip, self.s3, self.s2, 3 * self.s3, QImage.Format_RGB888)#QImage(self.sa_image, self.s2, self.s1, 3 * self.s2, QImage.Format_RGB888)
        self.sagittal_02 = QImage(self.ax_image_flip, self.s3, self.s2, 3 * self.s3, QImage.Format_RGB888)#QImage(self.sa_image_flip, self.s2, self.s1, 3 * self.s2, QImage.Format_RGB888)


    def initializeGL(self):
        print("initializeGL")
        #self.gl = self.context().versionFunctions()
        #gl.initializeOpenGLFunctions()

        self.makeObject()

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_TEXTURE_2D)
        vshader = QOpenGLShader(QOpenGLShader.Vertex, self)
        vshader.compileSourceCode(self.vsrc)

        fshader = QOpenGLShader(QOpenGLShader.Fragment, self)
        fshader.compileSourceCode(self.fsrc)
        #self.program.
        self.program = QOpenGLShaderProgram()
        self.program.addShader(vshader)
        self.program.addShader(fshader)
        self.program.bindAttributeLocation('vertex', self.PROGRAM_VERTEX_ATTRIBUTE)
        self.program.bindAttributeLocation('texCoord', self.PROGRAM_TEXCOORD_ATTRIBUTE)
        self.program.link()

        self.program.bind()
        self.program.setUniformValue('texture', 0)

        self.program.enableAttributeArray(self.PROGRAM_VERTEX_ATTRIBUTE)
        self.program.enableAttributeArray(self.PROGRAM_TEXCOORD_ATTRIBUTE)
        self.program.setAttributeArray(self.PROGRAM_VERTEX_ATTRIBUTE, self.vertices)
        self.program.setAttributeArray(self.PROGRAM_TEXCOORD_ATTRIBUTE, self.texCoords)

    def paintGL(self):
        gl.glClearColor(self.clearColor.redF(), self.clearColor.greenF(),
                        self.clearColor.blueF(), self.clearColor.alphaF())
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        m = QMatrix4x4()
        m.ortho(-0.5, 0.5, 0.5, -0.5, 4.0, 15.0)
        m.translate(0.0, 0.0, -10.0)
        m.rotate(self.xRot / 16.0, 1.0, 0.0, 0.0)
        m.rotate(self.yRot / 16.0, 0.0, 1.0, 0.0)
        m.rotate(self.zRot / 16.0, 0.0, 0.0, 1.0)

        camMatrix = QMatrix4x4(m);


        for i, texture in enumerate(self.textures):
            self.program.setUniformValue('matrix', camMatrix)

            if i == 0:
                localMatrix = QMatrix4x4(camMatrix)
                localMatrix.translate(0.0, 0.0, self.move_z)
                self.program.setUniformValue('matrix', localMatrix)

            elif i == 1:
                localMatrix = QMatrix4x4(camMatrix)
                localMatrix.translate(0.0, 0.0, self.move_z)
                self.program.setUniformValue('matrix', localMatrix)

            elif i == 4:
                localMatrix = QMatrix4x4(camMatrix)
                localMatrix.translate(0.0, self.move_y, 0.0)
                self.program.setUniformValue('matrix', localMatrix)

            elif i == 5:
                localMatrix = QMatrix4x4(camMatrix)
                localMatrix.translate(0.0, self.move_y, 0.0)
                self.program.setUniformValue('matrix', localMatrix)

            elif i == 3:
                localMatrix = QMatrix4x4(camMatrix)
                localMatrix.translate(self.move_x, 0.0, 0.0)
                self.program.setUniformValue('matrix', localMatrix)

            elif i == 2:
                localMatrix = QMatrix4x4(camMatrix)
                localMatrix.translate(self.move_x, 0.0, 0.0)
                self.program.setUniformValue('matrix', localMatrix)

            texture.bind()
            gl.glDrawArrays(gl.GL_TRIANGLE_FAN, i * 4, 4)

    def move_axial(self, volume_info, index):
        ax_image = volume_info
        ax_image = ax_image.astype(np.uint8)
        # images

        # co_image = self.brainmask_rgb[:, int(self.s2 / 2), :, :]
        ax_image = Draw_rect(ax_image, color=[0, 255, 0])
        self.ax_image = np.flipud(ax_image).astype(np.uint8).copy()
        self.ax_image_flip = np.flipud(self.ax_image).copy()

        # QImage
        # ax_sz, co_sz, sa_sz
        w, h, c = np.shape(self.ax_image)
        self.axial_01 = QImage(self.ax_image, h, w, 3 * h, QImage.Format_RGB888)
        self.axial_02 = QImage(self.ax_image_flip, h, w, 3 * h, QImage.Format_RGB888)

        self.move_y = (float(index) / float(self.ax_sz) - 0.5) * 2 * self.rate_y
        #print(self.move_y)

        self.makeObject()
        self.update()

    def move_sagittal(self, volume_info, index):
        sa_image = volume_info
        sa_image = sa_image.astype(np.uint8)
        # images

        # co_image = self.brainmask_rgb[:, int(self.s2 / 2), :, :]
        sa_image = Draw_rect(sa_image, color=[0, 0, 255])
        self.sa_image = sa_image.astype(np.uint8).copy()
        self.sa_image_flip = np.fliplr(self.sa_image).copy()
        #self.sa_image_flip = sa_image.astype(np.uint8).copy()
        # QImage
        # ax_sz, co_sz, sa_sz
        w, h, c = np.shape(self.sa_image)
        self.sagittal_01 = QImage(self.sa_image, h, w, 3 * h, QImage.Format_RGB888)
        self.sagittal_02 = QImage(self.sa_image_flip, h, w, 3 * h, QImage.Format_RGB888)

        self.move_x = (float(index) / float(self.sa_sz) - 0.5) * 2 * self.rate_x
        #print(self.move_x)

        self.makeObject()
        self.update()

    def move_coronal(self, volume_info, index):
        co_image = volume_info
        co_image = co_image.astype(np.uint8)
        # images

        # co_image = self.brainmask_rgb[:, int(self.s2 / 2), :, :]
        co_image = Draw_rect(co_image, color=[255, 0, 0])
        self.co_image = co_image.astype(np.uint8).copy()
        self.co_image_flip = np.fliplr(self.co_image).copy()

        # QImage
        # ax_sz, co_sz, sa_sz
        w,h,c = np.shape(self.co_image)
        self.coronal_01 = QImage(self.co_image, h, w, 3 * h, QImage.Format_RGB888)
        self.coronal_02 = QImage(self.co_image_flip, h, w, 3 * h, QImage.Format_RGB888)

        self.move_z = -(float(index) / float(self.co_sz) - 0.5) * 2 * self.rate_z
        #print(self.move_z)

        self.makeObject()
        self.update()


    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(200, 200)

    def makeObject(self):

        '''
            coords = (
            (( +1, -1, 0 ), ( -1, -1, 0 ), ( -1, +1, 0 ), ( +1, +1, 0 )),
            (( +1, 0, -1 ), ( -1, 0, -1 ), ( -1, 0, +1 ), ( +1, 0, +1 )),
            (( 0, -1, +1 ), ( 0, -1, -1 ), ( 0, +1, -1 ), ( 0, +1, +1 )),
            (( 0, -1, -1 ), ( 0, -1, +1 ), ( 0, +1, +1 ), ( 0, +1, -1 )),
            (( +1, 0, +1 ), ( -1, 0, +1 ), ( -1, 0, -1 ), ( +1, 0, -1 )),
            (( -1, -1, 0 ), ( +1, -1, 0 ), ( +1, +1, 0 ), ( -1, +1, 0 ))
        )
       '''

        self.textures = []
        self.texCoords = []
        self.vertices = []

        self.textures.append(QOpenGLTexture(self.coronal_01.mirrored()))
        for j in range(4):
            self.texCoords.append(((j == 0 or j == 3), (j == 0 or j == 1)))
            x, y, z = self.coords[0][j]
            self.vertices.append((self.rate_x * x, self.rate_y * y, self.rate_z * z))

        self.textures.append(QOpenGLTexture(self.coronal_02.mirrored()))
        for j in range(4):
            self.texCoords.append(((j == 0 or j == 3), (j == 0 or j == 1)))
            x, y, z = self.coords[5][j]
            self.vertices.append((self.rate_x * x, self.rate_y * y, self.rate_z * z))

        self.textures.append(QOpenGLTexture(self.sagittal_01.mirrored()))
        for j in range(4):
            self.texCoords.append(((j == 0 or j == 3), (j == 0 or j == 1)))
            x, y, z = self.coords[3][j]
            self.vertices.append((self.rate_x * x, self.rate_y * y, self.rate_z * z))

        self.textures.append(QOpenGLTexture(self.sagittal_02.mirrored()))
        for j in range(4):
            self.texCoords.append(((j == 0 or j == 3), (j == 0 or j == 1)))
            x, y, z = self.coords[2][j]
            self.vertices.append((self.rate_x * x, self.rate_y * y, self.rate_z * z))

        self.textures.append(QOpenGLTexture(self.axial_01.mirrored()))
        for j in range(4):
            self.texCoords.append(((j == 0 or j == 3), (j == 0 or j == 1)))
            x, y, z = self.coords[1][j]
            self.vertices.append((self.rate_x * x, self.rate_y * y, self.rate_z * z))

        self.textures.append(QOpenGLTexture(self.axial_02.mirrored()))
        for j in range(4):
            self.texCoords.append(((j == 0 or j == 3), (j == 0 or j == 1)))
            x, y, z = self.coords[4][j]
            self.vertices.append((self.rate_x * x, self.rate_y * y, self.rate_z * z))

    def resizeGL(self, width, height):
        side = min(width, height)
        gl.glViewport((width - side) // 2, (height - side) // 2, side, side)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.rotateBy(8 * dy, 8 * dx, 0)
        elif event.buttons() & Qt.RightButton:
            self.rotateBy(8 * dy, 0, 8 * dx)

        self.lastPos = event.pos()

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


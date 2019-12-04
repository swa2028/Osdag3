# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_plate.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Plate(object):
    def setupUi(self, Plate):
        Plate.setObjectName("Plate")
        Plate.resize(287, 129)
        self.gridLayout = QtWidgets.QGridLayout(Plate)
        self.gridLayout.setObjectName("gridLayout")
        self.plateHeight = QtWidgets.QLabel(Plate)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.plateHeight.setFont(font)
        self.plateHeight.setObjectName("plateHeight")
        self.gridLayout.addWidget(self.plateHeight, 0, 0, 1, 1)
        self.txt_plateThickness = QtWidgets.QLineEdit(Plate)
        self.txt_plateThickness.setObjectName("txt_plateThickness")
        self.gridLayout.addWidget(self.txt_plateThickness, 3, 1, 1, 1)
        self.txt_plateLength = QtWidgets.QLineEdit(Plate)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.txt_plateLength.setFont(font)
        self.txt_plateLength.setReadOnly(True)
        self.txt_plateLength.setObjectName("txt_plateLength")
        self.gridLayout.addWidget(self.txt_plateLength, 0, 1, 1, 1)
        self.txt_plateWidth = QtWidgets.QLineEdit(Plate)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.txt_plateWidth.setFont(font)
        self.txt_plateWidth.setReadOnly(True)
        self.txt_plateWidth.setObjectName("txt_plateWidth")
        self.gridLayout.addWidget(self.txt_plateWidth, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(Plate)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(Plate)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)

        self.retranslateUi(Plate)
        QtCore.QMetaObject.connectSlotsByName(Plate)

    def retranslateUi(self, Plate):
        _translate = QtCore.QCoreApplication.translate
        Plate.setWindowTitle(_translate("Plate", "Plate "))
        self.plateHeight.setText(_translate("Plate", "Length (mm)"))
        self.label_2.setText(_translate("Plate", "Width (mm)"))
        self.label_4.setText(_translate("Plate", "Thickness (mm)"))

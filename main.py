# -*- coding: utf-8 -*-
from os import listdir
from os.path import isfile, join
from PyQt4 import QtCore, QtGui ,uic

import sys


import vtk




class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self)
        self.setWindowTitle("3D reconstruction of medical images")
        self.setWindowIcon(QtGui.QIcon('icon.jpg'))
        self.pathdir = ""
        self.reader = vtk.vtkDICOMImageReader()
        self.dmc = vtk.vtkDiscreteMarchingCubes()
        self.dicomCounter = 0
        uic.loadUi('Interface.ui', self)
        self.load.clicked.connect(self.getdir)
        self.run.clicked.connect(self.visualisation)
        self.save.clicked.connect(self.savemodel)

        self.nbrimages.setText("")



    def getdir(self):
        qt = QtGui.QFileDialog()
        # direc = openDirectoryDialog.getOpenFileName(self, "open", "home")  # open file name
        self.pathdir = qt.getExistingDirectory(self, "open")  # Selectes folder

        if len(self.pathdir) > 0:
            
            listefiles = [f for f in listdir(pathde) if isfile(join(pathde, f))]
            for n in range(0, len(listefiles)):
                self.dicomCounter += 1

            srt = "{}".format(self.dicomCounter)
            self.nbrimages.setText(srt)

            self.reader.SetDirectoryName(pathde)
            self.reader.Update()

            shiftScale = vtk.vtkImageShiftScale()
            shiftScale.SetScale(self.reader.GetRescaleSlope())
            shiftScale.SetShift(self.reader.GetRescaleOffset())
            shiftScale.SetInputConnection(self.reader.GetOutputPort())
            shiftScale.Update()

    def visualisation(self):
            threshold = vtk.vtkImageThreshold()
            threshold.SetInputConnection(self.reader.GetOutputPort())
            threshold.ThresholdByLower(400)  # remove all soft tissue
            threshold.ReplaceInOn()
            threshold.SetInValue(0)  # set all values below 400 to 0
            threshold.ReplaceOutOn()
            threshold.SetOutValue(1)  # set all values above 400 to 1
            threshold.Update()


            self.dmc.SetInputConnection(threshold.GetOutputPort())
            self.dmc.GenerateValues(1, 1, 1)
            self.dmc.Update()



            ren = vtk.vtkRenderer()
            renWin = vtk.vtkRenderWindow()
            renWin.AddRenderer(ren)

            # create a render window interactor
            self.iren = vtk.vtkRenderWindowInteractor()
            self.iren.SetRenderWindow(renWin)

            # mapper
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInput(self.dmc.GetOutput())

            # actor
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            # assign actor to the renderer
            ren.AddActor(actor)
            ren.SetBackground(1, 1, 1)
            # enable user interface interactor
            self.iren.Initialize()
            renWin.Render()
            self.iren.Start()

    def savemodel(self):

        writer = vtk.vtkSTLWriter()
        writer.SetInputConnection(self.dmc.GetOutputPort())
        writer.SetFileTypeToBinary()
        writer.SetFileName("bones.stl")
        writer.Write()


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


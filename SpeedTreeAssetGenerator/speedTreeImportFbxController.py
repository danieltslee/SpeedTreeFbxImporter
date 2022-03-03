import hou
import os
from . import fbxSubnet
from PySide2 import QtCore, QtUiTools, QtWidgets
from functools import partial

class SpeedTreeFbxImporter(QtWidgets.QWidget):

    def __init__(self):
        super(SpeedTreeFbxImporter, self).__init__()
        #ui_file = 'Z:\houdini19.0\python3.7libs\SpeedTreeAssetGenerator\SpeedTreeImportFbxUI.ui'

        parentDir = os.path.split(__file__)[0]
        directoryContent = os.listdir(parentDir)
        for content in directoryContent:
            if content == 'SpeedTreeImportFbxUI.ui':
                ui_file = os.path.join(parentDir, content)
                self.ui = QtUiTools.QUiLoader().load(ui_file)
                self.layout = QtWidgets.QVBoxLayout(self)
                self.layout.addWidget(self.ui)
                self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        self.directoryPath = None
        hipDir = os.path.dirname(hou.hipFile.path())
        self.ui.directoryPath.setText(hipDir)

        self.ui.tableOfFoldersOnDisk.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        print(self.ui.matchSize.isChecked())
        print(self.ui.convertToYup.isChecked())

        # Signal
        self.signals()

    def signals(self):
        self.ui.launchBrowser.pressed.connect(partial(self.treeDirectory))
        self.ui.tableOfFoldersOnDisk.customContextMenuRequested.connect(self.tableMenu)

    def treeDirectory(self):
        # Browse to folder on dist
        fileExplore = QtWidgets.QFileDialog()
        self.directoryPath = fileExplore.getExistingDirectory(self,
                                                              dir=self.ui.directoryPath.text(),
                                                              caption="Select Directory Containing Fbxs")
        self.ui.directoryPath.setText(self.directoryPath)

        # Get formatted dictionary
        fbxImportFormat = fbxSubnet.getFbxFilesList(self.directoryPath)[0]

        # List of tree subnet folder names
        fbxDirNames = list(fbxImportFormat.keys())
        # Set row count on table
        self.ui.tableOfFoldersOnDisk.setRowCount(len(fbxDirNames))
        if len(fbxDirNames) == 0:
            # TODO add button functionality
            okOrCancel = self.messageBox(self.directoryPath)
        # Populate table
        for importIndex in range(0, len(fbxDirNames)):
            # Populate rows
            treeDirName = QtWidgets.QTableWidgetItem(fbxDirNames[importIndex])
            self.ui.tableOfFoldersOnDisk.setItem(importIndex, 0, treeDirName)

            # Populate Columns
            numFbxPaths = len(fbxImportFormat[fbxDirNames[importIndex]])
            if numFbxPaths < 2:
                fbxFoundMsg = "{NUMOFITEMS} fbx found".format(NUMOFITEMS=numFbxPaths)
            else:
                fbxFoundMsg = "{NUMOFITEMS} fbxs found".format(NUMOFITEMS=numFbxPaths)
            fbxFoundMsgObj = QtWidgets.QTableWidgetItem(fbxFoundMsg)
            self.ui.tableOfFoldersOnDisk.setItem(importIndex, 1, fbxFoundMsgObj)

    def messageBox(self, dir):
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Information)
        dialog.setWindowTitle("Proceed?")
        dialog.setText("No fbxs found in {DIR}, proceed?".format(DIR=dir))

        dialog.setStandardButtons(QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
        dialog.setDefaultButton(QtWidgets.QMessageBox.Yes)

        ret = dialog.exec_()

        if ret == dialog.Ok:
            return True
        else:
            return False

    def tableMenu(self, pos):
        menu = QtWidgets.QMenu()
        self.fileAction = QtWidgets.QAction("Clear")
        self.fileAction.triggered.connect(self.reformatClearedTable)
        menu.addAction(self.fileAction)
        menu.exec_(self.ui.tableOfFoldersOnDisk.viewport().mapToGlobal(pos))

    def reformatClearedTable(self):
        """numOfCol = self.ui.tableOfFoldersOnDisk.columnCount()
        for colIndex in range(0, numOfCol):
            self.ui.tableOfFoldersOnDisk."""
        self.ui.tableOfFoldersOnDisk.clearContents()

        """# Clears rows  TODO HORIZONTAL HEADER STILL DOESN'T CLEAR
        numOfRows = self.ui.tableOfFoldersOnDisk.rowCount()
        for rowIndex in range(0, numOfRows):
            self.ui.tableOfFoldersOnDisk"""

"""    def populateTreeSubnetList(self):
        obj = hou.node("/obj")
        self.ui.listOfTreeSubnets.clear()
        
        generatedNodes = []
        for node in obj:
            if node.creatorState() == "SpeedTree Asset Generator by Daniel":
                
        for selection in multipleSelections:
            item = QtWidgets.QListWidgetItem(selection)
            self.ui.listOfTreeSubnets.addItem(item)"""

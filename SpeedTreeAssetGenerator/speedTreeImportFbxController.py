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

        # Set default directory path
        self.directoryPath = None
        hipDir = os.path.dirname(hou.hipFile.path())
        self.ui.directoryPath.setText(hipDir)

        self.ui.tableOfFoldersOnDisk.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # Detect tree subnets in scene
        self.populateTreeSubnetTable()

        # Signal
        self.signals()

    def signals(self):
        self.ui.launchBrowser.pressed.connect(partial(self.treeDirectory))
        self.ui.tableOfFoldersOnDisk.customContextMenuRequested.connect(self.tableMenuTreesInDir)

    def treeDirectory(self):
        """ Open file explorer to find the directory containing trees """
        # Browse to folder on dist
        fileExplore = QtWidgets.QFileDialog()
        self.directoryPath = fileExplore.getExistingDirectory(self,
                                                              dir=self.ui.directoryPath.text(),
                                                              caption="Select Directory Containing Fbxs")
        self.ui.directoryPath.setText(self.directoryPath)

        # Get formatted dictionary
        fbxImportFormat = fbxSubnet.getFbxFilesList(self.directoryPath)[0]

        self.populateTreeDirTable(fbxImportFormat)

    def populateTreeDirTable(self, fbxImportFormat):
        """ Tree directory table from directoryPath """
        # List of tree subnet folder names
        fbxDirNames = list(fbxImportFormat.keys())
        # Set row count on table
        self.ui.tableOfFoldersOnDisk.setRowCount(len(fbxDirNames))

        # If no folders containing fbxs were found
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

    def tableMenuTreesInDir(self, pos):
        """ Right Click Menu for tableOfFoldersOnDisk """
        menu = QtWidgets.QMenu()
        self.fileAction = QtWidgets.QAction("Clear")
        self.fileAction.triggered.connect(self.reformatClearedTable)
        menu.addAction(self.fileAction)
        menu.exec_(self.ui.tableOfFoldersOnDisk.viewport().mapToGlobal(pos))

    def reformatClearedTable(self):
        """ Clears all rows but keeps columns in a table widget """
        self.ui.tableOfFoldersOnDisk.clearContents()
        # Clears rows
        self.ui.tableOfFoldersOnDisk.setRowCount(0)

    def populateTreeSubnetTable(self):
        obj = hou.node("/obj")
        self.ui.tableOfTreeSubnets.clear()

        generatedNodes = []
        for node in obj.children():
            if node.creatorState() == "SpeedTree Asset Generator by Daniel":
                generatedNodes.append(node)

        if not generatedNodes:
            self.ui.listOfTreeSubnets.addItem("No Tree Subnets Detected")
            noItemsText = self.ui.listOfTreeSubnets.item(0)
            noItemsText.setForeground(QtCore.Qt.red)
            return

        # Generate rows
        self.ui.tableOfTreeSubnets.setRowCount(len(generatedNodes))
        for nodeIndex in range(0, len(generatedNodes)):
            generatedNodeNameObj = QtWidgets.QTableWidgetItem(generatedNodes[nodeIndex].name())
            self.ui.tableOfTreeSubnets.setItem(nodeIndex, 0, generatedNodeNameObj)


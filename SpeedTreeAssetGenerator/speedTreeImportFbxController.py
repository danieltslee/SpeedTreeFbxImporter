import hou
import os
from . import fbxSubnet
from . import execute
from PySide2 import QtCore, QtUiTools, QtWidgets
from functools import partial
from collections import OrderedDict

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
        hipDir = os.path.dirname(hou.hipFile.path())
        self.directoryPath = hipDir
        self.ui.directoryPath.setText(self.directoryPath)

        self.ui.tableOfFoldersOnDisk.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # Select model is rows only
        self.ui.tableOfFoldersOnDisk.setSelectionBehavior(QtWidgets.QTableView.SelectRows)

        # Detect tree subnets in scene
        self.populateTreeSubnetTable()

        # Signal
        self.signals()

    def signals(self):
        self.ui.launchBrowser.pressed.connect(partial(self.launchTreeDirectoryBrowser))
        self.ui.tableOfFoldersOnDisk.customContextMenuRequested.connect(self.tableMenuTreesInDir)

        self.ui.importFbxExecute.pressed.connect(partial(self.testFunc))

        # TODO update when line edit (directoryPath) is manually typed in
        #self.ui.directoryPath.textChanged.connect(self.updateTreeDirTable)

    def launchTreeDirectoryBrowser(self):
        """ Open file explorer to find the directory containing trees """
        # Browse to folder on dist
        fileExplore = QtWidgets.QFileDialog()
        exploredPath = fileExplore.getExistingDirectory(self,
                                                              dir=self.ui.directoryPath.text(),
                                                              caption="Select Directory Containing Fbxs")

        # Set self.directoryPath to new searched path
        if exploredPath:
            # Set path in line edit to path of file explorer
            self.directoryPath = exploredPath
            self.ui.directoryPath.setText(self.directoryPath)
        else:
            # If exited fire explorer, then exit method
            return

        # Populate tree directory table
        self.populateTreeDirTable(self.directoryPath)
        # Add messages and color
        self.visualizeTreeDirTable()

        # Visualize tree Subnets table
        self.visualizeTreeSubnetTable()

    def populateTreeDirTable(self, directoryPath):
        """ Tree directory table from directoryPath """
        # Get formatted dictionary
        fbxImportFormat = fbxSubnet.getFbxFilesList(directoryPath)[0]
        self.fbxImportFormat = fbxImportFormat

        # List of tree subnet folder names
        fbxDirNames = list(fbxImportFormat.keys())
        # Set row count on table
        self.ui.tableOfFoldersOnDisk.setRowCount(len(fbxDirNames))

        # If no folders containing fbxs were found
        if len(fbxDirNames) == 0:
            # TODO add button functionality
            ok = self.messageBox(self.directoryPath)

        # Populate table
        for importIndex in range(0, len(fbxDirNames)):
            # First item is tree folder name
            treeDirName = QtWidgets.QTableWidgetItem(fbxDirNames[importIndex])
            self.ui.tableOfFoldersOnDisk.setItem(importIndex, 0, treeDirName)
            # Second item is number of .fbx files in folder
            numFbxPaths = len(fbxImportFormat[fbxDirNames[importIndex]])
            if numFbxPaths < 2:
                fbxFoundMsg = "{NUMOFITEMS} fbx found".format(NUMOFITEMS=numFbxPaths)
            else:
                fbxFoundMsg = "{NUMOFITEMS} fbxs found".format(NUMOFITEMS=numFbxPaths)
            fbxFoundMsgObj = QtWidgets.QTableWidgetItem(fbxFoundMsg)
            self.ui.tableOfFoldersOnDisk.setItem(importIndex, 1, fbxFoundMsgObj)
            # Third item is message
            messageStr = "default message"
            messageObj = QtWidgets.QTableWidgetItem(messageStr)
            self.ui.tableOfFoldersOnDisk.setItem(importIndex, 2, messageObj)

    # TODO this updates when directoryPath is editted by text
    def updateTreeDirTable(self):
        self.populateTreeDirTable(self.directoryPath)

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
        self.fileAction = QtWidgets.QAction("Clear Table")
        self.fileAction.triggered.connect(self.reformatClearedTable)
        menu.addAction(self.fileAction)
        menu.exec_(self.ui.tableOfFoldersOnDisk.viewport().mapToGlobal(pos))

    def reformatClearedTable(self):
        """ Clears all rows but keeps columns in a table widget """
        self.ui.tableOfFoldersOnDisk.clearContents()
        # Clears rows
        self.ui.tableOfFoldersOnDisk.setRowCount(0)

        # Revisualize tree subnets table
        self.visualizeTreeSubnetTable()

    def populateTreeSubnetTable(self):
        """ Detects tree subnets in scene and populates table """
        obj = hou.node("/obj")
        # Clear contents and rows
        self.ui.tableOfTreeSubnets.clearContents()
        self.ui.tableOfTreeSubnets.setRowCount(0)

        # Get nodes in obj with createState == "SpeedTree Asset Generator by Daniel"
        generatedNodes = []
        for node in obj.children():
            if node.creatorState() == "SpeedTree Asset Generator by Daniel":
                generatedNodes.append(node)

        # If no generated nodes are detected
        if not generatedNodes:
            self.ui.tableOfTreeSubnets.setRowCount(1)

            noneMsgObj1 = QtWidgets.QTableWidgetItem("None")
            noneMsgObj1.setForeground(QtCore.Qt.red)
            noneMsgObj2 = QtWidgets.QTableWidgetItem("None")
            noneMsgObj2.setForeground(QtCore.Qt.red)
            self.ui.tableOfTreeSubnets.setItem(0, 0, noneMsgObj1)
            self.ui.tableOfTreeSubnets.setItem(0, 1, noneMsgObj2)

            noSubnetsMessage = "No Tree Subnets Detected."
            noSubnetsMessageObj = QtWidgets.QTableWidgetItem(noSubnetsMessage)
            noSubnetsMessageObj.setForeground(QtCore.Qt.red)
            self.ui.tableOfTreeSubnets.setItem(0, 2, noSubnetsMessageObj)
            return

        # Generate rows
        self.ui.tableOfTreeSubnets.setRowCount(len(generatedNodes))
        for nodeIndex in range(0, len(generatedNodes)):
            node = generatedNodes[nodeIndex]
            # First item is tree subnet name
            generatedNodeNameObj = QtWidgets.QTableWidgetItem(node.name())
            self.ui.tableOfTreeSubnets.setItem(nodeIndex, 0, generatedNodeNameObj)
            # Second item is number of geos
            geoCount = len([geo for geo in node.children() if geo.type().name() == "geo"])
            countStr = "{COUNT} geos found".format(COUNT=geoCount)
            geoCountObj = QtWidgets.QTableWidgetItem(countStr)
            self.ui.tableOfTreeSubnets.setItem(nodeIndex, 1, geoCountObj)
            # Third item is message
            messageStr = "This subnet exists in scene.".format()
            messageObj = QtWidgets.QTableWidgetItem(messageStr)
            self.ui.tableOfTreeSubnets.setItem(nodeIndex, 2, messageObj)

    def getTableContents(self, uiTable):
        """ Get nested list of the uiTable object provided """
        rowCount = uiTable.rowCount()
        colCount = uiTable.columnCount()

        tableContents = OrderedDict()
        for rowIndex in range(0, rowCount):
            colContent = []
            for colIndex in range(1, colCount):
                colContent.append(uiTable.item(rowIndex, colIndex).text())

            treeKey = uiTable.item(rowIndex, 0).text()
            tableContents[treeKey] = colContent

        return tableContents

    def visualizeTreeDirTable(self):
        """ Updates messages according to fbxs detected. Changes row colors. """
        tableOfFoldersOnDiskContents = self.getTableContents(self.ui.tableOfFoldersOnDisk)
        tableOfTreeSubnetsContents = self.getTableContents(self.ui.tableOfTreeSubnets)

        currentRow = 0
        for treeKey, valueList in tableOfFoldersOnDiskContents.items():
            newColor = False
            # If it is a new tree
            if not treeKey in tableOfTreeSubnetsContents.keys():
                subnetMsg = "New tree detected."
                newColor = QtCore.Qt.green

            # If it already exists in scene
            else:
                subnetMsg = "Tree subnet detected in scene."
                # Check if fbx count is different
                tableDirFbxText = tableOfFoldersOnDiskContents[treeKey][0]
                tableTreeSubnetFbxText = tableOfTreeSubnetsContents[treeKey][0]
                if tableDirFbxText[0] != tableTreeSubnetFbxText[0]:
                    subnetMsg = "Fbx count is different from scene. Consider reimporting."
                    newColor = QtCore.Qt.yellow

            # Update Message
            subnetMsgObj = QtWidgets.QTableWidgetItem(subnetMsg)
            self.ui.tableOfFoldersOnDisk.setItem(currentRow, 2, subnetMsgObj)
            # Update color
            if newColor:
                for col in range(0, 3):
                    tableItem = self.ui.tableOfFoldersOnDisk.item(currentRow, col)
                    tableItem.setForeground(newColor)

            currentRow += 1

    def visualizeTreeSubnetTable(self):
        """ Updates messages according to fbxs detected. Changes row colors. """
        tableOfFoldersOnDiskContents = self.getTableContents(self.ui.tableOfFoldersOnDisk)
        tableOfTreeSubnetsContents = self.getTableContents(self.ui.tableOfTreeSubnets)

        if len(tableOfFoldersOnDiskContents) == 0:
            self.populateTreeSubnetTable()
            return

        currentRow = 0
        for treeKey, valueList in tableOfTreeSubnetsContents.items():
            # If it is a new tree
            if treeKey in tableOfFoldersOnDiskContents.keys():
                newColor = False
                subnetMsg = None
                # Check if fbx count is different
                tableDirFbxText = tableOfFoldersOnDiskContents[treeKey][0]
                tableTreeSubnetFbxText = tableOfTreeSubnetsContents[treeKey][0]
                if tableDirFbxText[0] != tableTreeSubnetFbxText[0]:
                    subnetMsg = "Fbx count is different from scene. Consider reimporting."
                    newColor = QtCore.Qt.yellow

                # Update Message
                if subnetMsg:
                    subnetMsgObj = QtWidgets.QTableWidgetItem(subnetMsg)
                    self.ui.tableOfTreeSubnets.setItem(currentRow, 2, subnetMsgObj)
                # Update color
                if newColor:
                    for col in range(0, 3):
                        tableItem = self.ui.tableOfTreeSubnets.item(currentRow, col)
                        tableItem.setForeground(newColor)

                currentRow += 1

    def confirmationBox(self, dir):
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

    def testFunc(self):
        tableOfFoldersOnDiskContents = self.getTableContents(self.ui.tableOfFoldersOnDisk)
        allTreeKeysFromTable = list(tableOfFoldersOnDiskContents)
        rowItems = self.ui.tableOfFoldersOnDisk.selectionModel().selectedRows()

        print("only import selected: " + str(self.ui.onlyImportSelectedFolders.isChecked()))

        # List of tree keys to import
        itemsToImport = []
        if self.ui.onlyImportSelectedFolders.isChecked():
            for rowItem in rowItems:
                rowIndex = rowItem.row()
                itemsToImport.append(allTreeKeysFromTable[rowIndex])
        else:
            fbxImportFormat = fbxSubnet.getFbxFilesList(self.directoryPath)[0]
            itemsToImport = fbxImportFormat.keys()

        # Get fbx formatted dictionary for all items in directory path
        fbxImportFormat = fbxSubnet.getFbxFilesList(self.directoryPath)[0]

        # Only use items in items to import list
        treeDicttoImport = dict()
        for item in itemsToImport:
            treeDicttoImport[item] = fbxImportFormat[item]

        reimportExisting = self.ui.reimportExistingTreeSubnets.isChecked()
        convertToYup = self.ui.convertToYup.isChecked()

        treeSubnetsFromDir = execute.treeSubnetsFromDir(treeDicttoImport,
                                                        reimportExisting=reimportExisting,
                                                        convertToYup=convertToYup)

        resetTransforms = self.ui.resetTransformations.isChecked()
        matchSize = self.ui.matchSize.isChecked()

        execute.treeSubnetsReformat(treeSubnetsFromDir,
                                    resetTransforms=resetTransforms,
                                    matchSize=matchSize)





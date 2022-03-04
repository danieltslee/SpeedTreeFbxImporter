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

        # Updating tree subnet table after browsing
        self.visualizeTreeSubnetTable()
        self.visualizeTreeDirTable()

    def populateTreeDirTable(self, directoryPath):
        """ Tree directory table from directoryPath """
        # Get formatted dictionary
        fbxImportFormat = fbxSubnet.getFbxFilesList(directoryPath)[0]

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

            noSubnetsMessage = "No Tree Subnets Detected"
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
            messageStr = "This subnet exists in scene".format()
            messageObj = QtWidgets.QTableWidgetItem(messageStr)
            self.ui.tableOfTreeSubnets.setItem(nodeIndex, 2, messageObj)

    def getTableContents(self, uiTable):
        """ Get nested list of the uiTable object provided """
        rowCount = uiTable.rowCount()
        colCount = uiTable.columnCount()

        tableContents = []
        for rowIndex in range(0, rowCount):
            colContent = []
            for colIndex in range(0, colCount):
                colContent.append(uiTable.item(rowIndex, colIndex).text())

            tableContents.append(colContent)
        return tableContents

    def visualizeTreeDirTable(self):
        rowCount = self.ui.tableOfFoldersOnDisk.rowCount()
        colCount = self.ui.tableOfFoldersOnDisk.columnCount()
        print(str(rowCount) + " rows")
        print(str(colCount) + " columns")

    def visualizeTreeSubnetTable(self):
        print("Tree Subnet Table Updates Here")

    def testFunc(self):
        tableOfFoldersOnDiskContents = self.getTableContents(self.ui.tableOfFoldersOnDisk)
        tableOfTreeSubnetsContents = self.getTableContents(self.ui.tableOfTreeSubnets)
        tableOfFoldersOnDiskFirst = [item[0] for item in tableOfFoldersOnDiskContents]
        tableOfTreeSubnetsFirst = [item[0] for item in tableOfTreeSubnetsContents]

        newTreeFolders = [item for item in tableOfFoldersOnDiskFirst if item not in tableOfTreeSubnetsFirst]

        print(newTreeFolders)

        newTreeIndex = [tableOfFoldersOnDiskFirst.index(item) for item in newTreeFolders]

        print(newTreeIndex)

        newSubnetMsg = "New tree detected. This will be imported."
        for index in newTreeIndex:
            newSubnetMsgObj = QtWidgets.QTableWidgetItem(newSubnetMsg)
            newSubnetMsgObj.setForeground(QtCore.Qt.green)
            self.ui.tableOfFoldersOnDisk.setItem(index, 2, newSubnetMsgObj)




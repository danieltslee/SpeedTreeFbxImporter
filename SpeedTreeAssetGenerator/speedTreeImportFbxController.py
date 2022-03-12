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

        # Set menu policy for right click menu
        self.ui.tableOfFoldersOnDisk.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tableOfTreeSubnets.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # Select model is rows only
        self.ui.tableOfFoldersOnDisk.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.ui.tableOfTreeSubnets.setSelectionBehavior(QtWidgets.QTableView.SelectRows)

        # Format table of trees in dir
        self.formatColumnWidth(self.ui.tableOfFoldersOnDisk)

        # Detect tree subnets in scene
        self.populateTreeSubnetTable()
        self.visualizeTreeSubnetTable()

        # fbx import formatted dictionary
        self.fbxImportFormat = dict()

        # Signal
        self.signals()

    def signals(self):
        self.ui.launchBrowser.pressed.connect(partial(self.launchTreeDirectoryBrowser))
        # Right click menu table of fbxs in dir
        self.ui.tableOfFoldersOnDisk.customContextMenuRequested.connect(self.tableRightClickMenuDIR)
        # Right click menu table of tree subnets in scene
        self.ui.tableOfTreeSubnets.customContextMenuRequested.connect(self.tableRightClickMenuSCENE)

        # Refresh Tables Button
        self.ui.refreshTables.pressed.connect(partial(self.refreshTablesButton))

        # Import Fbx Button
        self.ui.importFbxExecute.pressed.connect(partial(self.exeImportFbx))

        # Enter pressed on directory path line edit
        self.ui.directoryPath.returnPressed.connect(self.directoryPathEnter)

        # Detect when checkbox is clicked
        self.ui.reimportExistingSubnets.toggled.connect(self.onReimportExistingSubnetsClicked)

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
            messageStr = "Tree subnet exists in scene."
            messageObj = QtWidgets.QTableWidgetItem(messageStr)
            self.ui.tableOfFoldersOnDisk.setItem(importIndex, 2, messageObj)

        # Column width
        self.formatColumnWidth(self.ui.tableOfFoldersOnDisk)

    def directoryPathEnter(self):
        # Set directory path to new input
        self.directoryPath = self.ui.directoryPath.text()
        path = self.directoryPath
        # If invalid path, then return
        if not os.path.isdir(path):
            self.invalidPathBox()
            return

        # Refresh Tables
        self.refreshTablesButton()
        # Reformat Table
        # self.clearTableAction(self.ui.tableOfFoldersOnDisk)

        self.populateTreeDirTable(self.directoryPath)
        # Visualise Tables
        self.visualizeTreeDirTable()
        self.visualizeTreeSubnetTable()

    def invalidPathBox(self):
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Information)
        dialog.setWindowTitle("Error: Invalid Path Entered")
        dialog.setText("Invalid path entered. Please enter a valid path "
                       "or browse to directory.")

        dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        dialog.setDefaultButton(QtWidgets.QMessageBox.Yes)

        ret = dialog.exec_()

        if ret == dialog.Ok:
            return True
        else:
            return False

    def messageBox(self, dir):
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Information)
        dialog.setWindowTitle("Error: No fbx Files Found")
        dialog.setText("No fbxs found in {DIR}".format(DIR=dir))

        #dialog.setStandardButtons(QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
        dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        dialog.setDefaultButton(QtWidgets.QMessageBox.Yes)

        ret = dialog.exec_()

        if ret == dialog.Ok:
            return True
        else:
            return False

    def tableRightClickMenuDIR(self, pos):
        """ Right Click Menu for tableOfFoldersOnDisk """
        # Initialize Menu
        menu = QtWidgets.QMenu()

        # Clear table action
        clearTable = QtWidgets.QAction("Clear Table")
        clearTable.triggered.connect(lambda: self.clearTableAction(self.ui.tableOfFoldersOnDisk))
        menu.addAction(clearTable)

        # Select all action
        selectAllRows = QtWidgets.QAction("Select All")
        selectAllRows.triggered.connect(lambda: self.selectAllAction(self.ui.tableOfFoldersOnDisk))
        menu.addAction(selectAllRows)

        # Clear selection action
        clearSelection = QtWidgets.QAction("Clear Selection")
        clearSelection.triggered.connect(lambda: self.clearSelectionAction(self.ui.tableOfFoldersOnDisk))
        menu.addAction(clearSelection)

        menu.exec_(self.ui.tableOfFoldersOnDisk.viewport().mapToGlobal(pos))

    def tableRightClickMenuSCENE(self, pos):
        """ Right Click Menu for tableOfTreeSubnets """
        # Initialize Menu
        menu = QtWidgets.QMenu()

        # Select all action
        selectAllRows = QtWidgets.QAction("Select All")
        f = lambda: self.selectAllAction(self.ui.tableOfTreeSubnets)
        selectAllRows.triggered.connect(f)
        menu.addAction(selectAllRows)

        # Clear selection action
        clearSelection = QtWidgets.QAction("Clear Selection")
        clearSelection.triggered.connect(lambda: self.clearSelectionAction(self.ui.tableOfTreeSubnets))
        menu.addAction(clearSelection)

        menu.exec_(self.ui.tableOfTreeSubnets.viewport().mapToGlobal(pos))

    # TODO ADDED RIGHT CLICK FUNC DOESN'T WORK FOR NOW
    def formatRightClickAction(self, title, actionFunc, uiTable, menu):
        def simpleAdd(menu, action):
            menu.addAction(action)
        action = QtWidgets.QAction(title)
        f = lambda: actionFunc(uiTable)
        action.triggered.connect(f)
        simpleAdd(menu, action)
        return action

    def clearTableAction(self, uiTable):
        """ Clears all rows but keeps columns in a table widget """
        uiTable.clearContents()
        # Clear rows
        uiTable.setRowCount(0)

        # Revisualize tree subnets table
        self.visualizeTreeSubnetTable()

    def selectAllAction(self, uiTable):
        uiTable.selectAll()

    def clearSelectionAction(self, uiTable):
        uiTable.clearSelection()

    def refreshTablesButton(self):
        subnetsExists = self.populateTreeSubnetTable()
        if subnetsExists:
            self.visualizeTreeSubnetTable()
        self.directoryPath = self.ui.directoryPath.text()
        self.populateTreeDirTable(self.directoryPath)
        self.visualizeTreeDirTable()

    def populateTreeSubnetTable(self):
        """ Detects tree subnets in scene and populates table. Returns True if there are contents. """
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

            self.ui.tableOfTreeSubnets.setSpan(0, 0, 1, 3)
            noneMsgObj = QtWidgets.QTableWidgetItem("No Tree Subnets Detected.")
            noneMsgObj.setTextAlignment(QtCore.Qt.AlignCenter)
            noneMsgObj.setForeground(QtCore.Qt.red)
            self.ui.tableOfTreeSubnets.setItem(0, 0, noneMsgObj)
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
            messageStr = "Tree subnet exists in scene.".format()
            messageObj = QtWidgets.QTableWidgetItem(messageStr)
            self.ui.tableOfTreeSubnets.setItem(nodeIndex, 2, messageObj)

        # Column width
        self.formatColumnWidth(self.ui.tableOfTreeSubnets)

        return True

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
        # Only get tree subnet contents if not empty at first
        if not self.ui.tableOfTreeSubnets.item(0, 1):
            tableOfTreeSubnetsContents = OrderedDict()
        else:
            tableOfTreeSubnetsContents = self.getTableContents(self.ui.tableOfTreeSubnets)

        currentRow = 0
        for treeKey, valueList in tableOfFoldersOnDiskContents.items():
            subnetMsg = None
            newColor = QtCore.Qt.lightGray  # Default Color
            # If it is a new tree
            if treeKey not in tableOfTreeSubnetsContents.keys():
                subnetMsg = "New tree detected."
            #  If tree subnet detected in scene
            else:
                # Check if fbx count is different
                tableDirFbxText = tableOfFoldersOnDiskContents[treeKey][0]
                tableTreeSubnetFbxText = tableOfTreeSubnetsContents[treeKey][0]
                if tableDirFbxText[0] != tableTreeSubnetFbxText[0]:
                    subnetMsg = str(subnetMsg or "") + "Fbx count is different from scene. "
                # Check if matnet is formatted correctly
                subnetMsg = str(subnetMsg or "") + self.checkMatnetFormat(treeKey)

            # Update Message and color if subnetMsg has error
            if subnetMsg == "New tree detected.":  # If new tree detected
                subnetMsgObj = QtWidgets.QTableWidgetItem(subnetMsg)
                newColor = QtCore.Qt.green
            elif subnetMsg:  # If subnet has error
                subnetMsgObj = QtWidgets.QTableWidgetItem(subnetMsg + "Consider reimporting.")
                newColor = QtCore.Qt.yellow
            else:  # if tree exists in scene and no error
                subnetMsgObj = QtWidgets.QTableWidgetItem("Tree subnet exists in scene.")

            # Update mesage
            self.ui.tableOfFoldersOnDisk.setItem(currentRow, 2, subnetMsgObj)
            # Update color
            for col in range(0, 3):
                tableItem = self.ui.tableOfFoldersOnDisk.item(currentRow, col)
                tableItem.setForeground(newColor)

            currentRow += 1

        # Column width
        self.formatColumnWidth(self.ui.tableOfFoldersOnDisk)

    def visualizeTreeSubnetTable(self):
        """ Updates messages according to fbxs detected. Changes row colors. """
        tableOfFoldersOnDiskContents = self.getTableContents(self.ui.tableOfFoldersOnDisk)
        # Only get tree subnet contents if not empty at first
        if not self.ui.tableOfTreeSubnets.item(0, 1):
            tableOfTreeSubnetsContents = OrderedDict()
        else:
            tableOfTreeSubnetsContents = self.getTableContents(self.ui.tableOfTreeSubnets)

        # Check fbx count to geo count
        currentRow = 0
        for treeKey, valueList in tableOfTreeSubnetsContents.items():
            # Default color
            newColor = QtCore.Qt.lightGray
            subnetMsg = None
            # If it is a new tree
            if treeKey in tableOfFoldersOnDiskContents.keys():
                # Check if fbx count is different
                tableDirFbxText = tableOfFoldersOnDiskContents[treeKey][0]
                tableTreeSubnetFbxText = tableOfTreeSubnetsContents[treeKey][0]
                if tableDirFbxText[0] != tableTreeSubnetFbxText[0]:
                    subnetMsg = str(subnetMsg or "") + "Fbx count is different from scene. "

            # Check if matnet is formatted correctly
            subnetMsg = str(subnetMsg or "") + self.checkMatnetFormat(treeKey)

            # Update Message
            if subnetMsg:
                subnetMsgObj = QtWidgets.QTableWidgetItem(subnetMsg + "Consider reimporting.")
                self.ui.tableOfTreeSubnets.setItem(currentRow, 2, subnetMsgObj)
                newColor = QtCore.Qt.yellow
            for col in range(0, 3):
                tableItem = self.ui.tableOfTreeSubnets.item(currentRow, col)
                tableItem.setForeground(newColor)

            currentRow += 1

        # Column width
        self.formatColumnWidth(self.ui.tableOfTreeSubnets)

    def formatColumnWidth(self, uiTable):
        """ Streches 3rd column in table """
        header = uiTable.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

    def checkMatnetFormat(self, treeKey):
        treeSubnet = hou.node("/obj/{TREEKEY}".format(TREEKEY=treeKey))
        matnet = None
        msg = ""
        for child in treeSubnet.children():
            if child.type().name() == "matnet":
                matnet = child
        if not matnet:  # If matnet does not exist
            msg = "Matnet does not exist. "
        elif matnet.name() != "{TREEKEY}_matnet".format(TREEKEY=treeKey):
            msg = "Matnet may not be correctly formatted. "
        return msg

    def onReimportExistingSubnetsClicked(self):
        """ Enable/Disable the drop down combo box according to reimport existing subnet check box """
        state = self.ui.reimportExistingSubnets.isChecked()
        self.ui.reimportOptions.setEnabled(state)

    def noTreesInTableBox(self):
        """ Message for if trees in Directory table is empty """
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Information)

        dialog.setWindowTitle("Error: No Directory Specified")
        dialog.setText("Please enter a valid path or browse to directory.")

        dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        dialog.setDefaultButton(QtWidgets.QMessageBox.Yes)

        ret = dialog.exec_()

        if ret == dialog.Ok:
            return True
        else:
            return False

    def noSelectionBox(self):
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Information)

        title = "Info: No Trees Selected"
        message = "No trees Selected. Please select items to import or " \
                  "uncheck '"'Only Import Selected Folders'"'."

        dialog.setWindowTitle(title)
        dialog.setText(message)

        dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        dialog.setDefaultButton(QtWidgets.QMessageBox.Yes)

        ret = dialog.exec_()

        if ret == dialog.Ok:
            return True
        else:
            return False

    def confirmationBox(self, treeDicttoImport):
        """ Message Box for confirmation when import fbx button is executed """
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Information)

        if treeDicttoImport:
            title = "Confirm: Proceed With Fbx Import?"
            treeKeyList = list(treeDicttoImport.keys())
            if len(treeDicttoImport) > 1:
                countTxt = "Subnets"
                message = "{COUNTTXT} to import: " \
                          "{JOIN1}, and {JOIN2}.".format(COUNTTXT=countTxt,
                                                         JOIN1=", ".join(treeKeyList[:-1]),
                                                         JOIN2=treeKeyList[-1])
            else:
                countTxt = "Subnet"
                message = "{COUNTTXT} to import: " \
                          "{JOIN1}.".format(COUNTTXT=countTxt, JOIN1=treeKeyList[0])

        dialog.setWindowTitle(title)
        dialog.setText(message)

        dialog.setStandardButtons(QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
        dialog.setDefaultButton(QtWidgets.QMessageBox.Yes)

        ret = dialog.exec_()

        if ret == dialog.Ok:
            return True
        else:
            return False

    def formatTreeDictToImport(self):
        """ Format dictionary to import fbx.
         Ex:{"BostonFern": [path/to/geo1.fbx, path/to/geo2.fbx]} """
        tableOfFoldersOnDiskContents = self.getTableContents(self.ui.tableOfFoldersOnDisk)
        allTreeKeysFromTable = list(tableOfFoldersOnDiskContents.keys())
        rowItems = self.ui.tableOfFoldersOnDisk.selectionModel().selectedRows()

        # Message Box: If nothing in table from directory
        if not tableOfFoldersOnDiskContents:
            self.noTreesInTableBox()
            return

        # List of tree keys to import. Ex: ["BostonFern", "AmericanElm", "BananaPlant]
        itemsToImport = []

        # Check if only import selected folders is checked
        if self.ui.onlyImportSelectedFolders.isChecked():
            # Check if nothing is selected while "only import selected folders" is checked
            if len(rowItems) == 0:
                self.noSelectionBox()
                return
            for rowItem in rowItems:
                rowIndex = rowItem.row()
                itemsToImport.append(allTreeKeysFromTable[rowIndex])
        else:
            fbxImportFormat = fbxSubnet.getFbxFilesList(self.directoryPath)[0]
            itemsToImport = list(fbxImportFormat.keys())

        # If reimport existing tree subnets is checked, only remove specified from list
        if self.ui.reimportExistingSubnets.isChecked():
            if self.ui.reimportOptions.currentIndex() == 0:  # All existing subnets
                pass
            elif self.ui.reimportOptions.currentIndex() == 1:  # Recommended Subnets Only
                # Remove from list, subnets that are fine
                for rowIndex in range(0, self.ui.tableOfTreeSubnets.rowCount()):
                    cd = self.ui.tableOfTreeSubnets.item(rowIndex, 0).foreground().color().name()
                    treeSubnetName = self.ui.tableOfTreeSubnets.item(rowIndex, 0).text()
                    if cd == "#c0c0c0" and treeSubnetName in itemsToImport:  # '#c0c0c0' is lightGray
                        itemsToImport.remove(treeSubnetName)
        else:  # If reimport existing tree subnets is unchecked, remove subnets from list
            for rowIndex in range(0, self.ui.tableOfTreeSubnets.rowCount()):
                treeSubnetName = self.ui.tableOfTreeSubnets.item(rowIndex, 0).text()
                if treeSubnetName in itemsToImport:
                    itemsToImport.remove(treeSubnetName)

        # If itemsToImport is empty after removing existing subnets, meaning all subnets already in scene
        # message box and exit. Do not move on to import format dict phase
        if not itemsToImport:
            self.treesAlreadyImportedBox()
            return

        # Get fbx formatted dictionary for all items in directory path
        fbxImportFormat = fbxSubnet.getFbxFilesList(self.directoryPath)[0]

        # Only use items in items to import list
        treeDicttoImport = dict()
        for item in itemsToImport:
            treeDicttoImport[item] = fbxImportFormat[item]

        return treeDicttoImport

    def treesAlreadyImportedBox(self):
        """ Message Box for confirmation when import fbx button is executed """
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Information)

        dialog.setWindowTitle("Info: Trees Already in Scene")
        dialog.setText("Specified trees already exists in scene. "
                       "Check '"'Reimport Existing Subnets'"' or "
                       "import new trees.")

        dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        dialog.setDefaultButton(QtWidgets.QMessageBox.Yes)

        ret = dialog.exec_()

        if ret == dialog.Ok:
            return True
        else:
            return False

    def exeImportFbx(self):
        """ Press Import Fbx button """
        treeDicttoImport = self.formatTreeDictToImport()
        # Quit if empty dict
        if not treeDicttoImport:
            return

        # Message Box: Import Fbx confirmation
        confirmToImport = self.confirmationBox(treeDicttoImport)
        if not confirmToImport:
            return

        convertToYup = self.ui.convertToYup.isChecked()
        treeSubnetsFromDir = execute.treeSubnetsFromDir(treeDicttoImport,
                                                        convertToYup=convertToYup)

        # Check reset transformations and match size
        resetTransforms = self.ui.resetTransformations.isChecked()
        matchSize = self.ui.matchSize.isChecked()
        genRsMatandAssign = self.ui.genRsMatandAssign.isChecked()
        execute.treeSubnetsReformat(treeSubnetsFromDir,
                                    resetTransforms=resetTransforms,
                                    matchSize=matchSize,
                                    genRsMatandAssign=genRsMatandAssign)

        # Reset tables and visualizations
        self.populateTreeSubnetTable()
        self.visualizeTreeSubnetTable()
        self.visualizeTreeDirTable()



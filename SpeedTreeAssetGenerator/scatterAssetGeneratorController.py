import hou
import os
from PySide2 import QtCore, QtUiTools, QtWidgets
from functools import partial

class ScatterAssetGenerator(QtWidgets.QWidget):

    def __init__(self):
        super(ScatterAssetGenerator, self).__init__()
        #ui_file = 'Z:\houdini19.0\python3.7libs\SpeedTreeAssetGenerator\scatterAssetGeneratorUI_v02.ui'

        parentDir = os.path.split(__file__)[0]
        directoryContent = os.listdir(parentDir)
        for content in directoryContent:
            if content == 'scatterAssetGeneratorUI_v02.ui':
                ui_file = os.path.join(parentDir, content)
                self.ui = QtUiTools.QUiLoader().load(ui_file)
                self.layout = QtWidgets.QVBoxLayout(self)
                self.layout.addWidget(self.ui)
                self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        self.signals()

    def signals(self):
        self.ui.buttonSelectTreeSubnets.pressed.connect(partial(self.selectTreeSubnets))

    def selectTreeSubnets(self):
        self.ui.listOfTreeSubnets.clear()
        multipleSelections = hou.ui.selectMultipleNodes()
        for selection in multipleSelections:
            item = QtWidgets.QListWidgetItem(selection)
            self.ui.listOfTreeSubnets.addItem(item)


import hou
from PySide2 import QtCore, QtUiTools, QtWidgets


class SpeedTreeFbxImporter(QtWidgets.QWidget):

    def __init__(self):
        super(SpeedTreeFbxImporter, self).__init__()
        ui_file = 'Z:\houdini19.0\python3.7libs\SpeedTreeAssetGenerator\SpeedTreeImportFbxUI.ui'
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.ui)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)


class scatterAssetGenerator(QtWidgets.QWidget):

    def __init__(self):
        super(scatterAssetGenerator, self).__init__()
        ui_file = 'Z:\houdini19.0\python3.7libs\SpeedTreeAssetGenerator\scatterAssetGeneratorUI_v02.ui'
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.ui)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)



"""
PUT THIS IN A SHELF BUTTON IN HOUDINI
import SpeedTreeAssetGenerator as stag
import importlib

importlib.reload(stag)

win = stag.launch.SpeedTreeFbxImporter()
win.show()

"""


"""
test python file
"""

import hou
from . import fbxSubnetFormat

def myFunc():
    print("I am scripting in houdini 18.5. try #6")
    #obj = hou.node("/obj")
    #obj.createNode("geo", "myPycharmGeo")

    list1 = range(5)
    list2 = ["one", "two", "three", "four", "five"]

    print("myFunc executed")


def exe():

    # Get hip directory path
    hipPath = hou.hipFile.path()
    hipBaseName = hou.hipFile.basename()
    hipDir = hipPath.replace(hipBaseName, "")

    fbxImportFormat = getFbxFilesList("{HIPDIR}assets/myTrees/Acacia".format(HIPDIR=hipDir))

    # Import fbx
    for key in fbxImportFormat:
        subnetName = key
        fbxFilePaths = fbxImportFormat[key]
        treeSubnet = importSpeedTreeFbx(fbxFilePaths, subnetName)
        treeSubnet, matnetName = fbxSubnetFormat.AssignMaterials(treeSubnet)

        fbxSubnetFormat.createMatnet(treeSubnet, matnetName)


if __name__ == "__main__":
    myFunc()



"""
test python file
"""

import hou
from . import fbxSubnet
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

    fbxImportFormat = fbxSubnet.getFbxFilesList("{HIPDIR}assets/myTrees/stagTest".format(HIPDIR=hipDir))[0]

    # Import fbx
    generatedTreeSubnets = []
    for key in fbxImportFormat:
        subnetName = key
        fbxFilePaths = fbxImportFormat[key]
        treeSubnet = fbxSubnet.importSpeedTreeFbx(fbxFilePaths, subnetName)
        # Create Matnet
        matnetName = subnetName + "_matnet"
        treeSubnet = fbxSubnetFormat.createMatnet(treeSubnet, matnetName)
        print("Materials Created for: " + treeSubnet.name())
        # Create Material Assignments
        treeSubnet = fbxSubnetFormat.AssignMaterials(treeSubnet, matnetName)
        print("Created MaterialAssignments for: " + treeSubnet.name())
        print("\n")

        generatedTreeSubnets.append(treeSubnet)

    # Layout tree subnets
    obj = hou.node("/obj")
    obj.layoutChildren(tuple(generatedTreeSubnets), vertical_spacing=0.35)

if __name__ == "__main__":
    myFunc()



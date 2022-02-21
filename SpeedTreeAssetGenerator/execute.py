"""
Execution functions
"""

import hou
from . import fbxSubnet
from . import fbxSubnetFormat
from . import treeScatterSubnet


def generateTreeSubnets():
    # Get hip directory path
    hipPath = hou.hipFile.path()
    hipBaseName = hou.hipFile.basename()
    hipDir = hipPath.replace(hipBaseName, "")

    fbxImportFormat, fbxFilePaths, fbxFileDirs = \
        fbxSubnet.getFbxFilesList("{HIPDIR}assets/myTrees/stagTest".format(HIPDIR=hipDir))

    # Import fbx
    generatedTreeSubnets = []
    for key in fbxImportFormat:
        subnetName = key
        fbxFilePaths = fbxImportFormat[key]
        treeSubnet, actionMessage = fbxSubnet.importSpeedTreeFbx(fbxFilePaths, subnetName)
        print("\n{MSG}".format(MSG=actionMessage))
        # Create Matnet
        matnetName = subnetName + "_matnet"
        treeSubnet = fbxSubnetFormat.createMatnet(treeSubnet, matnetName)
        print("Materials Created for: " + treeSubnet.name())
        # Create Material Assignments
        treeSubnet = fbxSubnetFormat.AssignMaterials(treeSubnet, matnetName)
        print("Created MaterialAssignments for: " + treeSubnet.name())

        generatedTreeSubnets.append(treeSubnet)

    # Layout tree subnets
    if actionMessage.split()[0] == "Created":
        obj = hou.node("/obj")
        obj.layoutChildren(tuple(generatedTreeSubnets), vertical_spacing=0.35)


def generateScatterSubnets(treeSubnet, hfGeoNode):
    """
    Generate tree scatter subnet
    :param treeSubnet: Tree subnet hou.node object from which the scatter subnet will be generated
    :param hfGeoNode: hou.node in which the scatter subnet will be placed
    :return: hou.node tree scatter subnet
    """
    scatterSubnet, actionMessage = treeScatterSubnet.createTreeScatterSubnet(treeSubnet, hfGeoNode)
    print(actionMessage)

    return scatterSubnet

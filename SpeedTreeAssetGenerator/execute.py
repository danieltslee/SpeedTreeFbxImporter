"""
Execution functions
"""

import hou
from . import fbxSubnet
from . import fbxSubnetFormat
from . import treeScatterSubnet
from . import redshiftProxy
from pathlib import Path


def generateTreeSubnets(directory):

    fbxImportFormat, fbxFilePaths, fbxFileDirs = fbxSubnet.getFbxFilesList(directory)

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

    return generatedTreeSubnets


def generateScatterSubnets(treeSubnet, hfGeoNode):
    """
    Generate tree scatter subnet in specified node/context
    :param treeSubnet: Tree subnet hou.node object from which the scatter subnet will be generated
    :param hfGeoNode: hou.node in which the scatter subnet will be placed
    :return: hou.node tree scatter subnet
    """
    scatterSubnet, actionMessage = treeScatterSubnet.createTreeScatterSubnet(treeSubnet, hfGeoNode)
    print(actionMessage)

    return scatterSubnet


def generateRedshiftProxy(treeSubnets, rsFolder):
    """
    Create Redshift proxy files for all geometry nodes in a specified tree subnet.
    :param treeSubnet: tuple of hou.node tree subnets
    :param rsFolder: file directory in which the rs proxy files will be generated
    :return: None
    """
    # Format directory path
    rsFolder = Path(rsFolder)
    print(rsFolder)

    for treeSubnet in treeSubnets:
        redshiftProxy.createRedshiftProxy(treeSubnet, rsFolder)
        print("Created Redshift Proxy files for {TREE}".format(TREE=treeSubnet.name()))


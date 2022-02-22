"""
Execution functions
"""

import hou
from . import fbxSubnet
from . import fbxSubnetFormat
from . import treeScatterSubnet
from . import redshiftProxy
from pathlib import Path


def treeSubnetsFromDir(directory):
    """
    Creates subnets from directory. One subnet will be created for each folder containing fbxs
    :param directory: Folder which contains folders or subfolders containing the fbx files
    :return: List of hou.node tree subnet objects generated fron directory
    """
    obj = hou.node("/obj")

    # Get fbx directory
    fbxImportFormat, fbxFilePaths, fbxFileDirs = fbxSubnet.getFbxFilesList(directory)

    treeSubnetsFromDir = []
    createdTreeSubnets = []
    for key in fbxImportFormat:
        # Import fbx
        subnetName = key
        fbxFilePaths = fbxImportFormat[key]
        treeSubnet, actionMessage = fbxSubnet.importSpeedTreeFbx(subnetName, fbxFilePaths)
        print("{MSG}".format(MSG=actionMessage))

        # Store Created Tree Subnets in list
        if actionMessage.split()[0] == "Created":
            createdTreeSubnets.append(treeSubnet)

        treeSubnetsFromDir.append(treeSubnet)

    # Layout created tree subnets
    obj.layoutChildren(tuple(createdTreeSubnets), vertical_spacing=0.35)

    return treeSubnetsFromDir


def treeSubnetsReformat(treeSubnetList):

    treeSubnetsReformatted = []
    for treeSubnet in treeSubnetList:
        # Format fbx
        # Create Matnet
        matnetName = treeSubnet.name() + "_matnet"
        treeSubnet = fbxSubnetFormat.createMatnet(treeSubnet, matnetName)
        print("Materials Created for: " + treeSubnet.name())
        # Create Material Assignments
        treeSubnet = fbxSubnetFormat.AssignMaterials(treeSubnet, matnetName)
        print("Created MaterialAssignments for: " + treeSubnet.name())

        treeSubnetsReformatted.append(treeSubnet)
        treeSubnetNames = [treeSubnet.name() for treeSubnet in treeSubnetsReformatted]
        print("Reformatted Trees: {TREESREFORMATTED}".format(TREESREFORMATTED=', '.join(treeSubnetNames)))

    return treeSubnetsReformatted


def generateScatterSubnets(treeSubnet, hfGeoNode):
    """
    Generate tree scatter subnet in specified node/context
    :param treeSubnet: Tree subnet hou.node object from which the scatter subnet will be generated
    :param hfGeoNode: hou.node in which the scatter subnet will be placed
    :return: hou.node tree scatter subnet
    """
    # Get tree subnet in obj if selected the scatter subnet
    if "_scatter" in treeSubnet.name():
        treeSubnetName = treeSubnet.name().replace("_scatter", "")
        treeSubnet = hou.node("/obj/{TREENAME}".format(TREENAME=treeSubnetName))

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


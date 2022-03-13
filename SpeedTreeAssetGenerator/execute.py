"""
Execution functions
"""

import hou
from . import fbxSubnet
from . import fbxSubnetFormat
from . import treeScatterSubnet
from . import redshiftProxy
from pathlib import Path


def treeSubnetsFromDir(subnetName, fbxFilePaths, convertToYup=False):
    """
    Creates a subnet from directory. A geo node will be added for each path.
    :param subnetName: Name of subnet to be created
    :param fbxFilePaths: List of fbx paths
    :return: treeSubnet hou.node object, isNewSubnet boolean
    """
    subnetExists = hou.node("/obj/{SUBNETNAME}".format(SUBNETNAME=subnetName))
    if subnetExists:
        progressMsg = "Updating subnet {TREESUBNET}".format(TREESUBNET=subnetName)
    else:
        progressMsg = "Creating subnet {TREESUBNET}".format(TREESUBNET=subnetName)
    print(progressMsg)

    # Import Fbx
    treeSubnet, actionMessage = fbxSubnet.importSpeedTreeFbx(subnetName, fbxFilePaths,
                                                             convertToYup=convertToYup)
    treeSubnet.setDisplayFlag(False)

    # Adding new subnets to list
    createdTreeSubnets = []
    if actionMessage.split()[0] == "Created":
        createdTreeSubnets.append(treeSubnet)

    return treeSubnet, progressMsg

def treeSubnetsReformat(treeSubnet, resetTransforms=True, matchSize=True, genRsMatandAssign=True):
    """
    Formats subnets which contain imported SpeedTree Fbxs
    :param treeSubnet: treeSubnet hou.node obj to be formatted
    :param resetTransforms: reset translations and rotations on geo level
    :param matchSize: add match size node
    :param genRsMatandAssign: assign redshift materials and assign materials
    :return: formatted treeSubnet hou.node object
    """
    # Message in progress bar
    if genRsMatandAssign:
        progressMsg = "Formatting and creating materials for {TREESUBNET}"\
            .format(TREESUBNET=treeSubnet.name())
    else:
        progressMsg = "Formatting {TREESUBNET}".format(TREESUBNET=treeSubnet.name())
    print(progressMsg)

    # Reformat treeSubnet
    matnetName = treeSubnet.name() + "_matnet"
    # Create Material Assignments
    treeSubnet = fbxSubnetFormat.AssignMaterials(treeSubnet, matnetName,
                                                 resetTransforms=resetTransforms,
                                                 matchSize=matchSize,
                                                 assignMat=genRsMatandAssign)
    # Create Matnet
    if genRsMatandAssign:
        treeSubnet = fbxSubnetFormat.createMatnet(treeSubnet, matnetName)
    # Layout treeSubnet
    treeSubnet.layoutChildren(vertical_spacing=0.35)

    return treeSubnet, progressMsg

def generateScatterSubnets(treeSubnets, hfGeoNodePath,
                           createGeoNode=False,
                           matchsize=True):
    """
    Generate tree scatter subnet in specified node/context
    :param treeSubnets: Tree subnet hou.node object from which the scatter subnet will be generated
    :param hfGeoNode: hou.node in which the scatter subnet will be placed
    :return: List of hou.node tree scatter subnets
    """
    treeSubnets = list(treeSubnets)
    # Get tree subnet in obj if selected the scatter subnet
    i = 0
    for treeSubnet in treeSubnets:
        if "_scatter" in treeSubnet.name():
            treeSubnets[i] = hou.node("/obj/{TREENAME}".format(TREENAME=treeSubnet.name().replace("_scatter", "")))
        i += 1

    # Define hfGeoNode
    hfGeoNode = hou.node(hfGeoNodePath)
    # Create Geo Node
    while createGeoNode:
        if hfGeoNode:
            break
        else:
            obj = hou.node("/obj")
            pathFixed = hfGeoNodePath.replace("\\", "/")
            pathFixed.removeprefix("/")
            pathFixed.removeprefix("obj/")
            obj.createNode("geo", node_name=pathFixed)
            break

    # Generate scatter subnet for each item in treeSubnets
    allScatterSubnets = []
    createdScatterSubnets = []
    for treeSubnet in treeSubnets:
        scatterSubnet, actionMessage = treeScatterSubnet.createTreeScatterSubnet(treeSubnet,
                                                                                 hfGeoNode,
                                                                                 matchsize=matchsize)
        allScatterSubnets.append(scatterSubnet)
        print(actionMessage)

        # If created, store in list
        if actionMessage.split()[0] == "Created":
            createdScatterSubnets.append(scatterSubnet)

    # Layout created tree subnets
    if createdScatterSubnets:
        hfGeoNode.layoutChildren(tuple(createdScatterSubnets), vertical_spacing=0.35)

    return allScatterSubnets


def generateRedshiftProxy(treeSubnets, rsFolder,
                          createIntermediateDirectories=True,
                          skipExistingFiles=False,
                          matchsize=True,
                          createSubdir=False):
    """
    Create Redshift proxy files for all geometry nodes in a specified tree subnet.
    :param treeSubnet: tuple of hou.node tree subnets
    :param rsFolder: file directory in which the rs proxy files will be generated
    :return: None
    """
    # Format directory path
    rsFolder = Path(rsFolder)

    for treeSubnet in treeSubnets:
        redshiftProxy.createRedshiftProxy(treeSubnet, rsFolder,
                                          createIntermediateDirectories=createIntermediateDirectories,
                                          skipExistingFiles=skipExistingFiles,
                                          matchsize=matchsize,
                                          createSubdir=createSubdir)

        print("Created Redshift Proxy files for {TREE}".format(TREE=treeSubnet.name()))



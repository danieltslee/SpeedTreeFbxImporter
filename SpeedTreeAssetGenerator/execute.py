"""
Execution functions
"""

import hou
from . import fbxSubnet
from . import fbxSubnetFormat
from . import treeScatterSubnet
from . import redshiftProxy
from pathlib import Path


def treeSubnetsFromDir(fbxImportFormat, onlyImportSelected=[],
                       reimportExisting=True,
                       convertToYup=False):
    """
    Creates subnets from directory. One subnet will be created for each folder containing fbxs
    :param directory: Folder which contains fbxs or subfolders containing the fbx files
    :return: List of hou.node tree subnet objects generated from directory
    """
    obj = hou.node("/obj")

    """# Get fbx directory
    fbxImportFormat, fbxFilePaths, fbxFileDirs = fbxSubnet.getFbxFilesList(directory)"""

    # Dictionary to Import
    treeDicttoImport = fbxImportFormat
    """# Only Import selected is tree names (keys)
    if onlyImportSelected:
        selectedItems = []  # THESE ARE THE SELECTED FOLDERS TO IMPORT
        treeDicttoImport = dict()
        for selectedItem in selectedItems:
            treeDicttoImport[selectedItem] = fbxImportFormat[selectedItem]"""

    # Only reimport existing
    if not reimportExisting:
        # Get all created subnets in obj
        existingTreeSubnetNames = []
        for child in obj.children():
            if child.creatorState() == "SpeedTree Asset Generator by Daniel":
                existingTreeSubnetNames.append(child.name())
        # Delete existing tree subnet name from dictionary to import
        for existingTreeSubnetName in existingTreeSubnetNames:
            if existingTreeSubnetName in treeDicttoImport:
                del treeDicttoImport[existingTreeSubnetName]

    treeSubnetsFromDir = []
    createdTreeSubnets = []
    for key in treeDicttoImport:
        # Import fbx
        subnetName = key
        fbxFilePaths = treeDicttoImport[key]
        treeSubnet, actionMessage = fbxSubnet.importSpeedTreeFbx(subnetName, fbxFilePaths,
                                                                 convertToYup=convertToYup)
        print("{MSG}".format(MSG=actionMessage))

        # If created, store in list
        if actionMessage.split()[0] == "Created":
            createdTreeSubnets.append(treeSubnet)

        treeSubnetsFromDir.append(treeSubnet)

    # Layout created tree subnets
    if createdTreeSubnets:
        obj.layoutChildren(tuple(createdTreeSubnets), vertical_spacing=0.35)

    # Spacer
    print("")

    return treeSubnetsFromDir


def treeSubnetsReformat(treeSubnetList, resetTransforms=True, matchSize=True):

    treeSubnetsReformatted = []
    for treeSubnet in treeSubnetList:
        # Format fbx
        # Create Matnet
        matnetName = treeSubnet.name() + "_matnet"
        treeSubnet = fbxSubnetFormat.createMatnet(treeSubnet, matnetName)
        print("Materials Created for: " + treeSubnet.name())
        # Create Material Assignments
        treeSubnet = fbxSubnetFormat.AssignMaterials(treeSubnet, matnetName,
                                                     resetTransforms=resetTransforms,
                                                     matchSize=matchSize)
        print("Created MaterialAssignments for: " + treeSubnet.name())

    treeSubnetsReformatted.append(treeSubnet)

    return treeSubnetsReformatted


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



"""
Execution functions
"""

import hou
import fbxSubnet
import fbxSubnetFormat
import treeScatterSubnet
import redshiftProxy

def treeSubnetsFromDir(fbxImportFormat, convertToYup=False):
    """
    Creates subnets from directory. One subnet will be created for each folder containing fbxs
    :param directory: Folder which contains fbxs or subfolders containing the fbx files
    :return: List of hou.node tree subnet objects generated from directory
    """
    obj = hou.node("/obj")

    # Dictionary to Import
    treeDicttoImport = fbxImportFormat

    treeSubnetsFromDir = []
    createdTreeSubnets = []
    for key in treeDicttoImport:
        # Import fbx
        subnetName = key
        fbxFilePaths = treeDicttoImport[key]
        treeSubnet, actionMessage = fbxSubnet.importSpeedTreeFbx(subnetName, fbxFilePaths,
                                                                 convertToYup=convertToYup)
        treeSubnet.setDisplayFlag(False)
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


def treeSubnetsReformat(treeSubnetList, resetTransforms=True, matchSize=True, genRsMatandAssign=True):

    treeSubnetsReformatted = []
    for treeSubnet in treeSubnetList:
        # matnet name
        matnetName = treeSubnet.name() + "_matnet"

        # Create Material Assignments
        treeSubnet = fbxSubnetFormat.AssignMaterials(treeSubnet, matnetName,
                                                     resetTransforms=resetTransforms,
                                                     matchSize=matchSize,
                                                     assignMat=genRsMatandAssign)
        # Create Matnet
        if genRsMatandAssign:
            treeSubnet = fbxSubnetFormat.createMatnet(treeSubnet, matnetName)
            print("Materials Created for: " + treeSubnet.name())
        print("Formatted: " + treeSubnet.name())

        treeSubnet.layoutChildren(vertical_spacing=0.35)

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


    for treeSubnet in treeSubnets:
        redshiftProxy.createRedshiftProxy(treeSubnet, rsFolder,
                                          createIntermediateDirectories=createIntermediateDirectories,
                                          skipExistingFiles=skipExistingFiles,
                                          matchsize=matchsize,
                                          createSubdir=createSubdir)

        print("Created Redshift Proxy files for {TREE}".format(TREE=treeSubnet.name()))



"""
API for building tree fbx subnet given SpeedTree Fbx imports
"""

import hou
import os
from . import classNodeNetwork
from . import helper


def getFbxFilesList(rootDir):
    """
    Returns dictionary of to import fbx. Example: {"BostonFern": [path/to/geo1.fbx, path/to/geo2.fbx]}
    The key is the directory name in which the fbx is in. All fbx's in the same directory will be in the same subnet
    """

    # Find fbx files in directory
    fbxFilePaths = []
    fbxFiles = []
    for (root, dirs, files) in os.walk(rootDir):
        for file in files:
            if file.endswith(".fbx"):
                fbxFilePaths.append(os.path.join(root, file))
                fbxFiles.append(file)
    fbxFilePaths = [fbxFilePath.replace("\\", "/") for fbxFilePath in fbxFilePaths]

    # Get fbxFileDirs
    fbxFileDirs = []
    for fbxFilePath in fbxFilePaths:
        lastSlashIndex = fbxFilePath.rfind("/")
        fbxFileDirs.append(fbxFilePath[0:lastSlashIndex])

    # Store list of directory names where the fbx's are
    fbxSubnetKeys = []
    for fbxFileDir in fbxFileDirs:
        lastSlashIndex = fbxFileDir.rfind("/")
        fbxSubnetKeys.append(fbxFileDir[lastSlashIndex+1:])

    # Create formatted fbx import dictionary
    fbxImportFormat = {}
    i = 0
    for fbxSubnetKey in fbxSubnetKeys:
        if fbxSubnetKey in fbxImportFormat:
            fbxImportFormat[fbxSubnetKey].append(fbxFilePaths[i])
        else:
            fbxImportFormat[fbxSubnetKey] = [fbxFilePaths[i]]
        i += 1

    return fbxImportFormat, fbxFilePaths, fbxFileDirs


def importSpeedTreeFbx(treeSubnetName, fbxFilePathsList):
    """ Imports all Speed Tree fbx files in a directory and collapses into a single subnet
    Returns subnet with cleaned geometry nodes """

    # Define obj context
    obj = hou.node("/obj")

    # If tree subnet already exists, delete it
    oldTreeSubnet = hou.node("/obj/{TREESUBNETNAME}".format(TREESUBNETNAME=treeSubnetName))
    if oldTreeSubnet:
        # Get old subnet position
        oldTreeSubnetPos = oldTreeSubnet.position()
        # Find network box that node is in
        currentNetworkBox = helper.getNetworkBox(oldTreeSubnet, obj)
        action = "Updated"
        oldTreeSubnet.destroy()
    else:
        currentNetworkBox = None
        action = "Created"

    # Import Fbx geo and collapse into subnet
    subnetGeos = []
    for fbxFile in fbxFilePathsList:
        importedSubnet, importMsgs = hou.hipFile.importFBX(fbxFile, import_cameras=False,
                                                   import_joints_and_skin=False,
                                                   import_lights=False,
                                                   import_animation=False,
                                                   import_materials=True,
                                                   import_geometry=True,
                                                   hide_joints_attached_to_skin=True,
                                                   convert_joints_to_zyx_rotation_order=False,
                                                   material_mode=hou.fbxMaterialMode.VopNetworks,
                                                   compatibility_mode=hou.fbxCompatibilityMode.Maya,
                                                   unlock_geometry=True,
                                                   import_nulls_as_subnets=True,
                                                   import_into_object_subnet=True,
                                                   create_sibling_bones=False)

        mySubnet = classNodeNetwork.MyNetwork(importedSubnet)
        mySubnet.cleanNetwork("shopnet", method="type")
        subnetChildren = mySubnet.extractChildren()

        for subnetChild in subnetChildren:
            subnetGeos.append(subnetChild)

        importedSubnet.destroy()

    # Collapse geo nodes into subnet, name it treeName
    collapsedSubnet = obj.collapseIntoSubnet(subnetGeos, treeSubnetName)
    # Move to old position if exists
    if oldTreeSubnet:
        collapsedSubnet.setPosition(oldTreeSubnetPos)
    # Put in network box
    if currentNetworkBox:
        currentNetworkBox.addNode(collapsedSubnet)
    # Layout children
    collapsedSubnet.layoutChildren(vertical_spacing=0.35)
    # Set subnet color
    subnetColor = hou.Color((.71, .518, .004))
    collapsedSubnet.setColor(subnetColor)

    # Message
    actionMessage = "{ACTION} Tree Subnet: {TREESUBNETNAME}".format(ACTION=action, TREESUBNETNAME=treeSubnetName)

    return collapsedSubnet, actionMessage

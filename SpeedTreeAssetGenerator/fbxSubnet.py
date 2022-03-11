"""
API for building tree fbx subnet given SpeedTree Fbx imports
"""

import hou
import os
import classNodeNetwork
import helper


def getFbxFilesList(rootDir):
    """
    Returns dictionary of import fbx. Example: {"BostonFern": [path/to/geo1.fbx, path/to/geo2.fbx]}
    The key is the directory name in which the fbx is in. All fbx's in the same directory will be in the same subnet
    :param rootDir: Folder which contains folders or subfolders containing the fbx files
    :return: Formatted dictionary, fbx file paths, fbx file directories
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

def importSpeedTreeFbx(treeSubnetName, fbxFilePathsList, convertToYup=False):
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
    for fbxFile in fbxFilePathsList:
        importedSubnet, importMsgs = hou.hipFile.importFBX(fbxFile,
                                                           import_cameras=False,
                                                           import_joints_and_skin=False,
                                                           import_lights=False,
                                                           import_animation=False,
                                                           import_materials=True,
                                                           import_geometry=True,
                                                           hide_joints_attached_to_skin=True,
                                                           convert_joints_to_zyx_rotation_order=convertToYup,
                                                           material_mode=hou.fbxMaterialMode.VopNetworks,
                                                           compatibility_mode=hou.fbxCompatibilityMode.Maya,
                                                           unlock_geometry=True,
                                                           import_nulls_as_subnets=True,
                                                           import_into_object_subnet=True,
                                                           create_sibling_bones=False)

        mySubnet = classNodeNetwork.MyNetwork(importedSubnet)
        mySubnet.cleanNetwork("shopnet", "matnet", method="type")

        """# Rename LOD nodes if existing
        treeSubnetGeos = [node for node in importedSubnet.children() if node.type().name() == "geo"]
        LODGeos = [geo for geo in treeSubnetGeos if "lod" in geo.name().lower()]
        if LODGeos:
            for LODGeo in LODGeos:
                LODGeo.setName(LODGeo.input(0).name() + "_" + LODGeo.name())
        """
        # Set treeSubnet if the subnet already exists in obj. Move child nodes to treeSubnet
        objChildrenNames = [child.name() for child in obj.children()]
        if treeSubnetName in objChildrenNames:
            treeSubnet = hou.node("/obj/{TREESUBNETNAME}".format(TREESUBNETNAME=treeSubnetName))
            hou.moveNodesTo(importedSubnet.children(), treeSubnet)
            importedSubnet.destroy()
        else:  # Set treeSubnet if it doesn't exist yet
            importedSubnet.setName(treeSubnetName)
            treeSubnet = importedSubnet

    # Move to old position if exists
    if oldTreeSubnet:
        treeSubnet.setPosition(oldTreeSubnetPos)
    # Put in network box
    if currentNetworkBox:
        currentNetworkBox.addNode(treeSubnet)
    # Layout children
    treeSubnet.layoutChildren(vertical_spacing=0.35)
    # Set subnet color
    subnetColor = hou.Color((.71, .518, .004))
    treeSubnet.setColor(subnetColor)
    # collapsedSubnet set creator state
    treeSubnet.setCreatorState("SpeedTree Asset Generator by Daniel")

    # Message
    actionMessage = "{ACTION} Tree Subnet: {TREESUBNETNAME}".format(ACTION=action, TREESUBNETNAME=treeSubnetName)

    return treeSubnet, actionMessage


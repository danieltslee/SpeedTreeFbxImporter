"""
API for  creating .rs files in specified directory
"""

import hou
from . import classNodeNetwork as cnn

def createRedshiftProxy(treeSubnet, rsFolder,
                        createIntermediateDirectories=True,
                        skipExistingFiles=False,
                        matchsize=True,
                        createSubdir=False):
    """
    Create Redshift proxy files for all geometry nodes in a specified tree subnet
    :param treeSubnet: hou.node tree subnet
    :param rsFolder: file directory in which the rs proxy files will be generated
    :return: None
    """

    # Define out context
    out = hou.node("/out")

    # Create Redshift Rop temp
    rsRop = out.createNode("Redshift_ROP", node_name="proxy_export_temp")

    # Create assign material wrangle in tree geometry
    for treeGeo in treeSubnet.children():
        treeGeoNet = cnn.MyNetwork(treeGeo)
        # Create only in Geometry Nodes, skips matnets
        if treeGeo.type().name() != "geo":
            continue

        # Match size before output
        matchsizeNode = None
        if matchsize:
            lastNode = treeGeoNet.findLastNode()
            secondLastNode = lastNode.inputs()[0]
            matchsizeNode = treeGeo.createNode("matchsize", node_name="proxy_matchsize")
            matchsizeNode.setParms({"justify_y":1})
            matchsizeNode.setParms({"doscale":1})
            matchsizeNode.setParms({"uniformscale": 1})
            matchsizeNode.setParms({"scale_axis": 0})
            # Connect match size node
            matchsizeNode.setInput(0, secondLastNode)
            lastNode.setInput(0, matchsizeNode)

        # Create Intermediate Directories
        if createIntermediateDirectories:
            rsRop.setParms({"RS_archive_createDirs": 1})
        else:
            rsRop.setParms({"RS_archive_createDirs": 0})

        # Skip Existing Files
        if skipExistingFiles:
            rsRop.setParms({"RS_archive_skipFiles": 1})
        else:
            rsRop.setParms({"RS_archive_skipFiles": 0})

        # Create folder path
        folderPath = rsFolder
        if createSubdir:
            folderPath = "{RSFOLDER}/{TREESUBDIR}".format(RSFOLDER=rsFolder, TREESUBDIR=treeSubnet.name())

        # Set File Name
        rsRop.setParms({"RS_archive_enable": 1})
        rsRop.setParms(
            {"RS_archive_file": "{FOLDER}/{TREEGEO}_rsProxy.rs".format(FOLDER=folderPath, TREEGEO=treeGeo.name())})
        # Set Objects
        rsRop.setParms({"RS_objects_candidate": ""})
        rsRop.setParms({"RS_objects_force": treeGeo.path()})
        rsRop.setParms({"RS_lights_candidate": ""})

        # Press button to create .rs file
        renderToDisk = rsRop.parm("execute")
        renderToDisk.pressButton()

        # Delete temporary matchsize after creating .rs file
        if matchsizeNode:
            matchsizeNode.destroy()

    # Delete Temporary Rop
    rsRop.destroy()

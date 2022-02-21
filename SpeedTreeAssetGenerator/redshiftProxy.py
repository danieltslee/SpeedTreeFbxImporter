"""
API for  creating .rs files in specified directory
"""

import hou

def createRedshiftProxy(treeSubnet, rsFolder):
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
        # Create only in Geometry Nodes, skips matnets
        if treeGeo.type().name() != "geo":
            continue

        # Set File Name
        rsRop.setParms({"RS_archive_enable": 1})
        rsRop.setParms(
            {"RS_archive_file": "{FOLDER}/{TREEGEO}_rsProxy.rs".format(FOLDER=rsFolder, TREEGEO=treeGeo.name())})
        # Set Objects
        rsRop.setParms({"RS_objects_candidate": ""})
        rsRop.setParms({"RS_objects_force": treeGeo.path()})
        rsRop.setParms({"RS_lights_candidate": ""})

        # Press button to create .rs file
        renderToDisk = rsRop.parm("execute")
        renderToDisk.pressButton()

    # Delete Temporary Rop
    rsRop.destroy()

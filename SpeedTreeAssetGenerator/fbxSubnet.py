"""
API for building tree fbx subnet given SpeedTree Fbx imports
"""

import hou
import os
import classNodeNetwork as cnn

def importSpeedTreeFbx():
    """ Imports all Speed Tree fbx files in a directory and collapses into a single subnet
    Returns subnet with cleaned geometry nodes"""
    hipPath = hou.hipFile.path()
    hipBaseName = hou.hipFile.basename()
    hipDir = hipPath.replace(hipBaseName, "")
    treeName = "BosternFern"
    fileDir = "{HIPDIR}assets/myTrees/BostonFern/".format(HIPDIR=hipDir)
    fileName = "BostonFern_varB.fbx"
    fullPath = fileDir + fileName

    # Find fbx files in directory
    fbxFiles = []
    for file in os.listdir(fileDir):
        if file.endswith(".fbx"):
            fbxFiles.append(os.path.join(fileDir, file))

    # Define obj context
    obj = hou.node("/obj")

    # Import Fbx geo and collapse into subnet
    subnetGeos = []
    for fbxFile in fbxFiles:
        subnet, importMsgs = hou.hipFile.importFBX(fbxFile, import_cameras=False,
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

        mySubnet = cnn.MyNetwork(subnet)
        mySubnet.cleanNetwork("shopnet", method="type")
        subnetChildren = mySubnet.extractChildren()

        for subnetChild in subnetChildren:
            subnetGeos.append(subnetChild)

        subnet.destroy()

    collapsedSubnet = obj.collapseIntoSubnet(subnetGeos, treeName)
    # Layout children
    collapsedSubnet.layoutChildren()

    return collapsedSubnet


def AssignMaterials(subnet):
    """ Creates s@shop_materialpath attribute to existing primitive groups
    Returns formatted subnet and matnetName"""
    treeSubnet = cnn.MyNetwork(subnet)
    treeName = subnet.name()

    for treeGeo in treeSubnet.children:
        treeGeo.parm("tx").revertToDefaults()
        treeGeo.parm("ty").revertToDefaults()
        treeGeo.parm("tz").revertToDefaults()
        treeGeoNet = cnn.MyNetwork(treeGeo)
        print("Creating MaterialAssignments for " + treeGeoNet.name)

        # Prefix of new nodes
        newNodesPrefix = "myTree"

        # Clean old sops if any
        treeGeoNet.cleanNetwork("material", "pack", "output", method="type")
        treeGeoNet.cleanNetwork("assign_materials", method="name")
        #fileNode = treeGeoNet.findNodes("type", "file")[0]
        lastSop = treeGeoNet.findLastNode()

        # Add nodes and wire

        newNodes = treeGeoNet.addNodes("attribwrangle", "pack", "output", prefix=newNodesPrefix)
        treeGeoNet.wireNodes(newNodes, lastSop)

        # Add vex snippet to attribute wrangle. Create s@shop_materialpath to primitives
        assignWrangle = treeGeoNet.findNodes("type","attribwrangle")[0]
        assignWrangle.setName(newNodesPrefix+"_assign_materials")
        snippetParm = assignWrangle.parm("snippet")
        matnetName = treeName + "_matnet"
        matnetPath = "../../{MATNETNAME}/".format(MATNETNAME=matnetName)
        assignSnippet = '''// Assign different materials for each primitive group
string groups[] = detailintrinsic(0, "primitivegroups");

foreach (string group; groups) {{
    if (inprimgroup(0,group,@primnum) == 1){{
        string path = "{MATNETPATH}" + re_replace("_group","",group) + "/";
        s@shop_materialpath = opfullpath(path);
        }}

    }}
        '''.format(MATNETPATH=matnetPath)
        snippetParm.set(assignSnippet)
        assignWrangle.setParms({"class": 1})

        # Layout children
        treeGeo.layoutChildren(vertical_spacing=1)
        # Set display flag
        treeGeoNet.findLastNode().setDisplayFlag(True)
        treeGeoNet.findLastNode().setRenderFlag(True)

    return subnet, matnetName


def createMatnet(subnet, matnetName):
    treeSubnet = subnet
    treeMatnet = treeSubnet.createNode("matnet", matnetName)

    # Query first tree geo node in subnet
    treeGeo = treeSubnet.children()[0]
    treeGeoNet = cnn.MyNetwork(treeGeo)

    # Create material networks based on existing group nodes
    groupNodes = treeGeoNet.findNodes("group", method="name")
    groupNodeNames = [groupNode.name() for groupNode in groupNodes]
    groupMaterials = [groupNodeName.replace("_group","") for groupNodeName in groupNodeNames]
    print(groupMaterials)
    """
    for groupMaterial in groupMaterials:
        rsmb = treeMatnet.createNode("redshift_vopnet", groupMaterial)
        rsmbOut = rsmb.children()[0]
        shader = rsmb.children()[1]
        shaderTexName = groupMaterial.replace("_Mat","")
    """


def exe():
    treeSubnet = importSpeedTreeFbx()
    treeSubnet, matnetName = AssignMaterials(treeSubnet)
    createMatnet(treeSubnet, matnetName)



"""
API for building formatting tree subnet built from fbx Subnet
"""

from . import classNodeNetwork

def AssignMaterials(subnet):
    """ Creates s@shop_materialpath attribute to existing primitive groups
    Returns formatted subnet and matnetName"""
    treeSubnet = classNodeNetwork.MyNetwork(subnet)
    treeName = subnet.name()

    for treeGeo in treeSubnet.children:
        treeGeo.parm("tx").revertToDefaults()
        treeGeo.parm("ty").revertToDefaults()
        treeGeo.parm("tz").revertToDefaults()
        treeGeoNet = classNodeNetwork.MyNetwork(treeGeo)
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
    treeGeoNet = classNodeNetwork.MyNetwork(treeGeo)

    # Create material networks based on existing group nodes
    groupNodes = treeGeoNet.findNodes("group", method="name")
    groupNodeNames = [groupNode.name() for groupNode in groupNodes]
    groupMaterials = [groupNodeName.replace("_group", "") for groupNodeName in groupNodeNames]
    print(groupMaterials)
    """
    for groupMaterial in groupMaterials:
        rsmb = treeMatnet.createNode("redshift_vopnet", groupMaterial)
        rsmbOut = rsmb.children()[0]
        shader = rsmb.children()[1]
        shaderTexName = groupMaterial.replace("_Mat","")
    """

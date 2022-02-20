"""
API for building formatting tree subnet built from fbx Subnet
"""

import hou
from . import classNodeNetwork
from . import fbxSubnet
from PIL import Image

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


def materialDirectory():
    pass


def createMatnet(treeSubnet, matnetName):
    # Create Matnet
    treeMatnet = treeSubnet.createNode("matnet", matnetName)

    # Query first tree geo node in subnet
    treeGeo = treeSubnet.children()[0]
    treeGeoNet = classNodeNetwork.MyNetwork(treeGeo)

    # Get variables
    treeName = treeSubnet.name()

    # Create Redshift material networks based on existing primitive groups
    groupNodes = treeGeoNet.findNodes("group", method="name")
    groupNameParms = [groupNode.parm("crname") for groupNode in groupNodes]
    groupMaterials = [groupNameParm.eval().replace("_group", "") for groupNameParm in groupNameParms]
    print(groupMaterials)

    # Initialize Redshift Material Builders
    for groupMaterial in groupMaterials:
        rsmb = treeMatnet.createNode("redshift_vopnet", groupMaterial)
        rsmbOut = rsmb.children()[0]
        shader = rsmb.children()[1]
        shaderTexName = groupMaterial.replace("_Mat", "")

        # Path is $HIP/assets/myTrees/prefix/shaderTexName
        # Create Diffuse
        colorVop = rsmb.createNode("redshift::TextureSampler", "Color")
        colorVop.setParms({"tex0_colorSpace": "sRGB"})
        colorPath = "$HIP/assets/myTrees/{0}/{1}.png".format(treeName, shaderTexName)
        colorVop.setParms({"tex0": colorPath})
        # Create Normal
        normalVop = rsmb.createNode("redshift::TextureSampler", "Normal")
        normalVop.setParms({"tex0_colorSpace": "Raw"})
        normalPath = "$HIP/assets/myTrees/{0}/{1}_Normal.png".format(treeName, shaderTexName)
        normalVop.setParms({"tex0": normalPath})
        # Create Bump Vop
        bumpVop = rsmb.createNode("redshift::BumpMap")
        # Connect Diffuse
        shader.setInput(0, colorVop, 0)
        if "leaf" in groupMaterial.lower() or "leaves" in groupMaterial.lower():
            shader.setInput(3, colorVop, 0)  # Translucency
            shader.setParms({"transl_weight": 0.25})
        # Connect Bump Vop
        shader.setInput(52, bumpVop, 0)
        # Connect Normal
        bumpVop.setInput(0, normalVop, 0)

        # Find Opacity Image
        hipPath = hou.expandString("$HIP")
        texOpacityPath = "{0}/assets/myTrees/{1}/{2}_Opacity.png".format(hipPath, treeName, shaderTexName)
        # Sample Opacity Image
        img = Image.open(texOpacityPath)
        imgData = list(img.getdata(band=0))
        hasAlpha = 0 in imgData  # True if image has 0 in opacity texture
        img.close()
        # Create Sprite Vop if Opacity image has data
        spriteVop = rsmb.createNode("redshift::Sprite")
        # if ("leaf" in matName.lower() or "leaves" in matName.lower()) and ("branch" in matName.lower()):
        if hasAlpha:
            spriteVop.setParms({"tex0_colorSpace": "Raw"})
            spritePath = "$HIP/assets/myTrees/{0}/{1}_Opacity.png".format(treeName, shaderTexName)
            spriteVop.setParms({"tex0": spritePath})
            # Connect Sprite Vop
            rsmbOut.setInput(0, spriteVop, 0)
            spriteVop.setInput(0, shader, 0)
        else:
            spriteVop.destroy()
        # Layout texture and shader nodes
        rsmb.layoutChildren()

    # Format tree matnet
    treeMatnet.layoutChildren(vertical_spacing=1)


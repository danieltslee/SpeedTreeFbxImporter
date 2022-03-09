## Create geometry context
#obj = hou.node("/obj")
#prefix = hou.ui.readInput("Tree Subnet:")[1]
##prefix = "Acacia"
#print("Tree Subnet is " + prefix)



def createMaterialAssignments(prefix):
    # Define tree subnet
    treeSubnet = hou.node("/obj/" + prefix)

    # Create assign material wrangle in tree geometry
    for treeGeo in treeSubnet.children():
        # Delete any previous matnet
        if treeGeo.type().name() == "matnet" or treeGeo.type().name() == "shopnet":
            print("Destroyed previous matnet.")
            treeGeo.destroy()
            continue

        # Reset Transforms
        tx = treeGeo.parm("tx")
        ty = treeGeo.parm("ty")
        tz = treeGeo.parm("tz")
        tx.revertToDefaults()
        ty.revertToDefaults()
        tz.revertToDefaults()

        print("Creating MaterialAssignments for " + treeGeo.name())

        # Find geo sop and find any previews materials, assignments, and outputs
        oldNodes = [];
        for sop in treeGeo.children():
            if sop.type().name() == "file":
                geoSop = sop
            if sop.type().name() == "material":
                oldNodes.append(sop)
            if sop.name() == "assign_materials":
                oldNodes.append(sop)
            if sop.type().name()=="output":
                oldNodes.append(sop)
            if sop.type().name()=="pack":
                oldNodes.append(sop)

        # Destory any previews materials, assignments, and outputs
        for oldNode in oldNodes:
            oldNode.destroy()

        # Find last sop in chain prior to creating wrangle
        for sop in treeGeo.children():
            if not sop.outputs():
                lastSop = sop

        # Unlock geoSop
        geoSop.setHardLocked(False)



        # Create vex snippet
        assignWrangle = treeGeo.createNode("attribwrangle","assign_materials")

        snippetParm = assignWrangle.parm("snippet")

        matnet = "../../{0}_matnet/".format(prefix)

        assignSnippet = '''
string groups[] = detailintrinsic(0, "primitivegroups");

foreach (string group; groups) {{
    if (inprimgroup(0,group,@primnum) == 1){{
        string path = "{0}" + re_replace("_group","",group) + "/";
        s@shop_materialpath = opfullpath(path);
             }}

    }}
    '''.format(matnet)

        snippetParm.set(assignSnippet)
        assignWrangle.setParms({"class":1})
        assignWrangle.setInput(0,lastSop)

        # Create Pack sop
        packSop = treeGeo.createNode("pack")
        packSop.setInput(0,assignWrangle)
        # Create Output node
        outputSop = treeGeo.createNode("output")
        outputSop.setInput(0,packSop)
        # Layout
        treeGeo.layoutChildren(vertical_spacing=1)
        # Set Flags
        outputSop.setDisplayFlag(True)
        outputSop.setRenderFlag(True)
        # Set selected
        outputSop.setSelected(True,clear_all_selected=True)


def createMatnet(prefix):
    from PIL import Image

    # Define tree subnet
    treeSubnet = hou.node("/obj/" + prefix)

    # Create matnet
    matnet = treeSubnet.createNode("matnet",prefix + "_matnet")

    # Get material names
    treeGeo = treeSubnet.children()[0]

    matsNeeded = [] # names of group sops without the "_group"
    for sop in treeGeo.children():
        if "_group" in sop.name():
            matsNeeded.append(sop.name().replace("_group",""))

    # Create Redshift Material Builders
    for matName in matsNeeded:
        # matName is names of group sops without the "_group"
        rsmb = matnet.createNode("redshift_vopnet",matName)
        rsmbOut = rsmb.children()[0]
        shader = rsmb.children()[1]
        shaderTexName = matName.replace("_Mat","")

        # Path is $HIP/assets/myTrees/prefix/shaderTexName
        # Create Diffuse
        colorVop = rsmb.createNode("redshift::TextureSampler", "Color")
        colorVop.setParms({"tex0_colorSpace":"sRGB"})
        colorPath = "$HIP/assets/myTrees/{0}/{1}.png".format(prefix,shaderTexName)
        colorVop.setParms({"tex0":colorPath})
        # Create Normal
        normalVop = rsmb.createNode("redshift::TextureSampler", "Normal")
        normalVop.setParms({"tex0_colorSpace":"Raw"})
        normalPath = "$HIP/assets/myTrees/{0}/{1}_Normal.png".format(prefix,shaderTexName)
        normalVop.setParms({"tex0":normalPath})
        # Create Bump Vop
        bumpVop = rsmb.createNode("redshift::BumpMap")
        # Connect Diffuse
        shader.setInput(0,colorVop,0)
        if "leaf" in matName.lower() or "leaves" in matName.lower():
            shader.setInput(3,colorVop,0) # Translucency
            shader.setParms({"transl_weight":0.25})
        # Connect Bump Vop
        shader.setInput(52,bumpVop,0)
        # Connect Normal
        bumpVop.setInput(0,normalVop,0)

        # Find Opacity Image
        hipPath = hou.expandString("$HIP")
        texOpacityPath = "{0}/assets/myTrees/{1}/{2}_Opacity.png".format(hipPath,prefix,shaderTexName)
        # Sample Opacity Image
        img = Image.open(texOpacityPath)
        imgData = list(img.getdata(band=0))
        hasAlpha = 0 in imgData # True if image has 0 in opacity texture
        img.close()
        # Create Sprite Vop if Opacity image has data
        spriteVop = rsmb.createNode("redshift::Sprite")
        #if ("leaf" in matName.lower() or "leaves" in matName.lower()) and ("branch" in matName.lower()):
        if hasAlpha:
            spriteVop.setParms({"tex0_colorSpace":"Raw"})
            spritePath = "$HIP/assets/myTrees/{0}/{1}_Opacity.png".format(prefix,shaderTexName)
            spriteVop.setParms({"tex0":spritePath})
            # Connect Sprite Vop
            rsmbOut.setInput(0,spriteVop,0)
            spriteVop.setInput(0,shader,0)
        else:
            spriteVop.destroy()

        rsmb.layoutChildren()

    matnet.layoutChildren(vertical_spacing=1)



def createTreeScatterSubnet(prefix,hf_geo_path):
    import hou
    # Define tree subnet
    treeSubnet = hou.node("/obj/" + prefix)

    # Create obj merge and transform sops in hf_geo
    #hf_geo = hou.node("/obj/hf_geo")
    hf_geo = hou.node("/obj/" + hf_geo_path)
    # Deletes old treeScatterSubnet if existing
    treeScatterSubnetName = "{0}_scatter".format(prefix)
    oldSubnetPos = None
    allSubnets = ()
    for sop in hf_geo.children():
        # If old tree scatter subnet exists
        if sop.name() == treeScatterSubnetName:
            oldSubnetPos = sop.position()

        # Initialize some variables
            oldSubnetOutput = None

            # If old subnet has connection, find which input it is in the Merge node
            if bool(sop.outputs()):
                oldSubnetOutput = sop.outputs()[0]
                allSubnets = oldSubnetOutput.inputs()
                # Finds which input the old subnet is connected into
                inputIndex = allSubnets.index(sop)
            sop.destroy()

    # overall merge sop
    mergeTreeGeo = hf_geo.createNode("merge","merge_{0}".format(prefix))
    # overall xform scale sop
    xformScale = hf_geo.createNode("xform","{0}_scale".format(prefix))
    xformScale.setInput(0,mergeTreeGeo)
    # overall weight
    attrWeight = hf_geo.createNode("attribcreate::2.0","{0}_weight".format(prefix))
    attrWeight.setParms({"name1":"weight","class1":1,"value1v1":1})
    attrWeight.setInput(0,xformScale)
    # create output sop
    output = hf_geo.createNode("output","{0}_output".format(prefix))
    output.setInput(0,attrWeight)

    i = 0 # to store iteration
    subnetNodes = [mergeTreeGeo,xformScale,attrWeight,output] # subnetNodes list
    for treeGeo in treeSubnet.children():
        if treeGeo.type().name() == "matnet" or treeGeo.type().name() == "shopnet":
            continue
        objectMerge = hf_geo.createNode("object_merge",treeGeo.name())
        objectMerge.setParms({"objpath1":"/obj/{0}/$OS".format(prefix)})

        xform = hf_geo.createNode("xform","{0}_scale_to_x".format(treeGeo.name()))
        xform.setParmExpressions({"sx":"1 / bbox(0,D_XSIZE)", "sy":"ch(\"sx\")", "sz":"ch(\"sx\")"})
        xform.setInput(0,objectMerge)

        mergeTreeGeo.setInput(i,xform)
        i += 1

        # Add all new nodes into subnet
        subnetNodes.extend([objectMerge,xform])

    # Collapse into Subnet
    treeScatterSubnet = hf_geo.collapseIntoSubnet(subnetNodes,treeScatterSubnetName)
    treeScatterSubnet.layoutChildren()

    # Create Float Slider
    group = treeScatterSubnet.parmTemplateGroup()
    treeScaleTemplate = hou.FloatParmTemplate("treeScale", ("Tree Scale"), 1, default_value=([1]), min=0, max=6)
    group.append(treeScaleTemplate)
    weightTemplate = hou.FloatParmTemplate("weight", ("Weight"), 1, default_value=([1]), min=0, max=1)
    group.append(weightTemplate)
    treeScatterSubnet.setParmTemplateGroup(group)

    # Set relative references
    xformScale = hou.node(treeScatterSubnet.path()+"/{0}_scale".format(prefix))
    xformScaleParm = xformScale.parm("scale")
    xformScaleParm.setExpression("ch(\"../treeScale\")")

    attrWeight = hou.node(treeScatterSubnet.path()+"/{0}_weight".format(prefix))
    attrWeightParm = attrWeight.parm("value1v1")
    attrWeightParm.setExpression("ch(\"../weight\")")

    # Set Flags
    output = hou.node(treeScatterSubnet.path()+"/{0}_output".format(prefix))
    output.setRenderFlag(True)
    output.setDisplayFlag(True)

    # Move to replaced subnet location if was deleted
    if not oldSubnetPos == None:
        treeScatterSubnet.setPosition(oldSubnetPos)

    # Rewire all subnets
    if bool(allSubnets):
        allSubnetsList = list(allSubnets)
        allSubnetsList[inputIndex] = treeScatterSubnet
        # Disconnet all merge inputs
        for input in oldSubnetOutput.inputs():
            oldSubnetOutput.setInput(0, None)
        i = 0
        for subnet in allSubnetsList:
            oldSubnetOutput.setInput(len(allSubnetsList),subnet)
            i += 1

        print("Finished updating {0} Tree Scatter Subnet in /obj/{1}\n".format(prefix,hf_geo_path))
    else:
        print("Finished creating {0} Tree Scatter Subnet in /obj/{1}\n".format(prefix,hf_geo_path))





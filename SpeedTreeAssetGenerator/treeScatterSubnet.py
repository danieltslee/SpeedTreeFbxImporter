"""
API for creating tree scatter subnet
"""

import hou
from . import classNodeNetwork as cnn

def findNodeInList(nodeList, nodeType):
    """
    Simple function to return the first node that matches the node type
    :param nodeList: List of nodes
    :param nodeType: String of the node type
    :return: hou.node object
    """
    for node in nodeList:
        if node.type().name() == nodeType:
            break
        else:
            node = None
    return node

def createTreeScatterSubnet(treeSubnet, hfGeoNode):
    """ Create Subnet used for scattering in hf_scatter SOP"""
    treeSubnetNet = cnn.MyNetwork(treeSubnet)
    hfGeoNodeNet = cnn.MyNetwork(hfGeoNode)

    treeScatterSubnetName = treeSubnetNet.name + "_scatter"

    # Create tree scatter subnet
    oldScatterSubnetList = hfGeoNodeNet.findNodes(treeScatterSubnetName, method="name")
    if oldScatterSubnetList:
        oldScatterSubnet = oldScatterSubnetList[0]
        # Store old position and name
        oldScatterSubnetPos = oldScatterSubnet.position()
        oldScatterSubnetName = oldScatterSubnet.name()
        # Store wired merge node if exists
        if oldScatterSubnet.outputs():
            scatterMergeNodes = oldScatterSubnet.outputs()
            scatterConnections = oldScatterSubnet.outputConnections()
            scatterConnectionIndicies = [scatterConnection.inputIndex() for scatterConnection in scatterConnections]
        else:
            scatterMergeNodes = ()
            scatterConnectionIndicies = []

        # Copy old scatter subnet and delete contents
        scatterSubnet = oldScatterSubnet.copyTo(oldScatterSubnet.parent())
        oldScatterSubnet.destroy()
        for child in scatterSubnet.children():
            child.destroy()
        scatterSubnet.setPosition(oldScatterSubnetPos)
        scatterSubnet.setName(oldScatterSubnetName)

        # Rewire scatterSubnet
        if scatterMergeNodes:
            for i in range(len(scatterMergeNodes)):
                inputIndex = scatterConnectionIndicies[i]
                scatterMergeNodes[i].setInput(inputIndex, scatterSubnet)

        # Action message
        action = "Updated"
    else:
        # Create new tree scatter subnet
        scatterSubnet = hfGeoNode.createNode("subnet", treeScatterSubnetName)
        group = scatterSubnet.parmTemplateGroup()
        treeScaleTemplate = hou.FloatParmTemplate("treeScale", ("Tree Scale"), 1, default_value=([1]), min=0, max=6)
        group.append(treeScaleTemplate)
        weightTemplate = hou.FloatParmTemplate("weight", ("Weight"), 1, default_value=([1]), min=0, max=1)
        group.append(weightTemplate)
        scatterSubnet.setParmTemplateGroup(group)
        # Action message
        action = "Created"

    scatterSubnetNet = cnn.MyNetwork(scatterSubnet)

    # Create merge, xform, attribcreate, and output
    nodePrefix1 = treeSubnetNet.name + "_"  # Can be string or None
    nodePrefix1 = str(nodePrefix1 or "")
    newNodesGroup1 = scatterSubnetNet.addNodes("merge", "xform", "attribcreate::2.0", "output", prefix=nodePrefix1)
    mergeNode = findNodeInList(newNodesGroup1, "merge")
    attribCreateNode = findNodeInList(newNodesGroup1, "attribcreate::2.0")
    attribCreateNode.setParms({"name1": "weight", "class1": 1, "value1v1": 1})
    outputNode =findNodeInList(newNodesGroup1, "output")
    # Wires new nodes group 1 in the order of the list
    scatterSubnetNet.wireNodes(newNodesGroup1)

    # Create object_merge and matchsize
    i = 0
    newNodesGroup2 = []
    for child in treeSubnetNet.children:
        # Bypass material networks
        if child.type().name() == "matnet" or child.type().name() == "shopnet":
            continue

        nodePrefix2 = child.name() + "_"
        newNodesGroup2Temp = scatterSubnetNet.addNodes("object_merge", "matchsize", prefix=nodePrefix2)
        # Store all new nodes to newNodesGroup2
        for newNodeGroup2Temp in newNodesGroup2Temp:
            newNodesGroup2.append(newNodeGroup2Temp)

        objMergeNode = findNodeInList(newNodesGroup2Temp, "object_merge")
        objMergeNode.setParms({"objpath1":"/obj/{TREESUBNETNAME}/{CHILDNAME}".format(TREESUBNETNAME=treeSubnetNet.name,
                                                                                     CHILDNAME=child.name())})
        matchsizeNode = findNodeInList(newNodesGroup2Temp, "matchsize")
        matchsizeNode.setParms({"justify_y":1})
        matchsizeNode.setParms({"doscale":1})
        matchsizeNode.setParms({"uniformscale": 1})
        matchsizeNode.setParms({"scale_axis": 0})
        mergeNode.setInput(i, matchsizeNode)
        # Wires new nodes group 2 temp in the order of the list
        scatterSubnetNet.wireNodes(newNodesGroup2Temp)
        i += 1

    # Set relative references
    xformNode = scatterSubnetNet.findNodes("xform", method="type")[0]
    xformScale = xformNode.parm("scale")
    xformScale.setExpression("ch(\"../treeScale\")")
    attrWeightNode = scatterSubnetNet.findNodes("attribcreate::2.0", method="type")[0]
    attrWeightParm = attrWeightNode.parm("value1v1")
    attrWeightParm.setExpression("ch(\"../weight\")")

    # Set flags
    outputNode.setRenderFlag(True)
    outputNode.setDisplayFlag(True)

    # Layout Children
    scatterSubnet.layoutChildren()

    # Action Message
    actionMessage = "{ACTION} Scatter Subnet: {SCATTERSUBNETNAME}".format(ACTION=action,
                                                                          SCATTERSUBNETNAME=treeScatterSubnetName)

    return scatterSubnet, actionMessage

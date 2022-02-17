"""
API for creating tree scatter subnet
"""

import hou
import os
from . import classNodeNetwork as cnn
from collections import defaultdict


def createTreeScatterSubnet(subnet, hfGeoNode):
    """ Create Subnet used for scattering in hf_scatter SOP"""
    treeSubnet = cnn.MyNetwork(subnet)
    hfGeoNodeNet = cnn.MyNetwork(hfGeoNode)

    treeScatterSubnetName = treeSubnet.name + "_scatter"

    # Create tree scatter subnet
    oldScatterSubnetList = hfGeoNodeNet.findNodes(treeScatterSubnetName, method="name")
    if oldScatterSubnetList:
        oldScatterSubnet = oldScatterSubnetList[0]
        # Store old position and name
        oldScatterSubnetPos = oldScatterSubnet.position()
        oldScatterSubnetName = oldScatterSubnet.name()
        # Copy old scatter subnet and delete contents
        scatterSubnet = oldScatterSubnet.copyTo(oldScatterSubnet.parent())
        oldScatterSubnet.destroy()
        for child in scatterSubnet.children():
            child.destroy()
        scatterSubnet.setPosition(oldScatterSubnetPos)
        scatterSubnet.setName(oldScatterSubnetName)
    else:
        # Create new tree scatter subnet
        scatterSubnet = hfGeoNode.createNode("subnet", treeScatterSubnetName)
        group = scatterSubnet.parmTemplateGroup()
        treeScaleTemplate = hou.FloatParmTemplate("treeScale", ("Tree Scale"), 1, default_value=([1]), min=0, max=6)
        group.append(treeScaleTemplate)
        weightTemplate = hou.FloatParmTemplate("weight", ("Weight"), 1, default_value=([1]), min=0, max=1)
        group.append(weightTemplate)
        scatterSubnet.setParmTemplateGroup(group)
    scatterSubnetNet = cnn.MyNetwork(scatterSubnet)

    # Create merge, xform, attribcreate, and output
    nodePrefix1 = treeSubnet.name + "_"  # Can be string or None
    nodePrefix1 = str(nodePrefix1 or "")
    newNodesGroup1 = scatterSubnetNet.addNodes("merge", "xform", "attribcreate::2.0", "output", prefix=nodePrefix1)
    mergeNode = [node for node in newNodesGroup1 if node.type().name() == "merge"][0]
    attribCreateNode = [node for node in newNodesGroup1 if node.type().name() == "attribcreate::2.0"][0]
    attribCreateNode.setParms({"name1": "weight", "class1": 1, "value1v1": 1})
    scatterSubnetNet.wireNodes(newNodesGroup1)

    # Create object_merge and matchsize
    i = 0
    newNodesGroup2 = []
    for child in treeSubnet.children:
        # Bypass material networks
        if child.type().name() == "matnet" or child.type().name() == "shopnet":
            continue

        nodePrefix2 = child.name() + "_"
        newNodesGroup2Temp = scatterSubnetNet.addNodes("object_merge", "matchsize", prefix=nodePrefix2)
        for newNodeGroup2Temp in newNodesGroup2Temp:
            newNodesGroup2.append(newNodeGroup2Temp)
        objMergeNode = [node for node in newNodesGroup2Temp if node.type().name() == "object_merge"][0]
        objMergeNode.setParms({"objpath1":"/obj/{TREESUBNETNAME}/{CHILDNAME}".format(TREESUBNETNAME=treeSubnet.name,
                                                                                     CHILDNAME=child.name())})
        matchsizeNode = [node for node in newNodesGroup2Temp if node.type().name() == "matchsize"][0]
        matchsizeNode.setParms({"justify_y":1})
        matchsizeNode.setParms({"doscale":1})
        matchsizeNode.setParms({"uniformscale": 1})
        matchsizeNode.setParms({"scale_axis": 0})
        mergeNode.setInput(i, matchsizeNode)
        scatterSubnetNet.wireNodes(newNodesGroup2Temp)
        i += 1

    # Set relative references
    xformNode = scatterSubnetNet.findNodes("xform", method="type")[0]
    xformScale = xformNode.parm("scale")
    xformScale.setExpression("ch(\"../treeScale\")")
    attrWeightNode = scatterSubnetNet.findNodes("attribcreate::2.0", method="type")[0]
    attrWeightParm = attrWeightNode.parm("value1v1")
    attrWeightParm.setExpression("ch(\"../weight\")")

    # Layout Children
    scatterSubnet.layoutChildren()

def exe():
    subnet = hou.node("/obj/BostonFern")
    hfGeoNode = hou.node("/obj/hf_scatter_example")

    createTreeScatterSubnet(subnet, hfGeoNode)
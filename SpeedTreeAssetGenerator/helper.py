"""
Helper functions
"""
import hou


def getNetworkBox(treeSubnet, parentNode):
    """
    Gets network box that contains the node with the given name in obj context.
    :param treeName: Tree subnet name
    :return: hou.NetworkBox that contains the tree subnet with the name
    """

    # Find all network boxes in obj context
    objNetworkBoxes = parentNode.networkBoxes()

    # Find network box that the node is in
    foundNetworkBox = None
    for networkBox in objNetworkBoxes:
        nodeNames = [node.name() for node in networkBox.nodes(recurse=False)]
        if treeSubnet.name() in nodeNames:
            foundNetworkBox = 1
            break
        else:
            foundNetworkBox = 0

    if foundNetworkBox:
        return networkBox


def createNetworkBox(comment):
    """
    Create network box in obj context
    :param comment: comment in network box
    :return: hou.NetworkBox object
    """
    obj = hou.node("/obj")

    newNetworkBox = obj.createNetworkBox()
    newNetworkBox.setComment(comment)

    return newNetworkBox


def hideParms(nodeToHideParms, parmNamesList):

    parms = nodeToHideParms.parmTemplateGroup()
    for parmName in parmNamesList:
        p = parms.find(parmName)
        p.hide(True)
        parms.replace(parmName, p)
    nodeToHideParms.setParmTemplateGroup(parms)

    return nodeToHideParms



"""
Class definition for node and network
"""
import hou

class MyNetwork:

    def __init__(self, nodeNetwork):
        self.network = nodeNetwork
        self.name = nodeNetwork.name()

    @property
    def children(self):
        return self.network.children()

    def getChildKeys(self, method):
        """ Returns list(string) of names or types of network children
        This is used along with childIndexMatch method """
        if method == "name":
            childKeys = [child.name() for child in self.children]
        elif method == "type":
            childKeys = [child.type().name() for child in self.children]
        return childKeys

    def childMatchSearch(self, keyStringList, method):
        """ Returns a list of indices that matches inside of self.children
        This is used along with getChildKeys method """
        childKeys = self.getChildKeys(method=method)
        index = 0
        matchedChildNodes = []
        for childKey in childKeys:
            if method == "type":
                matchedChildNodes.append(self.children[index]) if childKey in keyStringList else matchedChildNodes
            if method == "name":
                isKeyStringInChild = any(elem in childKey for elem in keyStringList)
                matchedChildNodes.append(self.children[index]) if isKeyStringInChild else matchedChildNodes
            index += 1
        return matchedChildNodes

    def findNodes(self, *keyStrings, **kwargs):
        """ Returns list of hou.node objects by method based on matching keyStrings """
        method = kwargs.get("method", "type")
        matchedChildNodes = self.childMatchSearch(keyStrings, method)
        return matchedChildNodes

    def cleanNetwork(self, *keyStrings, **kwargs):
        """ Deletes children nodes by method based on matching keyStrings """
        method = kwargs.get("method", "type")
        matchedChildNodes = self.childMatchSearch(keyStrings, method)
        for childNode in matchedChildNodes:
            childNode.destroy()

    def addNodes(self, *nodeTypes, **kwargs):
        """ Creates new nodes in network of type [nodeTypes] in the order of the list.
        Node name has optional prefix. Returns list of hou.node objs """
        prefix = kwargs.get("prefix", None)
        newNodes = []
        for nodeType in nodeTypes:
            nodeTypeAlnum = ""
            for char in nodeType:
                if char.isalnum() or char == "_":
                    nodeTypeAlnum += char
            nodeName = prefix+nodeTypeAlnum if prefix else None
            newNodes.append(self.network.createNode(nodeType, nodeName))
        return newNodes

    def findLastNode(self):
        """ Returns the hou.node obj that is the last node in the chain """
        lastNode = None
        for child in self.children:
            if not child.outputs():
                lastNode = child
        return lastNode

    def wireNodes(self, nodeOrderedList, lastNode=None):
        """ Wires the given list of hou.node objects based on order of the list """
        if lastNode:
            nodeOrderedList[0].setInput(0, lastNode)
        for index in range(len(nodeOrderedList)-1):
            nodeBottom = nodeOrderedList[index+1]
            nodeTop = nodeOrderedList[index]
            nodeBottom.setInput(0, nodeTop)

    def extractChildren(self):
        """ Moves nodes from inside network to where the network is living """
        networkChildren = []
        for child in self.children:
            networkChildren.append(hou.moveNodesTo((child,), self.network.parent())[0])
        return networkChildren

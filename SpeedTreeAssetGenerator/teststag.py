"""
test python file
"""

import hou
from . import helper
from . import execute

def myFunc():
    obj = hou.node("/obj")
    objNetworkBoxes = obj.networkBoxes()

    treeName = "BostonFern"

    box = helper.getNetworkBox(treeName)
    print(box.comment() if box else "No network box found")


def exe1():
    # Get hip directory path
    hipPath = hou.hipFile.path()
    hipBaseName = hou.hipFile.basename()
    hipDir = hipPath.replace(hipBaseName, "")
    directory = "{HIPDIR}assets/myTrees/stagTest".format(HIPDIR=hipDir)

    generatedTreeSubnets = execute.generateTreeSubnets(directory)

    generatedTreeSubnetNames = [generatedTreeSubnet.name() for generatedTreeSubnet in generatedTreeSubnets]

    print("\nTree Subnets {NAME} is generated in obj".format(NAME=generatedTreeSubnetNames))

def exe2():
    treeSubnet = hou.node("/obj/BostonFern")
    hfGeoNode = hou.node("/obj/hf_scatter_example")

    execute.generateScatterSubnets(treeSubnet, hfGeoNode)

if __name__ == "__main__":
    myFunc()



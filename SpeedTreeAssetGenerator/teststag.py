"""
test python file
"""

import hou
from . import helper
from . import execute

def myFunc():
    # Get hip directory path
    hipPath = hou.hipFile.path()
    hipBaseName = hou.hipFile.basename()
    hipDir = hipPath.replace(hipBaseName, "")
    directory = "{HIPDIR}assets/myTrees/stagTest".format(HIPDIR=hipDir)

    generatedTreeSubnets = execute.treeSubnetsFromDir(directory)


def exe1():
    # Get hip directory path
    hipPath = hou.hipFile.path()
    hipBaseName = hou.hipFile.basename()
    hipDir = hipPath.replace(hipBaseName, "")
    directory = "{HIPDIR}assets/myTrees/stagTest".format(HIPDIR=hipDir)

    generatedTreeSubnets = execute.treeSubnetsFromDir(directory)

    treeSubnetsReformatted = execute.treeSubnetsReformat(generatedTreeSubnets)

    generatedTreeSubnetNames = [generatedTreeSubnet.name() for generatedTreeSubnet in generatedTreeSubnets]

    print("\nTree Subnets {NAME} is generated in obj".format(NAME=generatedTreeSubnetNames))


def exe2():
    """ Select tree subnets or scatter subnets """
    treeSubnets = hou.selectedNodes()
    hfGeoNode = hou.node("/obj/hf_scatter_example")

    for treeSubnet in treeSubnets:
        execute.generateScatterSubnets(treeSubnet, hfGeoNode)


def exe3():
    """ Select tree subnets """
    rsFolder = "Z:/Work/Houdini 1/environmentScene/assets/rsProxy"
    treeSubnets = hou.selectedNodes()
    execute.generateRedshiftProxy(treeSubnets, rsFolder)


if __name__ == "__main__":
    myFunc()


# SpeedTree Fbx Importer
This tool imports assets generated from SpeedTree into Houdini. Imported assets will be contained within subnets along with Redshift materials and material assignments.

## Table of contents
* [General Info](#general-info)
* [Requirements](#requirements)
* [Exporting From SpeedTree](#exporting-from-speedtree)
* [Setup](#setup)
* [Notes](#notes)
* [Task List](#task-list)

## General Info
The importer will import subnets with this structure into the Houdini scene:
```
/obj                        # obj context
├── AppleTree               # Subnet Generated by SpeedTreeFbxImporter
│   ├── AppleTree_1         # Geometry
│   ├── AppleTree_2         # Geometry
│   ├── AppleTree_3         # Geometry
│   └── AppleTree_matnet    # Material Network
```
## Requirements
* Houdini 19.0 or above
* Redshift in Houdini
* Some setup (see Setup)
## Exporting From SpeedTree
> Export SpeedTree generated models using the Export Mesh tool in SpeedTree. Ensure that *Group By* is set to *Hierachy* and hit *OK*.  
> ***Do not export the generated model using the Export to Game tool.***

![This is an image](images/speedTreeExportMeshLocation.png)   ![This is an image](images/speedTreeExportMesh.png)

## Setup
### Folder Setup
> To run this project, each set of SpeedTree generated models must live in the same directory. The example folder below, when imported using the tool, will create a subnet with 3 geometry nodes, each representing a fbx model:
```
AppleTree                     # Example of AppleTree Folder
├── AppleTree_var1.fbx        # fbx file
├── AppleTree_var2.fbx        # fbx file
├── AppleTree_var3.fbx        # fbx file
├── Bark.png                  # Texture
└── Leaf.png                  # Texture
``` 
![This is an image](images/AppleTreeExample.png)
> Example of a folder structure. Folders may contain any number of subdirectories:
```
FolderWithAllMyTrees          # Folder
├── FruitTrees                # Folder
│   │   Berries               # Folder
│   │   └── Strawberry        # Folder with SpeedTree assets
|   |
│   ├── AppleTree             # Folder with SpeedTree assets
│   ├── BananaPlant           # Folder with SpeedTree assets
│   └── CherryTree            # Folder with SpeedTree assets
| 
├── AfricanTrees              # Folder
│   ├── Acacia                # Folder with SpeedTree assets
│   └── Baobab                # Folder with SpeedTree assets
|
├── Oak                       # Folder with SpeedTree assets
└── MapleTree                 # Folder with SpeedTree assets
```
### Script Location
> Add **SpeedTreeAssetGenerator** folder $HOUDINI_USER_PREF_DIR/python3.7libs . See [python locations](https://www.sidefx.com/docs/houdini/hom/locations.html) for docs on Python script locations.  
> For Gnomon, place **SpeedTreeAssetGenerator** folder in Z:/houdini19.0/python3.7libs . Create the folder if it does not exist.  
> 
> Add all contents of **python_panels** folder to python_panels directory. See [python panel](https://www.sidefx.com/docs/houdini/ref/windows/pythonpaneleditor.html) for docs on Python Panel Editor.  
> For Gnomon, place all contents of **python_panels** folder in Z:/houdini19.0/python_panels . Create the folder if it does not exist.  
### Houdini Setup
> This tool is accessed through a dockable Python Panel in a Houdini session.

1. Add a python panel.

![This is an image](images/pythonPanelLocation.png)

2. Select SpeedTree Fbx Importer by Daniel in the drop down menu. If the selection is missing, restart Houdini.

![This is an image](images/pythonPanelDropDown.png)
## Notes
- SpeedTree fbxs automatically assigns primitive groups according to material.  
- *Do not change name of the group nodes and group names. Do not change the name of texture files. If materials are not rendering, consider reimporting.*  
- *After running the Importer in Houdini, if the number of geos do not match the number of FBXs on disk. You may have exported SpeedTree generated models using the Export to Game tool. Re-export from SpeedTree using Export Mesh tool and reimport in Houdini.*
## Task List
- [ ] Make compatible with assets other than fbx
- [ ] Make compatible with versions before Houdini 19.0
- [ ] Support textures other than png

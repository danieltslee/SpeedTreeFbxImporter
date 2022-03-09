# SpeedTree Fbx Importer
This tool imports assets generated from SpeedTree into Houdini. Imported assets will be contained within subnets along with Redshift materials and material assignments.

## Table of contents
* [General info](#general-info)
* [Requirements](#requirements)
* [Setup](#setup)

## General info
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
	
## Setup
### Folder Setup
> To run this project, each set of SpeedTree assets must live in the same directory:
```
AppleTree                     # Example of AppleTree Folder
├── AppleTree_var1.fbx        # fbx file
├── AppleTree_var1.fbx        # fbx file
├── AppleTree_var1.fbx        # fbx file
├── Bark.png                  # fbx file
└── Leaf.png                  # Textures
```
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
> Place SpeedTreeAssetGenerator folder in `$HOUDINI_USER_PREF_DIR`/python3.7libs . Create the folder if missing.  
> For Gnomon, place SpeedTreeAssetGenerator folder in Z:/houdini19.0/python3.7libs
### Houdini Setup
> This tool is accessed through a dockable Python Panel in a Houdini session.

1. Add a python panel.

![This is an image](SpeedTreeAssetGenerator/pythonPanelLocation.png)

2. Select SpeedTree Fbx Importer by Daniel in the drop down menu.

![This is an image](SpeedTreeAssetGenerator/pythonPanelDropDown.png)



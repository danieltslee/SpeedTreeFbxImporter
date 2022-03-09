# SpeedTreeFbxImporter
This tool imports assets generated from SpeedTree into Houdini. Imported assets will be contained within subnets along with Redshift materials and material assignments.

## Table of contents
* [General info](#general-info)
* [Requirements](#requirements)
* [Setup](#setup)

## General info

```
.
├── ...
├── test                    # Test files (alternatively `spec` or `tests`)
│   ├── benchmarks          # Load and stress tests
│   ├── integration         # End-to-end, integration tests (alternatively `e2e`)
│   └── unit                # Unit tests
└── ...
```
## Requirements
* Houdini 19.0 or above
* Redshift in Houdini
* Some setup (see Setup)
	
## Setup
To run this project, install it locally using npm:

```
$ cd ../lorem
$ npm install
$ npm start

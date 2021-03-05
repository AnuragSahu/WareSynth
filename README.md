 # WarehouseGen

 A procedural synthetic  data  generation pipeline  that  can  be  used  to  generate  3D  warehouse  scenes and  automate  the  process  of  data  capture  and  generating corresponding  annotation.

![Alt Text](./tes.gif)

## Repo setup
The repository is has to be setup we need to have blender get the objects asscets.

## Utility
* In order to generate the warehouse along with the front and top layouts:
```
bash genrateDataset
```

* If you want to also Generate Kitti, goto Constants files and make the GENERATE_KITTI flag true and then run the script
```
gedit scripts/pillared_warehouse/Constants.py
GENERATE_KITTI = True
bash genrateDataset
```

* The number of images and other configs of the warehouse can be altered by changing variables in the bottom-most for loop.

## Setup
The scripts here need blender to run, and you need to have the files set up as:
```bash
├── Project Directory
│   ├── Blender
│   │   ├── blender (executable)
│   ├── WarehouseGen (This repo)
│   │   ├── src
│   │   ├── objects
|   |   |   ├── primitives
```
